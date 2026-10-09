"""Install wheel outside checkout; test zipapp and rebuild source archive."""
import hashlib
import email
import zipfile
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import venv

from release_common import normalize_wheel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ad_opsec_auditor import __version__

wheel = ROOT / f'dist/ad_opsec_auditor-{__version__}-py3-none-any.whl'
zipapp = ROOT / f'dist/ad-opsec-auditor-{__version__}.pyz'
source = ROOT / f'dist/ad_opsec_auditor-{__version__}.tar.gz'
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
    metadata = email.message_from_bytes(archive.read(next(n for n in names if n.endswith('/METADATA'))))
    assert metadata['License-Expression'] == 'MIT'
    for license_name in ['LICENSE', 'LICENSE.ru.md']:
        member = next(n for n in names if n.endswith('/licenses/' + license_name))
        assert archive.read(member) == (ROOT / license_name).read_bytes()
with zipfile.ZipFile(zipapp) as archive:
    for license_name in ['LICENSE', 'LICENSE.ru.md']:
        assert archive.read(license_name) == (ROOT / license_name).read_bytes()
with tarfile.open(source) as archive:
    for license_name in ['LICENSE', 'LICENSE.ru.md']:
        member = f'ad_opsec_auditor-{__version__}/' + license_name
        assert archive.extractfile(member).read() == (ROOT / license_name).read_bytes()

with tempfile.TemporaryDirectory() as directory:
    working = Path(directory)
    environment = working / 'env'
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    subprocess.run([str(python), '-m', 'pip', 'install', '--no-index', '--no-deps', str(wheel)], cwd=working, check=True)
    for command in [[str(python), '-m', 'ad_opsec_auditor'], [sys.executable, str(zipapp)]]:
        version = subprocess.run([*command, '--version'], cwd=working, capture_output=True, text=True, encoding='utf-8', check=True)
        assert version.stdout.strip() == __version__
        schema = subprocess.run([*command, 'schema'], cwd=working, capture_output=True, text=True, encoding='utf-8', check=True)
        assert json.loads(schema.stdout)['title'] == 'Нормализованный снимок AD OPSEC v1'
        for name, expected in [('safe', 0), ('risky', 1), ('incomplete', 3)]:
            for form in ['json', 'markdown']:
                result = subprocess.run([*command, 'audit', str(ROOT / f'examples/{name}.synthetic.json'), '--format', form],
                                        cwd=working, capture_output=True, text=True, encoding='utf-8', timeout=10)
                assert result.returncode == expected, result.stderr
                if form == 'json':
                    assert len(json.loads(result.stdout)['results']) == 9
                else:
                    assert 'Реальные AD' in result.stdout
    with tarfile.open(source) as archive:
        archive.extractall(working / 'source', filter='data')
    checkout = working / 'source' / f'ad_opsec_auditor-{__version__}'
    subprocess.run([sys.executable, '-m', 'build', '--wheel', '--no-isolation', '--outdir', str(working / 'rebuilt')], cwd=checkout,
                   env=__import__('os').environ | {'SOURCE_DATE_EPOCH': '1770000000'}, check=True,
                   stdout=subprocess.DEVNULL)
    rebuilt = working / 'rebuilt' / wheel.name
    normalize_wheel(rebuilt)
    assert hashlib.sha256(rebuilt.read_bytes()).digest() == hashlib.sha256(wheel.read_bytes()).digest(), 'sdist wheel differs'
print('Установленные wheel и zipapp: версия, схема и 12 запусков audit проверены; сборка из исходного архива совпала с wheel')
