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


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline AD posture evidence auditor. No live AD collection.')
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('schema', help='Print input JSON Schema v1')
    validate = commands.add_parser('validate', help='Validate a local normalized JSON snapshot')
    validate.add_argument('input')
    audit = commands.add_parser('audit', help='Evaluate local evidence with baseline-v1 rules')
    audit.add_argument('input')
    audit.add_argument('--format', choices=('json', 'markdown'), default='json')
    audit.add_argument('--output', help='Create a new file (never overwrite); default stdout')
    args = parser.parse_args(argv)
    try:
        if args.command == 'schema':
            write_output(json.dumps(snapshot_schema(), ensure_ascii=True, sort_keys=True, indent=2) + '\n', None)
            return 0
        snapshot, raw = load_snapshot(args.input)
        if args.command == 'validate':
            write_output('Snapshot structure and references are valid; no live infrastructure verified.\n', None)
            return 0
        report = make_report(snapshot, raw)
        content = json_report(report) if args.format == 'json' else markdown_report(report)
        write_output(content, args.output)
        return audit_exit_code(report)
    except InputError as exc:
        print('error: ' + str(exc), file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print('error: cannot create or write report; destination must be new and writable', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
