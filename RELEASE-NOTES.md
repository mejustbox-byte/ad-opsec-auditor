# Примечания к 0.1.0a2

Предварительный выпуск автономного аудитора Microsoft AD. Tag v0.1.0a2, package0.1.0a2; старый v0.1.0a1 сохраняется. Русские документация, помощь CLI, описания правил/схем, отчёты и шаблоны. UTF-8 явно задан на Windows/POSIX. JSON ключи/enum, команды и baseline-v1 совместимы.

Девять проверок нормализованных фактов, evidence/severity/confidence/remediation, pass/fail/unknown/not_run, deterministic JSON/Markdown и SHA256 входа. Нет сети, credentials, эксплуатации или изменения AD. Добавлена безопасная библиотечная композиция audit_bytes. Публикация через штатный Actions проверяет immutable source и четыре скачанных assets до/после публикации.

Артефакты: wheel, исходный архив, переносимый zipapp, SHA256SUMS. Python 3.12, без внешних runtime dependencies. [Точные команды](INSTALL.md), [фактические контракты](CORE-CONTRACT.md), [проверки](VERIFICATION.md).

**НЕ ВЫПОЛНЕНО:** реальные AD/AD CS/RSAT, полный ACL graph, применение GPO/протокольных политик, минимальные права будущего сборщика, Windows Server compatibility, реальный forest recovery drill, независимая проверка нового cloud snapshot. Сборщик не поставляется; hosted Windows CI и synthetic не заменяют эти проверки. Риск AD CS узкий, пороги logging/recovery 30/180 дней — политика проекта, не универсальное соответствие Microsoft.

Публикация считается подтверждённой только фактическим GitHub release draft=false/prerelease=true с assets и checksum; этот документ описывает состав, не подменяет результат API/Actions. Чувствительные данные разрешены только в утверждённой частной среде, не в public Git/CI.
