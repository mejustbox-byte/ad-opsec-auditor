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
    Rule('T0-01', 'Tier 0 privilege exposure', 'high',
         ('unexpected_admin_paths', 'unapproved_privileged_members'),
         'Review and remove unapproved Tier 0 control paths and memberships through an authorized change process.',
         (('unexpected_admin_paths', 'eq', 0), ('unapproved_privileged_members', 'eq', 0))),
    Rule('CS-01', 'AD CS enrollment and control exposure', 'critical',
         ('unprivileged_ca_control', 'templates'),
         'Restrict CA control and template enrollment; review subject supply, authentication use, approval and signatures before any authorized change.'),
    Rule('ACL-01', 'Unauthorized directory control or delegation', 'high',
         ('unauthorized_control_edges', 'unresolved_aces'),
         'Resolve all ACE identities and object GUIDs; review unauthorized ACL/delegation paths with the directory owner.',
         (('unauthorized_control_edges', 'eq', 0),)),
    Rule('SVC-01', 'Service account exposure and lifecycle', 'high',
         ('unmanaged_privileged_accounts', 'stale_accounts', 'unrestricted_gmsa_readers'),
         'Review service privileges and stale accounts; restrict gMSA readers and use managed identities where suitable.',
         (('unmanaged_privileged_accounts', 'eq', 0), ('stale_accounts', 'eq', 0), ('unrestricted_gmsa_readers', 'eq', 0))),
    Rule('NTLM-01', 'NTLM restriction and observed use', 'medium',
         ('effective_restriction', 'observed_ntlm'),
         'Review observed NTLM dependencies and effective restriction policy; stage changes after compatibility testing.',
         (('effective_restriction', 'eq', True), ('observed_ntlm', 'eq', False))),
    Rule('LDAP-01', 'LDAP effective signing and channel binding', 'high',
         ('effective_signing_required', 'effective_channel_binding_required'),
         'Validate effective LDAP signing and channel binding requirements on all scoped endpoints; test client compatibility before changes.',
         (('effective_signing_required', 'eq', True), ('effective_channel_binding_required', 'eq', True))),
    Rule('SMB-01', 'SMB effective signing and legacy protocol', 'high',
         ('effective_signing_required', 'smb1_enabled'),
         'Validate SMB signing on scoped hosts and retire SMB1 through an authorized compatibility-tested change.',
         (('effective_signing_required', 'eq', True), ('smb1_enabled', 'eq', False))),
    Rule('LOG-01', 'Audit coverage, forwarding and retention', 'medium',
         ('effective_advanced_audit', 'forwarding_healthy', 'retention_days'),
         'Verify effective advanced auditing, end-to-end delivery and at least 30 days of retention for the scoped evidence window.',
         (('effective_advanced_audit', 'eq', True), ('forwarding_healthy', 'eq', True), ('retention_days', 'ge', 30))),
    Rule('REC-01', 'Forest recovery evidence freshness', 'high',
         ('runbook_reviewed', 'backup_verified', 'isolated_drill_succeeded', 'drill_age_days'),
         'Assign a recovery owner, review the runbook, verify backups and conduct a separately authorized isolated recovery drill at least every 180 days.',
         (('runbook_reviewed', 'eq', True), ('backup_verified', 'eq', True),
          ('isolated_drill_succeeded', 'eq', True), ('drill_age_days', 'le', 180))),
)


def _evaluate(rule, observation):
    if observation is None:
        return 'not_run', 'No observation supplied for this check.', []
    if observation['state'] != 'collected':
        return observation['state'], observation['reason'], []
    if observation['coverage'] != 'complete':
        return 'unknown', 'Coverage is incomplete: ' + observation['reason'], []
    if not observation['evidence_refs']:
        return 'unknown', 'No evidence references supplied.', []
    facts = observation['facts']
    missing = sorted(set(rule.required) - set(facts))
    if missing:
        return 'unknown', 'Required facts missing: ' + ', '.join(missing), []
    violations = []
    if rule.check_id == 'CS-01':
        if facts['unprivileged_ca_control']:
            violations.append('unprivileged_ca_control is true')
        # Empty template inventory cannot demonstrate enrollment safety.
        if not facts['templates'] and not violations:
            return 'unknown', 'No template inventory supplied; AD CS enrollment not assessed.', []
        for index, template in enumerate(facts['templates']):
            if (template['published'] and template['authentication']
                    and template['enrollee_supplies_subject'] and template['unprivileged_enrollment']
                    and not template['approval_required'] and template['authorized_signatures'] == 0):
                violations.append(f'templates[{index}] permits unapproved authentication subject supply')
    else:
        for field, operator, expected in rule.predicates:
            actual = facts[field]
            safe = {'eq': actual == expected, 'ge': actual >= expected, 'le': actual <= expected}[operator]
            if not safe:
                violations.append(f'{field} must be {operator} {expected}')
        if rule.check_id == 'ACL-01' and facts['unresolved_aces'] > 0 and not violations:
            return 'unknown', 'Unresolved ACEs prevent a complete access conclusion.', []
    if violations:
        return 'fail', 'Baseline predicates violated.', violations
    return 'pass', 'All baseline predicates met for declared complete coverage.', []


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
            'limitations': 'Operator-normalized evidence is not independently authenticated; no live AD verification.',
        })
    return results
