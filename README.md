# ad-opsec-auditor

Аудитор состояния безопасности Microsoft Active Directory: Tier 0, AD CS, ACL и делегирование, сервисные учётные записи, NTLM/LDAP/SMB, журналирование и готовность восстановления леса. Работает автономно и только чтением нормализованных свидетельств.

**0.1.0a2 — предварительный выпуск автономного анализатора, а не сборщик данных из AD.** Синтетические примеры и CI не проверяют реальную инфраструктуру. Все реальные проверки Windows AD пока **not_run**. CLI не использует учётные данные, сеть, эксплуатацию уязвимостей или команды изменения инфраструктуры.

## Быстрый запуск

Требуется Python 3.12; внешних зависимостей во время работы нет.

```sh
python3 -m ad_opsec_auditor --version
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/safe.synthetic.json --format markdown
python3 -m ad_opsec_auditor audit examples/risky.synthetic.json --format json
python3 -m unittest discover -s tests -v
```

Безопасный пример возвращает 0, рискованный — 1, неполный — 3; неверный ввод и ошибки файлов — 2. JSON и Markdown содержат свидетельства, критичность, уверенность, причины и рекомендации. Существующие файлы отчётов не перезаписываются. Реальные выгрузки инфраструктуры и секреты запрещены в публичном репозитории и CI.

- [Установка и использование](docs/user-guide.md)
- [Контракт входных данных и правила](docs/input-contract.md), [схема JSON](schemas/snapshot-v1.schema.json)
- [Требования](docs/requirements.md), [модель угроз](docs/threat-model.md), [архитектура](docs/architecture.md)
- [Матрица проверок](docs/check-matrix.md), [план MVP](docs/mvp-plan.md), [Windows-стенд](docs/lab.md)
- [ADR-0001](docs/adr/0001-stack.md), [ADR-0002](docs/adr/0002-offline-mvp.md)
- [Разработка и CI](docs/development.md), [публикация через Actions](docs/release-workflow.md)
- [История изменений](CHANGELOG.md), [безопасность](SECURITY.md), [вклад в проект](CONTRIBUTING.md)

Тег нового выпуска AD — `v0.1.0a2`, версия пакета — `0.1.0a2`. Старый `v0.1.0a1` не изменяется. Артефакты: wheel, исходный архив, переносимый Python zipapp и SHA256SUMS. Результат pass означает соответствие конкретному набору правил по заявленным данным; это не гарантия безопасности леса или успешного восстановления.

## Полный индекс документации

| Раздел | Самостоятельный документ |
| --- | --- |
| Компоненты и поток данных | [ARCHITECTURE](ARCHITECTURE.md) |
| Обоснование и версии/lock | [TECH-STACK](TECH-STACK.md) |
| Wheel/source/Windows/POSIX/удаление | [INSTALL](INSTALL.md) |
| Разработка и review | [CONTRIBUTING](CONTRIBUTING.md) |
| Этапы и критерии приёмки | [ROADMAP](ROADMAP.md) |
| Безопасность и данные | [SECURITY](SECURITY.md) |
| Контроли и остаточные риски | [THREAT-MODEL](THREAT-MODEL.md) |
| CLI/JSON/библиотека/расширение правил | [CORE-CONTRACT](CORE-CONTRACT.md) |
| Эксплуатация и ошибки | [RUNBOOK](RUNBOOK.md) |
| Воспроизводимая среда и восстановление | [CLOUD-DEVELOPMENT](CLOUD-DEVELOPMENT.md) |
| Локальный ПК и отдельный AD-стенд | [LOCAL-PC](LOCAL-PC.md) |
| Проверенные результаты и НЕ ВЫПОЛНЕНО | [VERIFICATION](VERIFICATION.md) |
| Процесс выпуска | [RELEASE](RELEASE.md) |
| Контроль tag/assets/clean install | [RELEASE-CHECKLIST](RELEASE-CHECKLIST.md) |
| Русские примечания выпуска | [RELEASE-NOTES](RELEASE-NOTES.md) |
| История | [CHANGELOG](CHANGELOG.md) |

Исходные подробные docs/требования/ADR/матрица/стенд сохранены и перечислены выше. Корневые документы — удобные самостоятельные руководства; при изменении контракта/команд оба представления обновляются вместе.

Лицензия: [MIT](LICENSE), [русское пояснение](LICENSE.ru.md). [Цепочка поставок и реестр лицензий](SUPPLY-CHAIN.md), [инструкции следующих циклов](AGENTS.md).
