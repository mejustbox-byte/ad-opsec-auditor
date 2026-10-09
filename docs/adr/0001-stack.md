# ADR-0001: Windows collection, offline analysis и проверки документации

Дата: 2026-10-09. Статус: историческое решение подготовки, дополнено ADR-0002 для offline prerelease.

## Контекст

Сначала определены требования, модель угроз, архитектура, check matrix и стенд. Нужны native AD security descriptors/RSAT, отсутствие эксплуатации, offline reproducibility и чёткая граница между Linux и Windows. Исходный репозиторий содержит только README, навязанный стек отсутствует.

## Решение

Будущий collector: Windows PowerShell 5.1 с RSAT ActiveDirectory/GroupPolicy и явно ограниченными .NET Windows API для необходимых read-only источников. Причина: доступ к integrated authentication и административным read-модулям на management host. AD CS, effective policy и event reads требуют отдельного прототипа и разрешений; наличие RSAT не доказывает их готовность. Не обещаем, что все cmdlets работают в PowerShell 7 или Linux. PowerShell 5.1 — native Windows runtime; scripts должны избегать dynamic execution и иметь safety review.

Будущий offline analyzer: Python 3.12, versioned JSON и чистые правила без сетевого доступа. Причина: переносимость Linux/Windows, stdlib JSON, unittest, удобные synthetic fixtures. Python не выполняет live AD collection. HTML UI, БД, daemon и контейнеры сейчас не нужны.

Текущий этап: Python 3.12 stdlib-only, `python3 -m unittest discover -s tests -v`, без pip install и сетевых dependency downloads. Public CI запускает только документационные/fixture contract checks с read-only token; actions pinned по immutable commit. Внешние Python пакеты и Pester пока не устанавливаются. При реализации Windows test stack добавится отдельным ADR с version pin, lock/hashes, лицензиями и доверенным способом установки.

## Альтернативы

C#/.NET collector: сильные типы и Windows APIs, но компиляция/дистрибуция и большая стартовая сложность; пересмотреть если PowerShell API или производительность не подходят. PowerShell для всей offline обработки: единый язык, но Windows-specific module boundaries и cross-platform тесты сложнее. Python LDAP collector: переносим, но не покрывает Windows policy/event semantics и integrated auth без дополнительных библиотек; не выбран. Offensive tooling: не подходит запрету эксплуатации и secret access.

## Последствия

Два runtime и явный schema boundary; требуется contract validation, версии модулей в evidence и Windows lab. Read-only гарантируется проверкой API и стендом, а не языком. Сейчас установлен только необходимый Linux runtime; Windows dependencies отмечены not_run, не считаются установленными. Нет утверждения о готовом продукте или пройденных AD tests.

Реализация и выпуск теперь разрешены пользователем; актуальные runtime/build решения: [ADR-0002](0002-offline-mvp.md). Исходные ограничения текущего этапа выше описывают предыдущую подготовку, а не запрет работы.
