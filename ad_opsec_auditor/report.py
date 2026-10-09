"""Deterministic reports, with untrusted Markdown escaped."""
from collections import Counter
import hashlib
import html
import json

from . import __version__
from .rules import evaluate, RULES_VERSION

STATUSES = ('pass', 'fail', 'unknown', 'not_run')


def make_report(snapshot, raw):
    results = evaluate(snapshot)
    counts = Counter(result['status'] for result in results)
    used = {reference for result in results for reference in result['evidence_refs']}
    return {
        'report_schema_version': 1, 'engine_version': __version__, 'rules_version': RULES_VERSION,
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'synthetic': snapshot['synthetic'], 'scope': snapshot['scope'],
        'collected_at': snapshot['collected_at'], 'source': snapshot['source'],
        'provenance': 'synthetic-example' if snapshot['synthetic'] else 'operator-supplied-unverified',
        'warning': 'Offline normalized evidence only. No live AD, AD CS or forest recovery validation performed.',
        'summary': {status: counts[status] for status in STATUSES}, 'results': results,
        'evidence': sorted((e for e in snapshot['evidence'] if e['id'] in used), key=lambda e: e['id']),
    }


def json_report(report):
    return json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2) + '\n'


def escape_markdown(value):
    # Escape Markdown structure before HTML; entities contain no executable markup.
    text = str(value)
    text = ''.join(c if ord(c) >= 32 and ord(c) != 127 else ' ' for c in text)
    for character in '\\`*_{}[]()#+-.!|':
        text = text.replace(character, '\\' + character)
    return html.escape(text, quote=True)


def markdown_report(report):
    esc = escape_markdown
    lines = ['# AD OPSEC offline evidence report', '', report['warning'], '',
             f"Scope: {esc(report['scope'])}", f"Provenance: {esc(report['provenance'])}",
             f"Collected at: {esc(report['collected_at'])}",
             f"Engine: {esc(report['engine_version'])}; rules: {esc(report['rules_version'])}",
             f"Input SHA256: {report['input_sha256']}", '',
             ' | '.join(f'{s}: {report["summary"][s]}' for s in STATUSES), '',
             '| Check | Status | Severity | Confidence | Coverage |', '| --- | --- | --- | --- | --- |']
    for result in report['results']:
        lines.append('| ' + ' | '.join(esc(result[k]) for k in
                     ('check_id', 'status', 'severity', 'confidence', 'coverage')) + ' |')
    for result in report['results']:
        lines += ['', f"## {result['check_id']}: {esc(result['title'])}", '',
                  f"Result: {esc(result['status'])}. {esc(result['reason'])}",
                  'Evidence: ' + (', '.join(esc(e) for e in result['evidence_refs']) or 'none'),
                  'Remediation: ' + esc(result['remediation']),
                  'Limitations: ' + esc(result['limitations'])]
        lines += ['- ' + esc(v) for v in result['violations']]
    lines += ['', '## Referenced evidence', '']
    for evidence in report['evidence']:
        lines.append(f"- {esc(evidence['id'])}: {esc(evidence['source'])}; {esc(evidence['collected_at'])}; {esc(evidence['description'])}")
    return '\n'.join(lines) + '\n'


def audit_exit_code(report):
    if report['summary']['fail']:
        return 1
    if report['summary']['unknown'] or report['summary']['not_run']:
        return 3
    return 0
