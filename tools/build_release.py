"""Build pinned wheel/sdist and deterministic stdlib portable zipapp."""
import gzip
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

from release_common import normalize_wheel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ad_opsec_auditor import __version__

EPOCH = 1770000000
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
# Never remove files not owned by this exact release version.
names = [f'ad_opsec_auditor-{__version__}-py3-none-any.whl', f'ad_opsec_auditor-{__version__}.tar.gz',
         f'ad-opsec-auditor-{__version__}.pyz']
for name in names:
    (DIST / name).unlink(missing_ok=True)
environment = dict(os.environ, SOURCE_DATE_EPOCH=str(EPOCH))
subprocess.run([sys.executable, '-m', 'build', '--no-isolation', '--outdir', str(DIST)],
               cwd=ROOT, env=environment, check=True)
normalize_wheel(DIST / names[0])
# Normalize sdist timestamps, ordering, ownership and gzip header.
archive = DIST / names[1]
with tarfile.open(archive, 'r:gz') as stream:
    entries = [(info, stream.extractfile(info).read() if info.isfile() else None) for info in stream.getmembers()]
with archive.open('wb') as raw:
    with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as stream:
            for info, contents in sorted(entries, key=lambda pair: pair[0].name):
                info.mtime, info.uid, info.gid = EPOCH, 0, 0
                info.uname = info.gname = ''
                info.mode = 0o755 if info.isdir() else 0o644
                info.pax_headers = {}
                stream.addfile(info, io.BytesIO(contents) if contents is not None else None)
with zipfile.ZipFile(DIST / names[2], 'w', compression=zipfile.ZIP_DEFLATED) as stream:
    files = [(f'ad_opsec_auditor/{p.name}', p.read_bytes())
             for p in sorted((ROOT / 'ad_opsec_auditor').iterdir()) if p.suffix in {'.py', '.json'}]
    files.extend((name, (ROOT / name).read_bytes()) for name in ['LICENSE', 'LICENSE.ru.md'])
    files.append(('__main__.py', b'from ad_opsec_auditor.cli import main\nraise SystemExit(main())\n'))
    for name, contents in sorted(files):
        info = zipfile.ZipInfo(name, date_time=(2026, 2, 2, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        stream.writestr(info, contents)
lines = [hashlib.sha256((DIST / name).read_bytes()).hexdigest() + '  ' + name for name in names]
(DIST / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
print('Собраны артефакты и SHA256SUMS:', ', '.join(names))
