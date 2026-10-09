from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from ad_opsec_auditor.report import make_report, json_report, markdown_report, audit_exit_code
from ad_opsec_auditor.schema import snapshot_schema
from ad_opsec_auditor.validation import InputError, MAX_BYTES, parse_snapshot, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]


def fixture(name='safe'):
    return json.loads((ROOT / f'examples/{name}.synthetic.json').read_text(encoding='utf-8'))


def report(data):
    raw = json.dumps(data).encode()
    return make_report(parse_snapshot(raw), raw)


class RuleTests(unittest.TestCase):
    def test_safe_and_risky_each_rule(self):
        safe, risky = report(fixture()), report(fixture('risky'))
        self.assertEqual(safe['summary'], {'pass': 9, 'fail': 0, 'unknown': 0, 'not_run': 0})
        self.assertEqual(risky['summary']['fail'], 9)
        for result in risky['results']:
            with self.subTest(check=result['check_id']):
                self.assertTrue(result['evidence_refs'])
                self.assertTrue(result['violations'])
                self.assertTrue(result['remediation'])
                self.assertIn(result['severity'], {'critical', 'high', 'medium'})
                self.assertEqual(result['confidence'], 'medium')

    def test_missing_fact_each_rule_is_unknown(self):
        for check_id, observation in fixture()['observations'].items():
            for field in observation['facts']:
                with self.subTest(check=check_id, field=field):
                    data = fixture()
                    del data['observations'][check_id]['facts'][field]
                    actual = next(r for r in report(data)['results'] if r['check_id'] == check_id)
                    self.assertEqual(actual['status'], 'unknown')

    def test_missing_evidence_each_rule_is_unknown(self):
        for check_id in fixture()['observations']:
            with self.subTest(check=check_id):
                data = fixture()
                data['observations'][check_id]['evidence_refs'] = []
                actual = next(r for r in report(data)['results'] if r['check_id'] == check_id)
                self.assertEqual(actual['status'], 'unknown')

    def test_partial_coverage_each_rule_is_unknown_even_with_risk(self):
        for check_id in fixture()['observations']:
            with self.subTest(check=check_id):
                data = fixture('risky')
                data['observations'][check_id].update(coverage='partial', reason='Synthetic partial scope')
                actual = next(r for r in report(data)['results'] if r['check_id'] == check_id)
                self.assertEqual(actual['status'], 'unknown')

    def test_unrun_and_unavailable_are_distinct(self):
        actual = report(fixture('incomplete'))
        self.assertEqual(actual['summary']['unknown'], 8)
        self.assertEqual(actual['summary']['not_run'], 1)
        self.assertEqual(audit_exit_code(actual), 3)
        data = fixture()
        data['observations'] = {}
        self.assertEqual(report(data)['summary']['not_run'], 9)

    def test_adcs_requires_all_risk_conditions(self):
        for field in ('published', 'authentication', 'enrollee_supplies_subject', 'unprivileged_enrollment'):
            with self.subTest(field=field):
                data = fixture('risky')
                data['observations']['CS-01']['facts']['templates'][0][field] = False
                self.assertEqual(report(data)['results'][1]['status'], 'pass')
        for field, value in [('approval_required', True), ('authorized_signatures', 1)]:
            data = fixture('risky')
            data['observations']['CS-01']['facts']['templates'][0][field] = value
            self.assertEqual(report(data)['results'][1]['status'], 'pass')

    def test_ca_control_fails_independently_and_empty_inventory_unknown(self):
        data = fixture()
        facts = data['observations']['CS-01']['facts']
        facts['templates'] = []
        self.assertEqual(report(data)['results'][1]['status'], 'unknown')
        facts['unprivileged_ca_control'] = True
        self.assertEqual(report(data)['results'][1]['status'], 'fail')

    def test_unresolved_acl_is_not_pass(self):
        data = fixture()
        facts = data['observations']['ACL-01']['facts']
        facts['unresolved_aces'] = 1
        self.assertEqual(report(data)['results'][2]['status'], 'unknown')
        facts['unauthorized_control_edges'] = 1
        self.assertEqual(report(data)['results'][2]['status'], 'fail')

    def test_logging_and_recovery_thresholds(self):
        for check_id, field, pairs in [('LOG-01', 'retention_days', [(29, 'fail'), (30, 'pass'), (31, 'pass')]),
                                       ('REC-01', 'drill_age_days', [(179, 'pass'), (180, 'pass'), (181, 'fail')])]:
            for value, expected in pairs:
                with self.subTest(check=check_id, value=value):
                    data = fixture()
                    data['observations'][check_id]['facts'][field] = value
                    actual = next(r for r in report(data)['results'] if r['check_id'] == check_id)
                    self.assertEqual(actual['status'], expected)

    def test_each_baseline_predicate_can_fail(self):
        from ad_opsec_auditor.rules import RULES
        for rule in RULES:
            for field, operator, expected in rule.predicates:
                with self.subTest(check=rule.check_id, field=field):
                    data = fixture()
                    bad = (not expected) if type(expected) is bool else (expected - 1 if operator == 'ge' else expected + 1)
                    data['observations'][rule.check_id]['facts'][field] = bad
                    actual = next(r for r in report(data)['results'] if r['check_id'] == rule.check_id)
                    self.assertEqual(actual['status'], 'fail')

    def test_report_deterministic_and_input_immutable(self):
        data = fixture()
        before = deepcopy(data)
        first, second = report(data), report(data)
        self.assertEqual(json_report(first), json_report(second))
        self.assertEqual(data, before)
        self.assertEqual(first['input_sha256'], hashlib.sha256(json.dumps(data).encode()).hexdigest())
        self.assertEqual(audit_exit_code(first), 0)
        self.assertEqual(audit_exit_code(report(fixture('risky'))), 1)

    def test_markdown_does_not_render_input_markup(self):
        data = fixture()
        data['scope'] = '<script>alert(1)</script>[click](javascript:alert(1))|`*'
        rendered = markdown_report(report(data))
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('[click](', rendered)
        self.assertIn('\\|', rendered)

    def test_real_flag_never_claims_verified(self):
        data = fixture()
        data['synthetic'] = False
        actual = report(data)
        self.assertEqual(actual['provenance'], 'operator-supplied-unverified')
        self.assertIn('No live AD', actual['warning'])


class ValidationTests(unittest.TestCase):
    def reject(self, data):
        with self.assertRaises(InputError):
            parse_snapshot(json.dumps(data).encode())

    def test_schema_artifacts_match_source(self):
        expected = snapshot_schema()
        for path in ['schemas/snapshot-v1.schema.json', 'ad_opsec_auditor/snapshot-v1.schema.json']:
            self.assertEqual(json.loads((ROOT / path).read_text(encoding='utf-8')), expected)

    def test_required_top_level_and_unknown_keys(self):
        for field in fixture():
            data = fixture()
            del data[field]
            self.reject(data)
        for field in ['password', 'token', 'raw_export', 'rule_expression']:
            data = fixture()
            data[field] = 'DO_NOT_ECHO_SECRET'
            self.reject(data)

    def test_scalar_and_nested_types(self):
        for field, value in [('schema_version', True), ('synthetic', 1), ('scope', None), ('observations', []), ('evidence', {})]:
            data = fixture()
            data[field] = value
            self.reject(data)
        for value in [True, -1, 1000001, '1', 1.0, None]:
            data = fixture()
            data['observations']['T0-01']['facts']['unexpected_admin_paths'] = value
            self.reject(data)
        data = fixture()
        data['observations']['SMB-01']['facts']['smb1_enabled'] = 0
        self.reject(data)
        data = fixture()
        data['observations']['T0-01']['evidence_refs'] = [{}]
        self.reject(data)

    def test_evidence_references_and_time(self):
        for mutation in ['dangling', 'duplicate-id', 'duplicate-ref', 'future']:
            data = fixture()
            if mutation == 'dangling':
                data['observations']['T0-01']['evidence_refs'] = ['absent']
            elif mutation == 'duplicate-id':
                data['evidence'].append(data['evidence'][0])
            elif mutation == 'duplicate-ref':
                data['observations']['T0-01']['evidence_refs'] *= 2
            else:
                data['evidence'][0]['collected_at'] = '2026-10-10T00:00:00Z'
            self.reject(data)

    def test_invalid_timestamps(self):
        for timestamp in ['2026-02-30T00:00:00Z', '2026-10-09T00:00:00+00:00', '2026-10-09', '2026-10-09T24:00:00Z']:
            data = fixture()
            data['collected_at'] = timestamp
            self.reject(data)

    def test_unknown_check_and_bad_collection_states(self):
        data = fixture()
        data['observations']['NEW-01'] = {}
        self.reject(data)
        for patch in [{'state': 'pass'}, {'state': 'not_run'}, {'coverage': 'none'}, {'coverage': 'partial', 'reason': ''}]:
            data = fixture()
            data['observations']['T0-01'].update(patch)
            self.reject(data)
        data = fixture('incomplete')
        data['observations']['T0-01']['reason'] = ''
        self.reject(data)

    def test_template_contract(self):
        data = fixture()
        del data['observations']['CS-01']['facts']['templates'][0]['published']
        self.reject(data)
        data = fixture()
        data['observations']['CS-01']['facts']['templates'][0]['command'] = 'malicious'
        self.reject(data)

    def test_malformed_duplicate_nonfinite_unicode_and_depth(self):
        cases = [b'{', b'\xff', b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
                 b'[' * 17 + b']' * 17, b'1' * 5000]
        for raw in cases:
            with self.subTest(size=len(raw)):
                with self.assertRaises(InputError):
                    parse_snapshot(raw)
        data = fixture()
        data['scope'] = '\ud800'
        self.reject(data)

    def test_string_and_array_limits(self):
        for value in ['x' * 257, '', 'bad\nname', '\x1b[31m', '\x7f']:
            data = fixture()
            data['scope'] = value
            self.reject(data)
        data = fixture()
        data['evidence'] *= 56
        self.reject(data)
        with self.assertRaises(InputError):
            parse_snapshot(b' ' * (MAX_BYTES + 1))

    def test_brackets_in_strings_are_not_depth(self):
        data = fixture()
        data['scope'] = '[' * 200
        validate_snapshot(data)
        parse_snapshot(json.dumps(data).encode())
