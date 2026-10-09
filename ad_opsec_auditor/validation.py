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
                raise InputError('Глубина входных данных превышает 16 уровней')
        elif character in '}]':
            depth -= 1


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('Повторяющийся ключ объекта JSON')
        result[key] = value
    return result


def _constant(_value):
    raise InputError('Бесконечные числа и NaN запрещены в JSON')


def _validate(value, schema):
    kind = schema['type']
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'integer': int}
    if type(value) is not types[kind]:
        raise InputError('Неверный тип поля входных данных')
    if 'enum' in schema and value not in schema['enum']:
        raise InputError('Неподдерживаемая версия или состояние входных данных')
    if kind == 'object':
        properties = schema['properties']
        if set(value) - set(properties):
            raise InputError('Неизвестные поля входных данных запрещены')
        if set(schema['required']) - set(value):
            raise InputError('Отсутствуют обязательные поля входных данных')
        for key, child in value.items():
            _validate(child, properties[key])
    elif kind == 'array':
        if len(value) > schema['maxItems']:
            raise InputError('Массив превышает ограничение контракта')
        for child in value:
            _validate(child, schema['items'])
        if schema.get('uniqueItems') and len(set(value)) != len(value):
            raise InputError('Повторяющаяся ссылка на свидетельство')
    elif kind == 'string':
        if not schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', 512):
            raise InputError('Строка пуста или превышает ограничение контракта')
        if 'pattern' in schema and re.fullmatch(schema['pattern'], value) is None:
            raise InputError('Неверные символы или формат строки')
        # Also reject unpaired surrogate code points, which cannot be safely UTF-8 encoded.
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise InputError('Некорректный Unicode во входных данных')
        if schema.get('format') == 'date-time':
            try:
                datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError as exc:
                raise InputError('Некорректное время UTC') from exc
    elif kind == 'integer':
        if not schema.get('minimum', 0) <= value <= schema.get('maximum', 1000000):
            raise InputError('Целое число вне ограничений контракта')


def validate_snapshot(data):
    _validate(data, snapshot_schema())
    ids = [entry['id'] for entry in data['evidence']]
    if len(ids) != len(set(ids)):
        raise InputError('Повторяющийся идентификатор свидетельства')
    available = set(ids)
    for entry in data['evidence']:
        if entry['collected_at'] > data['collected_at']:
            raise InputError('Свидетельство новее времени сбора снимка')
    for observation in data['observations'].values():
        if set(observation['evidence_refs']) - available:
            raise InputError('Ссылка на отсутствующее свидетельство')
        if observation['state'] != 'collected':
            if observation['coverage'] != 'none' or observation['facts'] or observation['evidence_refs']:
                raise InputError('Наблюдение без сбора не должно содержать факты или свидетельства')
            if not observation['reason'].strip():
                raise InputError('Наблюдение без сбора требует указания причины')
        else:
            if observation['coverage'] == 'none':
                raise InputError('Собранное наблюдение требует complete или partial покрытия')
            if observation['coverage'] == 'partial' and not observation['reason'].strip():
                raise InputError('Неполное покрытие требует указания причины')
    return data


def parse_snapshot(raw):
    if len(raw) > MAX_BYTES:
        raise InputError('Вход превышает ограничение 2 MiB')
    try:
        text = raw.decode('utf-8')
        _depth_guard(text)
        data = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
        return validate_snapshot(data)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InputError('Вход должен быть корректным JSON в UTF-8 в пределах ограничений') from exc
    except ValueError as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError('Некорректное число JSON во входных данных') from exc


def load_snapshot(path):
    descriptor = None
    try:
        # Nonblocking avoids hanging on FIFO inputs; fstat checks the actual opened object.
        descriptor = os.open(Path(path), os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise InputError('Вход должен быть обычным локальным файлом')
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            raw = stream.read(MAX_BYTES + 1)
        return parse_snapshot(raw), raw
    except OSError as exc:
        raise InputError('Не удалось прочитать входной файл') from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
