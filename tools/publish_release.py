"""Publish ONLY the existing prerelease from a manually dispatched Actions job.

No release creation, tag mutation, credentials configuration or asset overwrite.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

REPO = 'mejustbox-byte/ad-opsec-auditor'
TAG = 'v0.1.0a1'
COMMIT = '63579e76a7766c06dfc4626da683ad2db782d607'
RELEASE_ID = 407852541
NAMES = {'ad_opsec_auditor-0.1.0a1-py3-none-any.whl',
         'ad_opsec_auditor-0.1.0a1.tar.gz', 'ad-opsec-auditor-0.1.0a1.pyz'}


class PublishError(ValueError):
    pass


def gh(args, payload=None):
    result = subprocess.run(['gh', *args], input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        # Do not echo transport errors: they can contain temporary signed URLs.
        raise PublishError('GitHub operation failed; no credentials or signed URLs are printed')
    return result.stdout


def api(endpoint, payload=None):
    args = ['api', endpoint]
    if payload is not None:
        args += ['--method', 'PATCH', '--input', '-']
    return json.loads(gh(args, payload))


def artifacts(directory):
    directory = Path(directory)
    if {p.name for p in directory.iterdir()} != NAMES | {'SHA256SUMS'}:
        raise PublishError('Artifact set must be exactly the four approved files')
    for name in NAMES | {'SHA256SUMS'}:
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 256 * 1024 * 1024:
            raise PublishError('Unsafe or oversized artifact')
    digests = {}
    for line in (directory / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9_.-]+)', line)
        if not match or match[2] not in NAMES or match[2] in digests:
            raise PublishError('Invalid or duplicate checksum entry')
        digests[match[2]] = match[1]
    if set(digests) != NAMES:
        raise PublishError('Incomplete checksum manifest')
    for name, digest in digests.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise PublishError('Local artifact checksum mismatch')
    digests['SHA256SUMS'] = hashlib.sha256((directory / 'SHA256SUMS').read_bytes()).hexdigest()
    return digests


def verify_release(release, digests, complete=False, published=False):
    if release.get('id') != RELEASE_ID or release.get('tag_name') != TAG or release.get('prerelease') is not True:
        raise PublishError('Existing release identity or prerelease flag does not match')
    if type(release.get('draft')) is not bool or (published and release['draft']):
        raise PublishError('Release publication state does not match')
    seen = set()
    for asset in release.get('assets', []):
        name = asset.get('name')
        if name not in digests or name in seen or asset.get('state') != 'uploaded':
            raise PublishError('Unexpected, duplicate or incomplete release asset')
        seen.add(name)
        if asset.get('digest') is not None and asset['digest'] != 'sha256:' + digests[name]:
            raise PublishError('Remote asset digest does not match verified build')
    if complete and seen != set(digests):
        raise PublishError('Release assets are incomplete')
    return seen


def verify_tag():
    reference = api(f'repos/{REPO}/git/ref/tags/{TAG}')['object']
    if reference['type'] == 'tag':
        reference = api(f'repos/{REPO}/git/tags/{reference["sha"]}')['object']
    if reference['type'] != 'commit' or reference['sha'] != COMMIT:
        raise PublishError('Tag moved or does not identify the audited commit')


def verify_downloads(digests):
    with tempfile.TemporaryDirectory() as directory:
        for name in sorted(digests):
            gh(['release', 'download', TAG, '--repo', REPO, '--pattern', name, '--dir', directory])
            downloaded = Path(directory) / name
            if not downloaded.is_file() or hashlib.sha256(downloaded.read_bytes()).hexdigest() != digests[name]:
                raise PublishError('Downloaded asset checksum mismatch')


def publish(directory):
    digests = artifacts(directory)
    verify_tag()
    endpoint = f'repos/{REPO}/releases/{RELEASE_ID}'
    release = api(endpoint)
    present = verify_release(release, digests)
    if not release['draft']:
        verify_release(release, digests, complete=True, published=True)
        verify_downloads(digests)
        print('Existing public prerelease and all four downloaded checksums verified')
        return
    for name in sorted(set(digests) - present):
        gh(['release', 'upload', TAG, str(Path(directory) / name), '--repo', REPO])
    verify_release(api(endpoint), digests, complete=True)
    verify_downloads(digests)
    # Final tag guard immediately before publication; never recreate/move the tag.
    verify_tag()
    published = api(endpoint, {'draft': False, 'prerelease': True})
    verify_release(published, digests, complete=True, published=True)
    verify_release(api(endpoint), digests, complete=True, published=True)
    verify_downloads(digests)
    print(f'Published https://github.com/{REPO}/releases/tag/{TAG}; all four assets and downloads verified')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', required=True)
    args = parser.parse_args()
    if (os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != REPO
            or os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch'
            or os.environ.get('GITHUB_REF') != 'refs/heads/main'):
        raise SystemExit('Publication must run in the authorized manually dispatched main Actions job')
    try:
        publish(args.dist)
    except (PublishError, OSError, KeyError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        raise SystemExit('Release verification/publication failed: ' + type(exc).__name__) from None


if __name__ == '__main__':
    main()
