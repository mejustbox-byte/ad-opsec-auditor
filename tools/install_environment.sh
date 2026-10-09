#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ad-opsec-auditor
python3 -c 'import sys; assert sys.version_info[:2] == (3, 12), "Требуется Python 3.12"'
python3 -m venv /workspace/.ad-opsec-auditor-dev
opsec_python=/workspace/.ad-opsec-auditor-dev/bin/python
"$opsec_python" -m pip install --only-binary=:all: --require-hashes -r requirements-dev.lock
"$opsec_python" -m unittest discover -s tests -v
"$opsec_python" tools/check_schema.py
"$opsec_python" tools/scan_public.py
"$opsec_python" tools/build_release.py
"$opsec_python" tools/smoke_artifacts.py
"$opsec_python" tools/check_reproducible.py
"$opsec_python" -m pip install --no-index --no-deps --force-reinstall dist/ad_opsec_auditor-0.1.0a2-py3-none-any.whl
/workspace/.ad-opsec-auditor-dev/bin/ad-opsec-auditor validate examples/safe.synthetic.json
/workspace/.ad-opsec-auditor-dev/bin/ad-opsec-auditor audit examples/safe.synthetic.json --format json > /tmp/ad-opsec-auditor-setup-smoke.json
