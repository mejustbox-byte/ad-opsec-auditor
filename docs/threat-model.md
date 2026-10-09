# Модель угроз

## Активы и границы доверия

Защищаем целостность AD/CA/GPO, учётные данные оператора, конфиденциальность топологии/ACL и журналов, достоверность findings и доступность DC. Источники: каталог, CA, политика, журналы и документы recovery. Границы: оператор → Windows collector; collector → службы AD; сырые свидетельства → локальное частное хранилище; явно синтетический fixture → Linux/публичный CI; недоверенный JSON → offline analyzer; отчёт → читатель. Реальные exports не пересекают границу публичного репозитория или GitHub Actions.

Противники: скомпрометированный directory object, ошибающийся оператор, злоумышленник в зависимости/PR, пользователь с доступом к отчёту, скомпрометированный endpoint. Read-only запросы создают сетевой трафик и записи в журналах, поэтому не означают отсутствие операционного воздействия.

## Сценарии и меры

| ID | Угроза | Мера | Проверка / остаточный риск |
| --- | --- | --- | --- |
| TM-01 | Подмена DC/CA, downgrade LDAP | Доверенные endpoints, Kerberos и LDAPS/подписанный LDAP по утверждённой конфигурации, запрет bypass TLS | Windows: неправильный cert/endpoint отвергается; доменная trust compromise остаётся риском |
| TM-02 | Скрытая запись через cmdlet или CA API | Явный allowlist read operations, review каждого collector, запрет Set/Add/Remove и enrollment | Трасса лаборатории + контроль изменений до/после; текстовый поиск сам по себе недостаточен |
| TM-03 | JSON/LDAP имена вызывают команды или HTML injection | Без eval/Invoke-Expression, parameterized queries, escaping output, limits | Fixtures с кавычками, HTML, Unicode, oversized input; без исполнения содержимого |
| TM-04 | Утечка credential/topology в Git и логи | Integrated auth, отсутствие password inputs/logging, частное хранение, синтетические fixtures, review diff | Secret pattern check лишь дополнительный барьер; ручной review обязателен |
| TM-05 | Потеря evidence превращается в pass | Coverage и reasons обязательны, неизвестное сохраняется | Negative fixture missing evidence; Windows denied-read scenario |
| TM-06 | Перегрузка DC / массовая выборка | Scope allowlist, pagination, deadline, cancellation, throttling | Лабораторный нагрузочный тест; production запуск только после согласования |
| TM-07 | Подмена evidence/правил | Version/hash manifest, provenance, restricted storage, CI read-only permissions | Повреждённый bundle отклоняется; hash не доказывает честность источника |
| TM-08 | Кража избыточных прав оператора | Отдельная read account, endpoint hardening, запрет автоматического elevation | Проверка least privilege по источнику; Windows host остаётся доверенным |
| TM-09 | Supply-chain/PR вытягивает секреты | Нет secrets в public CI, pinned action SHA, stdlib-only сейчас, review зависимостей позже | PR workflow без private runners и credentials |
| TM-10 | Ложная уверенность в recovery | Отдельно документ/backup/успешное учение, возраст evidence | Recovery drill на изолированном стенде; аудитор лишь фиксирует подтверждение |

## Запреты и обработка инцидента

Не запрашивать DCSync, NTDS/SAM/LSASS, пароли gMSA, private keys CA, hashes и tickets. Не выполнять relay, coercion, password spraying, certificate enrollment, remote code deployment, policy edits или restore. При неожиданной записи, чтении секретного атрибута либо выходе за scope сбор останавливается; локальный журнал сохраняет только метаданные, владелец стенда расследует. При утечке в Git требуется ограничить доступ, отозвать credential и отдельно согласовать очистку истории; простого удаления файла недостаточно.

## Что ещё нужно подтвердить

Матрица read API и прав на Windows, поведение SD parsing, эффективность TLS/signing, влияние запроса на DC и корректность интерпретации AD CS пока не проверены. До evidence запрещено называть collector безопасным или готовым к production.

## MVP меры и остаточный риск

Offline CLI не имеет сетевого collector, команды remediation или dependency runtime. JSON размер/глубина/strings/arrays ограничены; strict keys/types и duplicate key rejection; diagnostic не включает входные значения. Evidence refs никогда не интерпретируются как путь/URL. Markdown экранирует HTML, markdown links и управляющие символы. Output O_EXCL/0600 на POSIX запрещает перезапись и input alias. Report не подтверждает истинность operator assertions; поддельные facts остаются риском, поэтому обязательны private evidence review и lab acceptance. Existence of SHA256 не равна подписи источника. TM-01/02/06/08 collector controls ещё не проверены на AD.
