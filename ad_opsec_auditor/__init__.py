"""Автономный аудитор свидетельств AD; сбор по сети отсутствует."""
__version__ = '0.1.0a2'


def audit_bytes(raw):
    """Проверить bytes JSON и вернуть отчёт; не читать файлы и не использовать сеть."""
    from .validation import parse_snapshot
    from .report import make_report
    return make_report(parse_snapshot(raw), raw)
