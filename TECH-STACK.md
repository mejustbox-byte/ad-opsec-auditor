# Стек и закреплённые версии

## Выбранные средства

Python 3.12 (облако 3.12.14, CI использует ветку 3.12), стандартные json/unittest/argparse/hashlib. Во время работы внешних зависимостей нет. Требование пакета >=3.12,<3.13 закреплено в pyproject.toml; .python-version содержит 3.12. Проверены Linux x86_64 и Windows x64 в hosted CI, другие платформы отдельно не подтверждены.

JSON Schema Draft 2020-12, схема v1 из schema.py, набор правил baseline-v1. Схема встроена в пакет и опубликована отдельно. Эталонная jsonschema используется только при разработке, не при анализе.

| Средство сборки/проверки | Версия |
| --- | --- |
| setuptools | 80.9.0 |
| wheel | 0.45.1 |
| build | 1.2.2.post1 |
| packaging | 25.0 |
| pyproject-hooks | 1.2.0 |
| jsonschema | 4.25.1 |
| attrs | 25.3.0 |
| jsonschema-specifications | 2025.9.1 |
| referencing | 0.36.2 |
| rpds-py | 0.27.1 |
| typing-extensions | 4.15.0 |
| colorama (Windows) | 0.4.6 |

[requirements-dev.lock](requirements-dev.lock) содержит версии и SHA256 официальных wheels; установка --only-binary=:all: --require-hashes. Lock проверен для Python 3.12 Linux/Windows x86_64. Обновление требует пересборки, проверки схемы, установки и CI, без отключения TLS или изменения ожидаемых хешей ради прохождения.

## Обоснование и альтернативы

Стандартная библиотека уменьшает поверхность зависимостей и позволяет частный автономный запуск. JSON разделяет сбор и анализ; Python обеспечивает переносимые тесты. Предпочтён wheel для установки, zipapp для запуска без pip; исходный архив содержит документацию и тесты. [ADR-0001](docs/adr/0001-stack.md) и [ADR-0002](docs/adr/0002-offline-mvp.md) рассматривают PowerShell/C# и Python LDAP.

Windows PowerShell 5.1/RSAT относятся только к проекту будущего сборщика, не к установленным зависимостям MVP. CI Actions закреплены по SHA, штатный GITHUB_TOKEN ограничен job публикации. Docker, uv, Ruff, HTTP-сервер и инфраструктурный стек чужих проектов сюда не перенесены.
