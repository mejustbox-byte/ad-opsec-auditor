# Матрица проверок

Проект правил, не результаты аудита. Все Windows сценарии сейчас not_run. Severity ниже — стартовая оценка риска, уточняется контекстом; confidence зависит от evidence. Read permission уточняется для каждого API при реализации.

| Check ID | Requirement | Threat | Область | Evidence и минимальный доступ | Условие finding | Windows: safe / risky / missing | Severity | Lab status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T0-01 | FR-03 | TM-02 | Tier 0 | Nested privileged groups, admin ACL, SID history; AD read + security descriptor visibility | Избыточный путь управления Tier 0 | Разрешённые пути / лишняя вложенная группа / закрытая ACL | high | not_run |
| CS-01 | FR-04 | TM-02 | AD CS | Template/CA ACL, enrollment flags, CA policy; directory + CA read | Опасное сочетание enrollment и authentication capabilities | Ограниченный template / рискованная комбинация / CA недоступна | critical | not_run |
| ACL-01 | FR-05 | TM-05 | ACL/делегирование | DACL, object GUID, inheritance, KCD/RBCD/trust; directory SD read | Неутверждённые write/replication/delegation rights | Эталон ACE / лишнее право / unresolved SID или GUID | high | not_run |
| SVC-01 | FR-06 | TM-04 | Сервисные учётные записи | SPN, account flags, groups, gMSA permitted readers metadata; AD read без password attributes | Привилегии, устаревший lifecycle, неограниченная экспозиция | Ограниченная gMSA / привилегированный svc / неполный lifecycle | high | not_run |
| NTLM-01 | FR-07 | TM-01 | NTLM | GPO/effective policy и ограниченные event metadata; policy/event read | Неприемлемое использование или разрешение NTLM | Ограничение + покрытие / разрешённый fallback / журнал недоступен | medium | not_run |
| LDAP-01 | FR-07 | TM-01 | LDAP | Signing/channel binding settings, applied policy, events; policy/event read | Недостаточная защита LDAP | Подтверждённая effective policy / слабая настройка / нет applied evidence | high | not_run |
| SMB-01 | FR-07 | TM-01 | SMB | Signing/encryption/protocol configured и effective state; member/DC policy read | Неприемлемая signing/protocol конфигурация | Утверждённый baseline / нарушение / host недоступен | high | not_run |
| LOG-01 | FR-08 | TM-05 | Журналирование | Advanced audit policy, retention, forwarding health metadata; delegated event read | Недостаточная регистрация/доставка важных событий | Доставка подтверждена / недостаточная retention / collector channel закрыт | medium | not_run |
| REC-01 | FR-09 | TM-10 | Восстановление леса | Runbook owner, backup verification, isolated drill evidence; document read | Нет актуального доказательства возможности восстановления | Актуальное учение / просроченное учение / только декларация backup | high | not_run |

## Правила интерпретации

Для каждой строки MVP fixture tests проверяют safe→pass, risky→fail и missing→unknown, plus not_applicable с rationale. Конфигурационное несоответствие даёт finding, но не доказывает успешную эксплуатацию. Доступ к recovery документам не доказывает успешный restore; требуется отдельное свидетельство drill. Offline synthetic сценарии реализованы; исходный readiness fixture отдельно проверяет полноту статусов и traceability. Live Windows сценарии остаются not_run. Нормализованные baseline facts и точные ограничения: [input contract](input-contract.md).

FR-01/02/10/11/12 и NFR проверяются сквозными contract/safety тестами: scope violation, forbidden operation, denied read, schema mismatch, deterministic findings, corrupted evidence, cancellation, large input. Эти продуктовые тесты также not_run до реализации. TM-03/06/07/08/09 покрываются cross-cutting safety review и будущими boundary/Windows tests, а не ошибочно маркируются пройденными документационным CI.

Опорные материалы для следующего review: [Microsoft AD security best practices](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory), [LDAP signing](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server), [forest recovery](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide). Ссылки — ориентиры, а не заявление об уже проверенном соответствии. Перед реализацией закрепить конкретные policy baselines и версии ОС.
