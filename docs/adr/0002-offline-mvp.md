# ADR-0002: evidence-first offline MVP

Дата: 2026-10-09. Статус: принято. Дополняет ADR-0001.

Пользователь разрешил реализацию, commit/push, PR, merge и release. Windows AD стенд пока недоступен. Решение: выпустить честный offline prerelease v0.1.0a1, не выдавая synthetic tests за проверку AD и не поставляя непроверенный collector.

Python >=3.12,<3.13, без runtime dependencies. JSON Schema Draft 2020-12 описывает узкий контракт; встроенный валидатор поддерживает только использованные keywords и принимает те же constraints. Схема строится из одного declarative source и включается в package. Отдельные tests сравнивают её с jsonschema эталоном в development окружении. Нормализованные факты доступны только по фиксированным полям каждого правила; нет произвольного скрипта или rule expression.

Публичные примеры synthetic=true. Input может обозначить synthetic=false в частном запуске, но report всегда предупреждает об unverified provenance: заявленный флаг не доказывает истинность данных. Evidence refs локальные логические IDs, не paths/URLs для чтения. Auditor не открывает файлы по ссылкам.

Build tooling и test-only jsonschema dependencies pinned по версии и SHA256; runtime остаётся stdlib-only. CLI работает из source, wheel и zipapp. Wheel install без зависимостей пригоден для private offline анализа. Portable zipapp включён для no-pip запуска. Все release artifacts собираются из проверенного checkout; SHA256SUMS не является криптографической подписью владельца.

Нормализованные счётчики/booleans ускоряют triage, но не заменяют raw ACL evaluation, CA exploitation proofs, effective host policy collection или recovery drill. Утверждённые thresholds являются baseline-v1, конфигурируемые baselines отложены до schema migration. Native collector остаётся отдельным следующим этапом.
