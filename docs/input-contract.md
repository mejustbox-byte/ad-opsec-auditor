# Нормализованный снимок v1 и baseline-v1

[Схема JSON](../schemas/snapshot-v1.schema.json) входит в пакет и выводится командой schema. UTF-8, вход ≤2 MiB, глубина ≤16. Неизвестные поля, duplicate keys, non-finite numbers, одиночные Unicode surrogates и управляющие символы запрещены. Время строго `YYYY-MM-DDTHH:MM:SSZ`; свидетельство не новее снимка. До 500 свидетельств и 1000 шаблонов; целые счётчики 0…1,000,000. Дополнительно проверяются связи и согласованность состояний, поэтому одной схемы недостаточно.

## Верхний уровень

Обязательны `schema_version=1`, `synthetic`, `scope`, `collected_at`, `source`, `evidence`, `observations`. `synthetic=true` заявляет вымышленный ввод; false означает данные оператора с непроверенным происхождением. Флаг и хеш не доказывают истинность. `scope` — утверждённая область (1…256 символов), `source` — источник (1…128 символов).

Свидетельство содержит `id`, `source`, `collected_at`, `description`. ID — 1…64 ASCII букв/цифр/`_.:-`, первый символ буквенно-цифровой; уникален. Описание ≤512 символов. `evidence_refs` ссылаются только на этот массив; пути и URL никогда не открываются. Отчёт включает только использованные записи.

Наблюдение находится под ID проверки в `observations`: `state` (collected/unknown/not_run), `coverage` (complete/partial/none), `reason`, `evidence_refs`, `facts`. Для unknown/not_run: none, пустые факты/ссылки, непустая причина. Для collected: complete/partial, для partial обязательна причина. Отсутствующее наблюдение даёт not_run. Отсутствующие факты/ссылки или partial дают unknown. Готовый результат pass нельзя подать вместо фактов.

## Интерпретация фактов

Факты подтверждает доверенный оператор независимыми источниками. Boolean относится ко всем относящимся к проверке узлам утверждённой области, счётчики — к полной области. Незнание выражается отсутствием поля или partial, а не нулём/false. Complete — заявление оператора, не независимо доказанная полнота.

| ID | Ключи facts | Условия соответствия |
| --- | --- | --- |
| T0-01 | unexpected_admin_paths, unapproved_privileged_members | оба =0 |
| CS-01 | unprivileged_ca_control, templates | нет управления CA у непривилегированных; нет полной рискованной комбинации шаблона |
| ACL-01 | unauthorized_control_edges, unresolved_aces | оба =0; неизвестные ACE дают unknown, если нет известного нарушения |
| SVC-01 | unmanaged_privileged_accounts, stale_accounts, unrestricted_gmsa_readers | все =0; устаревание по утверждённой политике владельца |
| NTLM-01 | effective_restriction, observed_ntlm | true/false; наблюдение только для подтверждённого окна и источников |
| LDAP-01 | effective_signing_required, effective_channel_binding_required | оба true, действующие требования всех узлов области |
| SMB-01 | effective_signing_required, smb1_enabled | true/false |
| LOG-01 | effective_advanced_audit, forwarding_healthy, retention_days | true/true/≥30 |
| REC-01 | runbook_reviewed, backup_verified, isolated_drill_succeeded, drill_age_days | true/true/true/≤180 на collected_at |

Шаблон содержит обязательные `name`, `published`, `authentication`, `enrollee_supplies_subject`, `unprivileged_enrollment`, `approval_required`, `authorized_signatures`. Риск: published AND authentication AND enrollee_supplies_subject AND unprivileged_enrollment AND NOT approval_required AND authorized_signatures=0. Это узкий конфигурационный сигнал типа ESC1, не доказательство эксплуатации и не покрытие ESC2…ESC16. Управление CA у непривилегированных отдельно даёт fail. Пустой перечень шаблонов без известного нарушения даёт unknown.

Пороги хранения 30 дней и учения 180 дней — политика baseline-v1 проекта, не универсальный стандарт Microsoft. Устаревание, неожиданные пути и неутверждённые права требуют согласованной политики и свидетельств. Исходные ACE и междоменные графы в MVP не вычисляются. Отсутствие событий ограниченной выборки не доказывает observed_ntlm=false.

## Выход и доверие

`report_schema_version=1`, версии, `input_sha256`, область/источник/время, `synthetic`, `provenance`, `warning`, `summary`, `results`, `evidence`. Результат содержит `check_id`, `rule_id`, `status`, `severity`, `risk_severity`, `confidence`, `coverage`, ссылки, причину, нарушения, рекомендации и ограничения. Критичность fail соответствует риску правила, прочих — info; потенциальный риск сохранён отдельно. Уверенность pass/fail — medium, остальных — low из-за непроверенного происхождения.

Partial всегда unknown даже при известных рискованных фактах; это не означает благополучие. Известное неутверждённое право ACL даёт fail даже при неизвестных ACE, но не полный вывод о графе прав. Повторение тех же байтов с той же версией даёт одинаковый отчёт; изменение пробелов JSON меняет хеш. Рекомендация — текст, не исполняемая команда.
