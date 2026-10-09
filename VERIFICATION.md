# Проверенные результаты и непроверенные границы

## Исторический подтверждённый выпуск 0.1.0a1

Product commit `63579e76a7766c06dfc4626da683ad2db782d607`, [PR #1](https://github.com/mejustbox-byte/ad-opsec-auditor/pull/1), [CI merge commit](https://github.com/mejustbox-byte/ad-opsec-auditor/actions/runs/37924160724): Linux и Windows completed/success. Tag v0.1.0a1 сохранён. [PR #2](https://github.com/mejustbox-byte/ad-opsec-auditor/pull/2) добавил publisher, merge `45a2c46e89164069eb86ac0a1ec4d759832a0e21`. [Actions публикации](https://github.com/mejustbox-byte/ad-opsec-auditor/actions/runs/37925907853) completed/success; [release](https://github.com/mejustbox-byte/ad-opsec-auditor/releases/tag/v0.1.0a1) имеет draft=false/prerelease=true и четыре uploaded assets. Скачанные хеши сверены.

36 первоначальных локальных тестов без skipped, 1317 вариантов сверки Draft 2020-12, 12 audit запусков wheel/zipapp вне checkout, пересборка исходного архива и повторные hashes прошли. После publisher добавлены проверки release-gates. На Windows POSIX-only symlink/FIFO ожидаемо skipped; это не failed и не passed.

## Воспроизведение актуальной версии

Команды [разработки](docs/development.md) и [установки среды](CLOUD-DEVELOPMENT.md) используют фактический checkout. Suite дополнительно проверяет русский UTF-8, библиотечную композицию, список/ссылки документов и безопасный выбор release target. Сверка схемы, scan, build/smoke/repro должны пройти; число тестов фиксировать из вывода текущего запуска. Финальный CI/commit тега v0.1.0a2 и состояние assets проверяются в Actions/API при публикации, не выводятся из старого run.

## Явно НЕ ВЫПОЛНЕНО

Реальный Windows AD/AD CS/RSAT collector, effective ACL graph, protocol/GPO application, least-privilege safety, Windows Server 2019/2022/2025 matrix, backup/forest restore drill, новый независимо восстановленный cloud snapshot, независимый security audit. Ноль ошибок на synthetic не оценивает реальные ложные срабатывания или достаточность источников. Шаблонный secret scan не доказывает отсутствие всех секретов.

## Полнота документации

Индекс README покрывает общий комплект, указанный для sigma-ruleforge/autonomous-pentest-ai/modular-c2-framework/redblue-arena/honeypot-grid: архитектура/стек/установка/вклад/план/безопасность/история плюс угрозы/контракты/эксплуатация/облако/локальная приёмка/проверки/выпуск. Для структуры дополнительно прочитаны INSTALL/RUNBOOK honeypot-grid и VERIFICATION/MODULE-API redblue-arena. Их функции, uv/Docker/HTTP, числа тестов и результаты не перенесены в AD. Существующие docs сохранены и связаны; полнота проверяется по применимым разделам и командам, не объёму текста.
