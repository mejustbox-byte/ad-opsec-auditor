"""Single source for the supported input JSON Schema contract."""
from copy import deepcopy


def text(maximum=512, minimum=1):
    return {'type': 'string', 'minLength': minimum, 'maxLength': maximum,
            'pattern': r'^[^\x00-\x1f\x7f]*$'}


def obj(properties, required=()):
    return {'type': 'object', 'properties': properties, 'required': list(required),
            'additionalProperties': False}


BOOL = {'type': 'boolean'}
COUNT = {'type': 'integer', 'minimum': 0, 'maximum': 1000000}
IDENTIFIER = {'type': 'string', 'pattern': r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$', 'maxLength': 64}
UTC = {**text(20), 'format': 'date-time', 'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'}
TEMPLATE = obj({
    'name': text(128), 'published': BOOL, 'authentication': BOOL,
    'enrollee_supplies_subject': BOOL, 'unprivileged_enrollment': BOOL,
    'approval_required': BOOL, 'authorized_signatures': COUNT,
}, ('name', 'published', 'authentication', 'enrollee_supplies_subject',
    'unprivileged_enrollment', 'approval_required', 'authorized_signatures'))
FACTS = {
    'T0-01': obj({'unexpected_admin_paths': COUNT, 'unapproved_privileged_members': COUNT}),
    'CS-01': obj({'unprivileged_ca_control': BOOL,
                  'templates': {'type': 'array', 'items': TEMPLATE, 'maxItems': 1000}}),
    'ACL-01': obj({'unauthorized_control_edges': COUNT, 'unresolved_aces': COUNT}),
    'SVC-01': obj({'unmanaged_privileged_accounts': COUNT, 'stale_accounts': COUNT,
                   'unrestricted_gmsa_readers': COUNT}),
    'NTLM-01': obj({'effective_restriction': BOOL, 'observed_ntlm': BOOL}),
    'LDAP-01': obj({'effective_signing_required': BOOL, 'effective_channel_binding_required': BOOL}),
    'SMB-01': obj({'effective_signing_required': BOOL, 'smb1_enabled': BOOL}),
    'LOG-01': obj({'effective_advanced_audit': BOOL, 'forwarding_healthy': BOOL,
                   'retention_days': COUNT}),
    'REC-01': obj({'runbook_reviewed': BOOL, 'backup_verified': BOOL,
                   'isolated_drill_succeeded': BOOL, 'drill_age_days': COUNT}),
}


def snapshot_schema():
    observations = {}
    for check_id, facts in FACTS.items():
        observations[check_id] = obj({
            'state': {'type': 'string', 'enum': ['collected', 'unknown', 'not_run']},
            'coverage': {'type': 'string', 'enum': ['complete', 'partial', 'none']},
            'reason': text(512, 0),
            'evidence_refs': {'type': 'array', 'items': IDENTIFIER, 'maxItems': 500, 'uniqueItems': True},
            'facts': facts,
        }, ('state', 'coverage', 'reason', 'evidence_refs', 'facts'))
    schema = obj({
        'schema_version': {'type': 'integer', 'enum': [1]},
        'synthetic': BOOL,
        'scope': text(256),
        'collected_at': UTC,
        'source': text(128),
        'evidence': {'type': 'array', 'maxItems': 500, 'items': obj({
            'id': IDENTIFIER, 'source': text(128), 'collected_at': UTC,
            'description': text(512),
        }, ('id', 'source', 'collected_at', 'description'))},
        'observations': obj(observations),
    }, ('schema_version', 'synthetic', 'scope', 'collected_at', 'source', 'evidence', 'observations'))
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    descriptions = {'schema_version': 'Версия контракта входных данных.', 'synthetic': 'Признак искусственного примера; не подтверждает подлинность данных.', 'scope': 'Заявленная область снимка; полнота не проверяется сборщиком.', 'collected_at': 'Время снимка в UTC.', 'source': 'Заявленный источник без проверки подлинности.', 'evidence': 'Ссылочные свидетельства; секреты и исходные выгрузки не допускаются.', 'observations': 'Нормализованные факты по идентификаторам проверок.'}
    for key, description in descriptions.items():
        schema['properties'][key]['description'] = description
    schema['title'] = 'Нормализованный снимок AD OPSEC v1'
    return deepcopy(schema)
