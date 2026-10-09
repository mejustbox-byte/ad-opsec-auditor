# Контрольный список выпуска

1. Проверить checkout/пользовательские изменения и версию; документация/помощь/правила/схема/шаблоны на русском, ключи и ID сохранены. Проверить полный индекс и ссылки.
2. Запустить suite/schema/public scan/build/installed smoke/repro из [разработки](docs/development.md). Ручной анализ secrets и происхождения обязателен; реальные exports отсутствуют.
3. Дождаться CI Linux/Windows именно head PR; отделить expected skipped и real AD not_run. Слить PR и проверить main CI/merge SHA.
4. Создать новый tag v0.1.0a2 на финальном main SHA; подтвердить dereferenced SHA. Не менять v0.1.0a1. Убедиться в package0.1.0a2.
5. Создать единственный draft с русскими notes и prerelease=true; сохранить ID. Не дублировать release.
6. Запустить release.yml с main, конкретным tag/expected_commit/release_id. Build must success до publisher.
7. Проверить draft=false/prerelease=true, четыре uploaded assets, имена/размеры/digests, совпадение скачанных SHA256SUMS. Пустой draft не выпуск.
8. Проверить чистую установку скачанного wheel вне checkout, версию, safe/risky/incomplete и неверный ввод; zipapp и source archive также должны работать. Не считать это AD-стендом.
9. Зафиксировать ссылки PR/merge/CI/release и ограничения в сообщении пользователю; старый выпуск сохранён. install/start среды на русском, проверены без сохранённого venv и сохранены в draft.
10. Публикацию cloud snapshot выполняет пользователь в настройках, затем отдельная новая задача проверяет восстановление. До неё status НЕ ВЫПОЛНЕНО.

Неизменные запреты: новые credentials в Git, реальные infrastructure exports, отключение TLS/хешей, платные ресурсы и выдуманные лабораторные результаты.
