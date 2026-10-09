"""Documentation fixture validator only; no product rules or network collection."""
import re

STATUSES = {'pass', 'fail', 'unknown', 'not_applicable', 'not_run'}


def validate_fixture(data, expected_ids):
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported fixture version')
    if data.get('synthetic') is not True or data.get('scope') != 'lab.example.test':
        raise ValueError('Only explicitly synthetic lab fixture is permitted')
    checks = data.get('checks')
    if not isinstance(checks, list):
        raise ValueError('Missing checks')
    ids = []
    for check in checks:
        check_id = check.get('check_id')
        if not isinstance(check_id, str) or not re.fullmatch(r'[A-Z0-9]+-\d{2}', check_id):
            raise ValueError('Invalid check ID')
        ids.append(check_id)
        status = check.get('status')
        if status not in STATUSES:
            raise ValueError('Invalid status')
        evidence = check.get('evidence_refs')
        if not isinstance(evidence, list) or any(not isinstance(e, str) or not e.strip() for e in evidence):
            raise ValueError('Invalid evidence references')
        if status in {'pass', 'fail'} and not evidence:
            raise ValueError('A result requires evidence')
        if status in {'unknown', 'not_applicable', 'not_run'}:
            if not isinstance(check.get('reason'), str) or not check['reason'].strip():
                raise ValueError('An incomplete or excluded check requires a reason')
        # This fixture describes current readiness, not simulated AD findings.
        if status != 'not_run' or evidence:
            raise ValueError('Current Windows readiness must remain not_run without evidence')
    if len(set(ids)) != len(ids) or set(ids) != set(expected_ids):
        raise ValueError('Duplicate IDs or incomplete coverage')
