# MVP v0.1.0a1: offline evidence auditor

## Принятое направление

Первый пригодный prerelease анализирует нормализованный JSON snapshot локально, без сети, AD API, secrets и исправления инфраструктуры. Это полезный evidence triage и policy review, не автоматический live scanner. Input facts готовит оператор по лабораторной инструкции; auditor проверяет их структуру и согласованность, но не удостоверяет истинность источника.

## Объём выпуска

1. Версионированная schema, строгие типы, запрет неизвестных полей, duplicate JSON keys, non-finite values, лимиты размера/глубины/числа объектов.
2. Девять правил по матрице: Tier 0, AD CS, ACL, сервисные учётные записи, NTLM, LDAP, SMB, logging, forest recovery. Каждое выдаёт pass/fail/unknown/not_run, evidence, severity, confidence и remediation.
3. CLI validate/audit/schema, JSON и escaped Markdown, детерминированные результаты, hash входного файла, явно synthetic/live-unverified labels.
4. Полные и неполные синтетические примеры, negative fixtures, unit и CLI integration, install/build smoke tests, Linux и Windows hosted CI только на synthetic данных.
5. Hash-pinned build dependencies, wheel/sdist/portable zipapp и SHA256SUMS, PR и prerelease если платформа позволяет.

## Deferred и release gates

Native Windows collector, raw ACL effective access graph, CA endpoint interrogation, применение GPO, authentication/channel tests и recovery drills не реализуются в этом MVP. Никакого claim об их успешности. Windows AD laboratory gate = not_run до настоящего evidence, даже если hosted Windows Python tests пройдут. Full stable release требует trusted collector и лабораторного safety review. Отсутствие API permission блокирует PR/merge/release, но не локальную реализацию, build или Git push.

## Критерии приёмки

Для каждого правила есть safe/risky/missing evidence tests. Missing или partial coverage не дают pass. Неверный ввод получает exit 2 без traceback/эхо данных. Audit выдаёт exit 1 при fail, exit 3 при unknown/not_run без fail, exit 0 только при всех pass. Не перезаписывает файлы или вход. Релиз публикуется только после всех доступных local/remote checks; unavailable checks перечисляются отдельно.
