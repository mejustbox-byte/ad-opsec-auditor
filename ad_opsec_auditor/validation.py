"""Bounded input parser and strict contract validation, without input echo."""
import datetime
import json
import os
from pathlib import Path
import re
import stat

from .schema import snapshot_schema

MAX_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 16


class InputError(ValueError):
    """Safe-to-print structural error, never includes user data."""


def _depth_guard(raw):
    depth = 0
    in_string = False
    escape = False
    for character in raw:
        if in_string:
            if escape:
                escape = False
            elif character == '\\':
                escape = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in '{[':
            depth += 1
            if depth > MAX_DEPTH:
                raise InputError('Input nesting exceeds 16 levels')
        elif character in '}]':
            depth -= 1


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('Duplicate JSON object key')
        result[key] = value
    return result


def _constant(_value):
    raise InputError('Non-finite JSON numbers are not allowed')


def _validate(value, schema):
    kind = schema['type']
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'integer': int}
    if type(value) is not types[kind]:
        raise InputError('Input contains an invalid field type')
    if 'enum' in schema and value not in schema['enum']:
        raise InputError('Input contains an unsupported version or state')
    if kind == 'object':
        properties = schema['properties']
        if set(value) - set(properties):
            raise InputError('Unknown input fields are not allowed')
        if set(schema['required']) - set(value):
            raise InputError('Required input fields are missing')
        for key, child in value.items():
            _validate(child, properties[key])
    elif kind == 'array':
        if len(value) > schema['maxItems']:
            raise InputError('Input array exceeds contract limit')
        for child in value:
            _validate(child, schema['items'])
        if schema.get('uniqueItems') and len(set(value)) != len(value):
            raise InputError('Duplicate evidence reference')
    elif kind == 'string':
        if not schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', 512):
            raise InputError('Input string exceeds contract limits or is empty')
        if 'pattern' in schema and re.fullmatch(schema['pattern'], value) is None:
            raise InputError('Input string contains invalid characters or format')
        # Also reject unpaired surrogate code points, which cannot be safely UTF-8 encoded.
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise InputError('Invalid Unicode in input')
        if schema.get('format') == 'date-time':
            try:
                datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError as exc:
                raise InputError('Invalid UTC timestamp') from exc
    elif kind == 'integer':
        if not schema.get('minimum', 0) <= value <= schema.get('maximum', 1000000):
            raise InputError('Input integer outside contract limits')


def validate_snapshot(data):
    _validate(data, snapshot_schema())
    ids = [entry['id'] for entry in data['evidence']]
    if len(ids) != len(set(ids)):
        raise InputError('Duplicate evidence identifier')
    available = set(ids)
    for entry in data['evidence']:
        if entry['collected_at'] > data['collected_at']:
            raise InputError('Evidence is newer than snapshot collection time')
    for observation in data['observations'].values():
        if set(observation['evidence_refs']) - available:
            raise InputError('Dangling evidence reference')
        if observation['state'] != 'collected':
            if observation['coverage'] != 'none' or observation['facts'] or observation['evidence_refs']:
                raise InputError('Uncollected observation must have no facts or evidence')
            if not observation['reason'].strip():
                raise InputError('Uncollected observation requires a reason')
        else:
            if observation['coverage'] == 'none':
                raise InputError('Collected observation requires complete or partial coverage')
            if observation['coverage'] == 'partial' and not observation['reason'].strip():
                raise InputError('Partial coverage requires a reason')
    return data


def parse_snapshot(raw):
    if len(raw) > MAX_BYTES:
        raise InputError('Input exceeds 2 MiB limit')
    try:
        text = raw.decode('utf-8')
        _depth_guard(text)
        data = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
        return validate_snapshot(data)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InputError('Input must be bounded valid UTF-8 JSON') from exc
    except ValueError as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError('Invalid numeric JSON input') from exc


def load_snapshot(path):
    descriptor = None
    try:
        # Nonblocking avoids hanging on FIFO inputs; fstat checks the actual opened object.
        descriptor = os.open(Path(path), os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise InputError('Input must be a regular local file')
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            raw = stream.read(MAX_BYTES + 1)
        return parse_snapshot(raw), raw
    except OSError as exc:
        raise InputError('Cannot read input file') from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
