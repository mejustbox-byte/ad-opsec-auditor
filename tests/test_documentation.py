import copy
import json
from pathlib import Path
import re
import unittest

from tools.check_contracts import validate_fixture

ROOT = Path(__file__).resolve().parents[1]
IDS = {'T0-01', 'CS-01', 'ACL-01', 'SVC-01', 'NTLM-01', 'LDAP-01', 'SMB-01', 'LOG-01', 'REC-01'}


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'tests/fixtures/readiness.synthetic.json').read_text(encoding='utf-8'))

    def test_required_documents_and_traceability(self):
        for path in ['requirements.md', 'threat-model.md', 'architecture.md', 'check-matrix.md', 'lab.md', 'development.md', 'adr/0001-stack.md']:
            self.assertTrue((ROOT / 'docs' / path).is_file(), path)
        requirements = (ROOT / 'docs/requirements.md').read_text(encoding='utf-8')
        threats = (ROOT / 'docs/threat-model.md').read_text(encoding='utf-8')
        matrix = (ROOT / 'docs/check-matrix.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| ([A-Z0-9]+-\d{2}) \| (FR-\d{2}) \| (TM-\d{2}) \|.*$', matrix, re.M)
        self.assertEqual({row[0] for row in rows}, IDS)
        self.assertEqual(len(rows), len(IDS))
        for check, requirement, threat in rows:
            self.assertIn(requirement, requirements, check)
            self.assertIn(threat, threats, check)
        for number in range(1, 13):
            self.assertIn(f'FR-{number:02}', requirements)

    def test_local_markdown_links(self):
        documents = [*sorted(ROOT.glob('*.md')), *sorted((ROOT / 'docs').rglob('*.md')), *sorted((ROOT / '.github').rglob('*.md'))]
        count = 0
        for doc in documents:
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                count += 1
                resolved = (doc.parent / target.split('#')[0]).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT), str(resolved))
                self.assertTrue(resolved.is_file(), f'{doc}: {target}')
        self.assertGreater(count, 5)

    def test_synthetic_readiness_contract(self):
        validate_fixture(self.data, IDS)

    def test_rejects_missing_or_duplicate_check(self):
        missing = copy.deepcopy(self.data)
        missing['checks'].pop()
        duplicate = copy.deepcopy(self.data)
        duplicate['checks'].append(duplicate['checks'][0])
        for data in [missing, duplicate]:
            with self.assertRaises(ValueError):
                validate_fixture(data, IDS)

    def test_rejects_false_readiness_and_missing_reason(self):
        for patch in [{'status': 'pass'}, {'status': 'pass', 'evidence_refs': ['fake']}, {'reason': ''}, {'status': 'skipped'}]:
            data = copy.deepcopy(self.data)
            data['checks'][0].update(patch)
            with self.assertRaises(ValueError):
                validate_fixture(data, IDS)

    def test_rejects_non_synthetic_scope_and_version(self):
        for patch in [{'synthetic': False}, {'scope': 'production.example.com'}, {'schema_version': 2}, {'schema_version': True}]:
            data = copy.deepcopy(self.data)
            data.update(patch)
            with self.assertRaises(ValueError):
                validate_fixture(data, IDS)

    def test_fixture_has_no_obvious_secret_material(self):
        raw = (ROOT / 'tests/fixtures/readiness.synthetic.json').read_text(encoding='utf-8')
        self.assertNotRegex(raw, r'-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|"(?:password|token|secret|private_key)"\s*:')


if __name__ == '__main__':
    unittest.main()


class FullDocumentationTests(unittest.TestCase):
    def test_complete_root_index_and_mit_metadata(self):
        import tomllib
        expected = ['ARCHITECTURE.md', 'TECH-STACK.md', 'INSTALL.md', 'CONTRIBUTING.md',
                    'ROADMAP.md', 'SECURITY.md', 'CHANGELOG.md', 'THREAT-MODEL.md', 'CORE-CONTRACT.md',
                    'RUNBOOK.md', 'CLOUD-DEVELOPMENT.md', 'LOCAL-PC.md', 'VERIFICATION.md',
                    'RELEASE.md', 'RELEASE-CHECKLIST.md', 'RELEASE-NOTES.md', 'SUPPLY-CHAIN.md', 'LICENSE.ru.md', 'AGENTS.md']
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for name in expected:
            self.assertTrue((ROOT / name).is_file(), name)
            self.assertIn('](' + name + ')', readme, name)
        metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']
        self.assertEqual(metadata['license'], 'MIT')
        self.assertEqual(set(metadata['license-files']), {'LICENSE', 'LICENSE.ru.md'})
        license_text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
        self.assertIn('Permission is hereby granted, free of charge', license_text)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', license_text)
