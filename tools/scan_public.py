"""Conservative public-file guard; supplements, never replaces, manual review."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).split(b'\0')
patterns = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=]{32,}'),
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'),
    re.compile(rb'AKIA[0-9A-Z]{16}'),
]
prohibited_suffixes = {'.pfx', '.p12', '.key', '.evtx', '.kirbi', '.dmp'}
count = 0
for encoded in sorted(set(paths)):
    if not encoded:
        continue
    path = ROOT / encoded.decode()
    if not path.is_file():
        continue
    count += 1
    if path.suffix.lower() in prohibited_suffixes:
        raise SystemExit(f'Prohibited public artifact: {path.relative_to(ROOT)}')
    raw = path.read_bytes()
    if any(pattern.search(raw) for pattern in patterns):
        raise SystemExit(f'Possible credential material in {path.relative_to(ROOT)}; contents withheld')
    if path.suffix == '.json' and ('examples' in path.parts or 'fixtures' in path.parts):
        data = json.loads(raw)
        if data.get('synthetic') is not True or data.get('scope') != 'lab.example.test':
            raise SystemExit(f'Public fixture must be explicitly synthetic: {path.relative_to(ROOT)}')
print(f'Проверка публичных файлов пройдена: {count} файлов; ручная проверка происхождения остаётся обязательной')
