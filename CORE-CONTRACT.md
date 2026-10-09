# Контракты CLI, JSON и библиотеки

## CLI

`ad-opsec-auditor` или `python -m ad_opsec_auditor`: `--version`, `--help`, `schema`, `validate INPUT`, `audit INPUT [--format json|markdown] [--output NEW_FILE]`. Нет HTTP API, сетевого клиента, authentication endpoint, динамических плагинов или исполнения remediation.

Validate/schema: 0 при успехе. Audit: 0 только все pass; 1 при хотя бы одном fail; 3 при unknown/not_run без fail; 2 при неверном вводе/аргументах/I/O. Stdout — отчёт/результат; stderr — безопасная русская диагностика без входных значений. `--output` создаёт файл эксклюзивно и не перезаписывает существующий/symlink/вход. UTF-8; JSON использует стандартное экранирование Unicode.

## JSON

Input schema_version=1; точные поля/ограничения и семантические связи: [контракт снимка](docs/input-contract.md), [схема](schemas/snapshot-v1.schema.json). Output report_schema_version=1, engine_version, rules_version=baseline-v1, input_sha256, synthetic/provenance, scope/collected_at/source/warning, summary/results/evidence. Статусы/ключи сохраняются между 0.1.0a1 и 0.1.0a2; изменены человекочитаемые тексты.

Связь результата: check_id/rule_id, status, severity/risk_severity/confidence, coverage, evidence_refs, reason, violations, remediation, limitations. Происхождение и правдивость источника не удостоверяются. Pass — лишь соответствие заявленных фактов правилам. [Матрица](docs/check-matrix.md).

## Библиотека

`from ad_opsec_auditor import audit_bytes`: `audit_bytes(raw: bytes) -> dict` проверяет bounded UTF-8 JSON и строит отчёт с хешем тех же байтов. Неверный снимок вызывает `ad_opsec_auditor.validation.InputError`. Нет чтения файлов/сети или мутации raw. Код выхода относится только к CLI; библиотека возвращает структуру.

Нижний уровень: `parse_snapshot(raw)` возвращает валидированный dict; `load_snapshot(path)` возвращает (dict, raw_bytes), принимает обычный локальный файл. `validate_snapshot(data)` проверяет схему и ссылки нормализованного dict. `evaluate(snapshot)` и `make_report(snapshot, raw)` требуют уже валидированных данных, соответствующих raw; для безопасной композиции предпочитать audit_bytes. Низкоуровневые функции не являются обещанием стабильного внешнего ABI.

## Расширение правил

Добавить постоянный ID в FACTS/schema.py, запись Rule в RULES/rules.py, требования/матрицу/ограничения и positive/negative/missing тесты. Специальные условия — явный проверенный код, не выражения из входа. Обновить опубликованную и встроенную схему, выполнить check_schema.py. При смене контракта/логики пересмотреть версии; перевод не меняет baseline-v1. Не считать mock/synthetic доказательством реального сбора.
