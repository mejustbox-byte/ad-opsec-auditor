"""Canonical ZIP metadata for repeatable wheels across checkout umasks."""
from pathlib import Path
import zipfile


def normalize_wheel(path):
    path = Path(path)
    with zipfile.ZipFile(path) as stream:
        entries = [(info.filename, stream.read(info.filename)) for info in stream.infolist()]
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as stream:
        for name, content in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 2, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 << 16)
            stream.writestr(info, content)
