"""Read local snapshots and optionally create a new report; no network access."""
import argparse
import json
import os
import sys

from . import __version__
from .report import audit_exit_code, json_report, make_report, markdown_report
from .schema import snapshot_schema
from .validation import InputError, load_snapshot


def write_output(content, destination):
    if destination is None:
        sys.stdout.write(content)
        return
    # Exclusive creation rejects existing files, symlinks and input aliases.
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
        stream.write(content)


class RussianParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs['add_help'] = False
        super().__init__(*args, **kwargs)
        self.add_argument('-h', '--help', action='help', help='Показать справку и завершить работу')

    def format_help(self):
        return super().format_help().replace('usage:', 'использование:').replace('positional arguments:', 'позиционные аргументы:').replace('options:', 'параметры:')

    def format_usage(self):
        return super().format_usage().replace('usage:', 'использование:')

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, 'ошибка: неверные аргументы; используйте --help\n')


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = RussianParser(description='Автономный аудитор свидетельств безопасности AD. Реальный сбор из AD не выполняется.')
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True, title='команды')
    commands.add_parser('schema', help='Вывести схему входного JSON v1')
    validate = commands.add_parser('validate', help='Проверить локальный нормализованный снимок JSON')
    validate.add_argument('input')
    audit = commands.add_parser('audit', help='Оценить локальные свидетельства по baseline-v1')
    audit.add_argument('input')
    audit.add_argument('--format', choices=('json', 'markdown'), default='json')
    audit.add_argument('--output', help='Создать новый файл без перезаписи; по умолчанию stdout')
    args = parser.parse_args(argv)
    try:
        if args.command == 'schema':
            write_output(json.dumps(snapshot_schema(), ensure_ascii=True, sort_keys=True, indent=2) + '\n', None)
            return 0
        snapshot, raw = load_snapshot(args.input)
        if args.command == 'validate':
            write_output('Структура и ссылки снимка корректны; реальная инфраструктура не проверена.\n', None)
            return 0
        report = make_report(snapshot, raw)
        content = json_report(report) if args.format == 'json' else markdown_report(report)
        write_output(content, args.output)
        return audit_exit_code(report)
    except InputError as exc:
        print('ошибка: ' + str(exc), file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print('ошибка: не удалось записать отчёт; файл назначения должен быть новым и доступным для записи', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
