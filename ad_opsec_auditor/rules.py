"""Deterministic baseline-v1 rules over operator-normalized evidence."""
from dataclasses import dataclass

RULES_VERSION = 'baseline-v1'


@dataclass(frozen=True)
class Rule:
    check_id: str
    title: str
    severity: str
    required: tuple
    remediation: str
    predicates: tuple = ()


RULES = (
    Rule('T0-01', 'Избыточные привилегии Tier 0', 'high',
         ('unexpected_admin_paths', 'unapproved_privileged_members'),
         'Проверить неутверждённые пути управления и членство Tier 0; изменения выполнять только согласованным процессом.',
         (('unexpected_admin_paths', 'eq', 0), ('unapproved_privileged_members', 'eq', 0))),
    Rule('CS-01', 'Риски выдачи сертификатов и управления AD CS', 'critical',
         ('unprivileged_ca_control', 'templates'),
         'Ограничить управление CA и выдачу по шаблонам; перед согласованным изменением проверить выбор субъекта, использование для аутентификации, одобрение и подписи.'),
    Rule('ACL-01', 'Неутверждённые права управления каталогом или делегирования', 'high',
         ('unauthorized_control_edges', 'unresolved_aces'),
         'Разрешить все идентификаторы ACE и GUID объектов; проверить неутверждённые пути ACL и делегирования с владельцем каталога.',
         (('unauthorized_control_edges', 'eq', 0),)),
    Rule('SVC-01', 'Привилегии и жизненный цикл сервисных учётных записей', 'high',
         ('unmanaged_privileged_accounts', 'stale_accounts', 'unrestricted_gmsa_readers'),
         'Проверить привилегии и устаревшие сервисные учётные записи; ограничить чтение gMSA и применять управляемые идентификаторы, где это подходит.',
         (('unmanaged_privileged_accounts', 'eq', 0), ('stale_accounts', 'eq', 0), ('unrestricted_gmsa_readers', 'eq', 0))),
    Rule('NTLM-01', 'Ограничения NTLM и наблюдаемое использование', 'medium',
         ('effective_restriction', 'observed_ntlm'),
         'Проверить наблюдаемые зависимости NTLM и действующие ограничения; вводить согласованные изменения после проверки совместимости.',
         (('effective_restriction', 'eq', True), ('observed_ntlm', 'eq', False))),
    Rule('LDAP-01', 'Действующие требования подписи LDAP и привязки канала', 'high',
         ('effective_signing_required', 'effective_channel_binding_required'),
         'Подтвердить действующие требования подписи LDAP и привязки канала на всех узлах области; перед изменениями проверить совместимость клиентов.',
         (('effective_signing_required', 'eq', True), ('effective_channel_binding_required', 'eq', True))),
    Rule('SMB-01', 'Действующая подпись SMB и устаревший протокол', 'high',
         ('effective_signing_required', 'smb1_enabled'),
         'Подтвердить подпись SMB на всех узлах области; отказаться от SMB1 только согласованным изменением с проверкой совместимости.',
         (('effective_signing_required', 'eq', True), ('smb1_enabled', 'eq', False))),
    Rule('LOG-01', 'Полнота аудита, доставка и хранение событий', 'medium',
         ('effective_advanced_audit', 'forwarding_healthy', 'retention_days'),
         'Подтвердить действующий расширенный аудит, доставку событий до получателя и хранение не менее 30 дней для указанного окна наблюдений.',
         (('effective_advanced_audit', 'eq', True), ('forwarding_healthy', 'eq', True), ('retention_days', 'ge', 30))),
    Rule('REC-01', 'Актуальность свидетельств восстановления леса', 'high',
         ('runbook_reviewed', 'backup_verified', 'isolated_drill_succeeded', 'drill_age_days'),
         'Назначить владельца восстановления, проверить процедуру и резервные копии; проводить отдельно разрешённое изолированное учение не реже чем раз в 180 дней.',
         (('runbook_reviewed', 'eq', True), ('backup_verified', 'eq', True),
          ('isolated_drill_succeeded', 'eq', True), ('drill_age_days', 'le', 180))),
)


def _evaluate(rule, observation):
    if observation is None:
        return 'not_run', 'Наблюдение для этой проверки не предоставлено.', []
    if observation['state'] != 'collected':
        return observation['state'], observation['reason'], []
    if observation['coverage'] != 'complete':
        return 'unknown', 'Покрытие неполное: ' + observation['reason'], []
    if not observation['evidence_refs']:
        return 'unknown', 'Ссылки на свидетельства не предоставлены.', []
    facts = observation['facts']
    missing = sorted(set(rule.required) - set(facts))
    if missing:
        return 'unknown', 'Отсутствуют обязательные факты: ' + ', '.join(missing), []
    violations = []
    if rule.check_id == 'CS-01':
        if facts['unprivileged_ca_control']:
            violations.append('unprivileged_ca_control имеет значение true')
        # Empty template inventory cannot demonstrate enrollment safety.
        if not facts['templates'] and not violations:
            return 'unknown', 'Перечень шаблонов отсутствует; выдача сертификатов AD CS не оценена.', []
        for index, template in enumerate(facts['templates']):
            if (template['published'] and template['authentication']
                    and template['enrollee_supplies_subject'] and template['unprivileged_enrollment']
                    and not template['approval_required'] and template['authorized_signatures'] == 0):
                violations.append(f'templates[{index}] разрешает неутверждённый выбор субъекта для аутентификации')
    else:
        for field, operator, expected in rule.predicates:
            actual = facts[field]
            safe = {'eq': actual == expected, 'ge': actual >= expected, 'le': actual <= expected}[operator]
            if not safe:
                violations.append(f'{field} должно удовлетворять {operator} {expected}')
        if rule.check_id == 'ACL-01' and facts['unresolved_aces'] > 0 and not violations:
            return 'unknown', 'Неразрешённые ACE не позволяют сделать полный вывод о правах.', []
    if violations:
        return 'fail', 'Нарушены условия базовой политики.', violations
    return 'pass', 'Все условия базовой политики выполнены для заявленного полного покрытия.', []


def evaluate(snapshot):
    """Call only with a validated snapshot; never mutate supplied facts."""
    results = []
    for rule in RULES:
        observation = snapshot['observations'].get(rule.check_id)
        status, reason, violations = _evaluate(rule, observation)
        results.append({
            'check_id': rule.check_id, 'rule_id': rule.check_id + ':' + RULES_VERSION,
            'title': rule.title, 'status': status,
            'severity': rule.severity if status == 'fail' else 'info',
            'risk_severity': rule.severity,
            'confidence': 'medium' if status in {'pass', 'fail'} else 'low',
            'coverage': observation['coverage'] if observation else 'none',
            'evidence_refs': sorted(observation['evidence_refs']) if observation else [],
            'reason': reason, 'violations': violations,
            'remediation': rule.remediation,
            'limitations': 'Происхождение нормализованных свидетельств оператора независимо не подтверждено; реальная AD не проверялась.',
        })
    return results
