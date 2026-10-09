"""Repeat the exact release build and compare artifact hashes."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
before = (ROOT / 'dist/SHA256SUMS').read_bytes()
subprocess.run([sys.executable, str(ROOT / 'tools/build_release.py')], check=True, stdout=subprocess.DEVNULL)
if (ROOT / 'dist/SHA256SUMS').read_bytes() != before:
    raise SystemExit('Repeated release build differs')
print('SHA256 повторных сборок wheel/исходного архива/zipapp совпали')
