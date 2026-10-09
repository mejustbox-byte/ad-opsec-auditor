# Changelog

## 0.1.0a1 — offline prerelease

Первый offline read-only evidence auditor: CLI validate/audit/schema, strict JSON contract, nine baseline rules, evidence/severity/confidence/remediation, JSON/Markdown reports, synthetic examples, unit/integration tests, pinned builds и CI.

Read-only здесь означает чтение локального snapshot и запись выбранного отчёта; нет network collection, credential inputs, remediation execution или AD modifications. Нормализованные facts требуют доверенного источника и ручного review. Rule risk findings не доказывают успешную эксплуатацию.

**Not run:** live AD/AD CS/ACL/RSAT collection, effective GPO/signing/channel validation, least-privilege collector safety, реальный recovery drill, Windows Server 2019/2022/2025 compatibility. Collector не поставляется. Поэтому выпуск prerelease, а не stable production scanner. Hosted Windows CI проверяет только offline Python workflow.

Артефакты: wheel, sdist, Python zipapp, SHA256SUMS. Python 3.12; runtime dependencies отсутствуют. Установка/запуск: [user guide](docs/user-guide.md). Не публиковать secrets или реальные infrastructure exports. Remote PR/merge/CI/release state фиксируется только фактическими результатами GitHub; changelog сам по себе не доказывает публикацию.
