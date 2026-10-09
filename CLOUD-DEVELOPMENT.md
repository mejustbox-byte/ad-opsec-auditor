# Облачная разработка и снимок среды

## Воспроизводимая установка

Существующий checkout `/workspace/ad-opsec-auditor`, Python 3.12. Каждая задача изолирована; worktree без явного запроса не нужен. Проверить git status и сохранить пользовательские изменения. Реальные exports/credentials в облаке запрещены.

```sh
cd /workspace/ad-opsec-auditor
bash tools/install_environment.sh
```

Скрипт создаёт `/workspace/.ad-opsec-auditor-dev` заново при отсутствии, ставит hash-pinned tooling, проверяет тесты/схему/публичные файлы, сборку, установку, повторяемость, затем актуальный wheel и installed CLI. Сохранённый venv, отдельный onboarding каталог, services или secrets не нужны. Повторный запуск использует те же команды; пользовательские source-файлы не удаляются. Пишутся только ignored build/dist/egg-info, venv и собственный /tmp отчёт.

## Сохранение и публикация

install_script хранит полный проверенный скрипт, start_skill — русские инструкции запуска/проверок. Network draft сохраняет только нужные домены GitHub API/uploads/логов с сохранением иных правил; credentials не добавляются. Git read/write и API использовать через штатную платформенную аутентификацию. Локальный upload 401 не обходится: assets публикует [Actions](RELEASE.md).

Сохранение draft не выполняет код и не публикует snapshot. Пользователь проверяет/сохраняет настройки и нажимает Publish / «Опубликовать среду». Процессы не переживают snapshot, но текущий CLI сервисов не имеет. Публикация GitHub release независима от публикации среды.

## Проверка восстановленной задачи

После публикации открыть новую задачу, проверить фактический checkout/HEAD и версию, выполнить install script при отсутствующем venv, suite, check_schema.py, scan_public.py и installed CLI на safe/risky/incomplete. Проверить реальные числа passed/failed/skipped/not_run, clean git status и отсутствие приватных данных. Эта новая независимая проверка восстановления пока **НЕ ВЫПОЛНЕНО**; текущая fresh-venv установка её не заменяет. [История проверки среды](docs/environment-validation.md).
