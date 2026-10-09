"""Check the published schema against a reference Draft 2020-12 validator."""
from copy import deepcopy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ad_opsec_auditor.schema import snapshot_schema
from ad_opsec_auditor.validation import InputError, _validate

schema = snapshot_schema()
Draft202012Validator.check_schema(schema)
reference = Draft202012Validator(schema, format_checker=FormatChecker())
cases = []
for name in ['safe', 'risky', 'incomplete']:
    data = json.loads((ROOT / f'examples/{name}.synthetic.json').read_text())
    cases.append(data)
base = cases[0]


def paths(data, path=()):
    yield path
    if isinstance(data, dict):
        for key, child in data.items():
            yield from paths(child, (*path, key))
    elif isinstance(data, list):
        for index, child in enumerate(data):
            yield from paths(child, (*path, index))


for path in paths(base):
    for bad in [None, 1, True, -1, 1.5, '', [], {}, 'x' * 600]:
        changed = deepcopy(base)
        if not path:
            changed = bad
        else:
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = bad
        cases.append(changed)
for index, data in enumerate(cases):
    reference_valid = reference.is_valid(data)
    try:
        _validate(data, schema)
        actual_valid = True
    except InputError:
        actual_valid = False
    if reference_valid != actual_valid:
        raise AssertionError(f'Schema agreement failed for generated case {index}')
for file in [ROOT / 'schemas/snapshot-v1.schema.json', ROOT / 'ad_opsec_auditor/snapshot-v1.schema.json']:
    if json.loads(file.read_text()) != schema:
        raise AssertionError('Published schema is stale')
print(f'Reference schema agreement: {len(cases)} cases passed')
