# Требования GITHUB-OPSEC: Microsoft AD

Статус: требования продукта и MVP, 2026-10-09. Заказчик задаёт границы продукта; владелец AD утверждает scope и доступ, security reviewer утверждает правила, оператор исполняет сбор, владелец восстановления подтверждает процедуры. Пользователь разрешил реализацию, commit/push/PR/merge и prerelease в текущем задании.

## Цель и границы

Аудитор формирует воспроизводимую оценку конфигурации AD и её ограничений. Он работает только чтением, без эксплуатации, исправления конфигурации и получения секретов. Облако Linux предназначено для документации, синтетических данных и будущего offline-анализатора. Windows-стенд обязателен для проверки реального сбора. Производственный лес не является тестовым стендом.

В scope: Tier 0, AD CS, ACL и делегирование, сервисные учётные записи, NTLM/LDAP/SMB, журналирование и готовность восстановления леса. Entra ID, эксплуатация CVE, пентест, парольный аудит, автоисправление и резервное копирование самим аудитором вне scope.

## Функциональные требования

| ID | Требование | Приёмка |
| --- | --- | --- |
| FR-01 | Явный scope: лес, домены, серверы, OU, разрешённые источники | Сбор отклоняет цели вне scope; покрытие явно перечислено |
| FR-02 | Только разрешённые read API и утверждённые запросы | Windows-трасса не содержит записи в AD/CA/GPO; отказ доступа не вызывает повышение прав |
| FR-03 | Tier 0: членство, вложенность, привилегированные ACL, административные пути | Сопоставление с эталонной топологией, циклы и неизвестные группы видны |
| FR-04 | AD CS: шаблоны, CA, права, enrollment policy | Риск привязан к комбинации условий; нет выдачи сертификатов |
| FR-05 | ACL и делегирование: inheritance, object GUID, trusts, KCD/RBCD | Неизвестные GUID и неполные границы не дают ложный pass |
| FR-06 | Service accounts: SPN, gMSA metadata, privileges, lifecycle | Никакие managed passwords, hashes или tickets не читаются |
| FR-07 | NTLM/LDAP/SMB: политика и свидетельства применения | Раздельные configured/effective/observed; отсутствие событий не доказывает отсутствие NTLM |
| FR-08 | Logging: audit policy, retention, forwarding coverage | Недоступный журнал = unknown, а не здоровая конфигурация |
| FR-09 | Recovery: инвентаризация процедур, доказательств и учений | Наличие backup не равно доказанному восстановлению; аудитор не запускает restore |
| FR-10 | Версионированный JSON отчёт | ID правила, scope, источник, время UTC, evidence, severity, confidence, remediation, limitations |
| FR-11 | Offline повторный анализ | Одни данные и версии правил дают одинаковые findings; время запуска хранится отдельно |
| FR-12 | Частичный сбор | Для каждого check coverage и причина unavailable; missing не преобразуется в pass |

## Нефункциональные требования

NFR-01: входные данные недоверенные; schema version, ограничения размера/глубины, timeouts и безопасный разбор обязательны. NFR-02: минимальные права по источнику, без Domain Admin по умолчанию; дополнительные read-разрешения документируются отдельно. NFR-03: collector ограничивает страницы, число объектов и параллелизм; исходная цель — один запрос одновременно, timeout 30 секунд, максимум 1000 записей на страницу; значения уточняются нагрузочным тестом. NFR-04: не обходить TLS, подписи или проверки артефактов. NFR-05: сырые данные и отчёты остаются в частном хранилище с ACL, шифрованием и согласованным сроком удаления (для лаборатории 7 дней). NFR-06: отчёт не содержит credentials, private keys, ticket material, полных event payloads; идентификаторы минимизируются. NFR-07: стабильные check ID, versioned rules и traceability к матрице.

## Семантика результата и готовность

Результат проверки: pass, fail, unknown, not_applicable, not_run. Severity (critical/high/medium/low/info) отделена от confidence (high/medium/low). Pass требует полного достаточного evidence для заявленного scope. Unknown означает недостаток доступа/данных; not_run — не запускали; not_applicable требует обоснования. Исключение имеет владельца, срок и rationale и не удаляет finding.

Приёмка документационного этапа: все восемь областей отражены в матрице, есть threat model, архитектура, лаборатория, ADR и воспроизводимый local/CI check. Приёмка продукта позже: unit/fixture suite, Windows integration evidence и negative safety checks. Прохождение Linux CI не является приёмкой collector или безопасности леса.

## MVP-ограничение и дополнительные требования

MVP-01: CLI audit/validate/schema; JSON и escaped Markdown; четыре outcome pass/fail/unknown/not_run. not_applicable отложен: не выдавать pass для исключённого источника. MVP-02: анализатор принимает нормализованные facts от оператора, а не сам извлекает AD; это не выполнение FR-02 native collector. MVP-03: schema strict, input ≤2 MiB, глубина ≤16, unknown fields/duplicate keys/non-finite numbers запрещены. MVP-04: pass требует complete coverage, всех необходимых facts и существующих evidence references. MVP-05: правила/результаты детерминированны относительно input bytes и engine version, отчёт с SHA256 и provenance warning. MVP-06: error exit 2 без traceback/echo input; существующий output не перезаписывается. MVP-07: no runtime dependencies, wheel/sdist/zipapp, pinned build tooling и local/CI installation tests. MVP-08: prerelease не закрывает live Windows acceptance. См. [план MVP](mvp-plan.md).
