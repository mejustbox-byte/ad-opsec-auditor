from copy import deepcopy
from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import publish_release as release


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(redirect_stdout(io.StringIO()))
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        for name in release.NAMES:
            (self.directory / name).write_bytes(('synthetic artifact ' + name).encode())
        manifest = ''.join(hashlib.sha256((self.directory / name).read_bytes()).hexdigest() + '  ' + name + '\n'
                           for name in sorted(release.NAMES))
        (self.directory / 'SHA256SUMS').write_text(manifest, encoding='utf-8')
        self.digests = release.artifacts(self.directory)
        self.metadata = {'id': release.RELEASE_ID, 'tag_name': release.TAG, 'draft': True, 'prerelease': True,
                         'assets': [{'name': n, 'state': 'uploaded', 'digest': 'sha256:' + digest}
                                    for n, digest in self.digests.items()]}

    def test_artifact_integrity_and_strict_manifest(self):
        (self.directory / sorted(release.NAMES)[0]).write_bytes(b'corrupted')
        with self.assertRaises(release.PublishError):
            release.artifacts(self.directory)
        (self.directory / 'SHA256SUMS').write_text('0' * 64 + '  ../secret\n', encoding='utf-8')
        with self.assertRaises(release.PublishError):
            release.artifacts(self.directory)

    def test_existing_release_identity_assets_and_checksums(self):
        release.verify_release(self.metadata, self.digests, complete=True)
        for change in [{'id': 1}, {'tag_name': 'wrong'}, {'prerelease': False}, {'assets': []}]:
            with self.subTest(change=change), self.assertRaises(release.PublishError):
                release.verify_release(self.metadata | change, self.digests, complete=True)
        for change in [{'digest': 'sha256:' + '0' * 64}, {'state': 'starter'}, {'name': 'unknown'}]:
            data = deepcopy(self.metadata)
            data['assets'][0].update(change)
            with self.assertRaises(release.PublishError):
                release.verify_release(data, self.digests, complete=True)

    def test_moved_tag_rejected(self):
        with patch.object(release, 'api', return_value={'object': {'type': 'commit', 'sha': 'wrong'}}):
            with self.assertRaises(release.PublishError):
                release.verify_tag()

    def test_download_failure_prevents_publication(self):
        with patch.object(release, 'verify_tag'), patch.object(release, 'api', return_value=self.metadata) as api:
            with patch.object(release, 'verify_downloads', side_effect=release.PublishError('mismatch')):
                with self.assertRaises(release.PublishError):
                    release.publish(self.directory)
            self.assertTrue(all(call.args == (f'repos/{release.REPO}/releases/{release.RELEASE_ID}',) for call in api.call_args_list))

    def test_only_existing_release_is_patched_after_verified_downloads(self):
        calls = []
        published = self.metadata | {'draft': False}
        def api(endpoint, payload=None):
            calls.append(('api', payload))
            return published if payload is not None or sum(c == ('api', None) for c in calls) >= 3 else self.metadata
        with patch.object(release, 'verify_tag', side_effect=lambda: calls.append(('tag', None))):
            with patch.object(release, 'api', side_effect=api), patch.object(release, 'gh') as gh:
                with patch.object(release, 'verify_downloads', side_effect=lambda d: calls.append(('download', None))):
                    release.publish(self.directory)
        self.assertFalse(gh.called, 'Existing assets must not be overwritten')
        write = calls.index(('api', {'draft': False, 'prerelease': True}))
        self.assertIn(('download', None), calls[:write])
        self.assertIn(('download', None), calls[write + 1:])
        self.assertEqual(len([c for c in calls if c[0] == 'api' and c[1] is not None]), 1)

    def test_published_release_is_verified_without_modification(self):
        with patch.object(release, 'verify_tag'), patch.object(release, 'api', return_value=self.metadata | {'draft': False}) as api:
            with patch.object(release, 'verify_downloads') as download, patch.object(release, 'gh') as gh:
                release.publish(self.directory)
        download.assert_called_once()
        self.assertEqual(api.call_count, 1)
        self.assertFalse(gh.called)

    def test_release_target_versions_and_immutable_commit_validation(self):
        with patch.object(release, 'TAG', release.TAG), patch.object(release, 'COMMIT', release.COMMIT):
            with patch.object(release, 'RELEASE_ID', release.RELEASE_ID), patch.object(release, 'NAMES', release.NAMES):
                release.configure_target('v0.1.0a2', 'a' * 40, 123)
                self.assertEqual(release.TAG, 'v0.1.0a2')
                self.assertIn('ad_opsec_auditor-0.1.0a2-py3-none-any.whl', release.NAMES)
                for tag, commit, identifier in [('other', 'a' * 40, 123), ('v0.1.0a2', 'short', 123), ('v0.1.0a2', 'a' * 40, 0)]:
                    with self.assertRaises(release.PublishError):
                        release.configure_target(tag, commit, identifier)
