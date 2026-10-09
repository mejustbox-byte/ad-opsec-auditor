# Инструкции следующих циклов GITHUB-OPSEC AD

- Вся документация, помощь CLI, описания схем/правил, шаблоны и release notes на русском. Команды, пути, ключи JSON, идентификаторы, enum и синтаксис кода не переводить. Стандартный исходный текст MIT сохранять в LICENSE; русское пояснение отдельно.
- README содержит полный индекс ARCHITECTURE, TECH-STACK, INSTALL, CONTRIBUTING, ROADMAP, SECURITY, CHANGELOG, THREAT-MODEL, CORE-CONTRACT, RUNBOOK, CLOUD-DEVELOPMENT, LOCAL-PC, VERIFICATION, RELEASE, RELEASE-CHECKLIST, RELEASE-NOTES, SUPPLY-CHAIN и LICENSE.ru.md. Существующие docs не удалять; команды/ссылки и смысл согласовывать.
- Использовать существующий checkout; каждая cloud задача изолирована. Worktree только по явному запросу. Проверять status и сохранять пользовательские изменения; не выполнять reset/clean для их удаления.
- Реализован автономный MVP, а не Windows collector. Синтетические проверки и hosted Windows Python CI не выдавать за live AD/AD CS/ACL/RSAT/effective policy/recovery validation. Непроверенное отмечать not_run / НЕ ВЫПОЛНЕНО.
- Реальные секреты, выгрузки инфраструктуры, keys, tickets и частные отчёты запрещены в публичном репозитории и CI. Не создавать платные ресурсы и не отключать TLS/подписи/хеши.
- Установка воспроизводится tools/install_environment.sh без сохранённого venv; зависимости закреплены requirements-dev.lock. Выполнять meaningful suite/schema/scan/build/installed smoke/repro, проверять фактическое число passed/failed/skipped и license inclusion.
- CI проверять по exact head/main commit. Перед выпуском проверить неизменный tag→commit, package version, существующий release ID, draft/prerelease, четыре uploaded assets, скачанные checksum и чистую установку. Пустой draft не считать выпуском. Старые теги/выпуски не переносить/удалять.
- Публикация assets — только разрешённый manual main Actions со штатным GITHUB_TOKEN и ограниченным job contents:write. Не извлекать credentials и не обходить локальную аутентификацию.
- install_script/start_skill среды сохранять на русском под фактическую версию и команды. Config draft, публикация snapshot пользователем и независимая проверка восстановления — разные состояния; сообщать только подтверждённое.
- Commit/push/PR/merge/release выполнять в рамках разрешения текущего пользователя; не наследовать произвольное разрешение на будущие релизы. Текущий цикл пользователем разрешён.
