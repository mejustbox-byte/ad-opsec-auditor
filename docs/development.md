# Разработка, проверки и сборка

Python 3.12. Использовать существующий checkout `/workspace/ad-opsec-auditor`; облачная задача изолирована, worktree не нужен без явного запроса. Основные тесты и запуск из исходников не требуют внешних пакетов.

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

На Windows использовать `.venv\Scripts\python.exe`. Инструменты сборки/проверки закреплены по версиям и SHA256; зависимости во время работы отсутствуют. Сборка wheel/исходного архива с --no-isolation, вывод только в ignored dist/build. Нормализованные метаданные обеспечивают повторяемость. Проверяется установка вне checkout, zipapp, пересборка из архива и повторные хеши. В исходный архив входят документация, тесты, схема и примеры, не частные данные.

CI запускает эти проверки на Ubuntu и Windows с read-only token и закреплёнными SHA Actions. Реальные данные, secrets, частные runners и pull_request_target не используются. Windows CI проверяет автономный Python, не AD; POSIX-only тест symlink/FIFO ожидаемо пропускается на Windows. Лабораторные проверки остаются not_run.

Публикация: [Actions workflow](release-workflow.md). Реальные файлы инфраструктуры и секреты запрещены; проверка шаблонов дополняет обязательный ручной анализ. Пользователь разрешил реализацию/PR/merge/release, но не изменение AD и платные ресурсы. Документация и пользовательские тексты на русском, ключи/команды/пути/ID сохраняются. UTF-8 задаётся явно.
