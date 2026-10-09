# Разработка, CI и данные

Использовать существующий checkout `/workspace/ad-opsec-auditor`; cloud task изолирован, worktree не нужен. Python 3.12. Source запуск и основная suite не требуют внешних пакетов:

```sh
python3 -m unittest discover -s tests -v
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/safe.synthetic.json --format markdown
```

## Полная воспроизводимая проверка

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: --require-hashes -r requirements-dev.lock
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_schema.py
.venv/bin/python tools/scan_public.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/smoke_artifacts.py
.venv/bin/python tools/check_reproducible.py
```

На Windows использовать `.venv\Scripts\python.exe`. Все package pins/hashes находятся в lock; нет runtime dependencies. Build script пишет только ignored dist/ и build/. Сборка wheel/sdist через pinned build backend с --no-isolation. Одинаковый source и SOURCE_DATE_EPOCH дают повторяемые artifacts; проверка повторной сборки сравнивает hashes. Source archives включают документы/tests/schema/examples, но не private-data/reports.

CI: `.github/workflows/ci.yml`, push/pull_request/workflow_dispatch; hosted Ubuntu/Windows, Python 3.12, read-only token, immutable action SHA, без secret bindings/private runners. Выполняет suite, reference schema check, public-file scan, build, installed wheel/zipapp smoke. Hosted Windows здесь тестирует Python CLI, **не AD**. Релиз выполняется после CI по exact commit, сборки и smoke tests. Не использовать pull_request_target или production exports в CI.

Публично допустимы только вручную созданные synthetic fixtures. Реальные exports, keys, credential, event payloads и production topology запрещены; в этой cloud задаче они не используются. Private report хранить вне checkout с ACL/шифрованием и retention. `.gitignore` и pattern scanner — вспомогательные барьеры; ручной diff review остаётся обязательным.

См. [MVP](mvp-plan.md), [user guide](user-guide.md), [лабораторию](lab.md), [релизные ограничения](../CHANGELOG.md). Пользователь разрешил commit/push/PR/merge/release; прежний запрет документационного этапа отменён. Изменение AD и создание платных ресурсов не разрешено.
