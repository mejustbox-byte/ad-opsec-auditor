# Проверка среды и offline MVP

Дата: 2026-10-09. Checkout `/workspace/ad-opsec-auditor`, репозиторий mejustbox-byte/ad-opsec-auditor. `/workspace/onboarding` отсутствует и не требуется.

## Исходное состояние

HEAD `130bde69f31fd82a498ee8fe49a7c17edb1e45b2` совпал с удалённым main. В cloud checkout ветка называлась work. Подготовленные документы были локальными, а исходный commit содержал только README. Документы сохранены и актуализированы под разрешённую реализацию. Работа ведётся в feat/offline-auditor-mvp без reset или worktree.

## Доступные проверки

- Python 3.12.14; runtime dependencies отсутствуют.
- 36 unit/documentation/CLI integration tests: passed на Linux, без skipped.
- 1317 структурных variants: agreement встроенного валидатора с jsonschema Draft 2020-12.
- Public-file guard, fixture provenance review и git diff --check: passed. Реальные credentials/exports не использовались.
- Wheel и zipapp запущены из временной директории вне checkout: version/schema, safe/risky/incomplete JSON и Markdown (12 audit invocations) passed.
- Wheel из sdist совпал с canonical wheel; повторные wheel/sdist/zipapp hashes совпали. ZIP и tar metadata нормализованы, runtime signing не заявляется.
- Native Git read работает через платформенный HTTPS proxy. GitHub API ранее давал network 403 и единичный 401; после добавления api.github.com/uploads.github.com metadata/PR-list requests успешно выполняются. GitHub MCP tools в этой задаче отсутствуют; credentials не извлекались.
- Live Windows AD/AD CS/RSAT/ACL, effective protocol policies и recovery drill: **not_run**. Collector не поставляется. Hosted Windows CI проверяет только offline Python, не AD.

## Повторная настройка без сохранённого venv

Cloud install script — [tools/install_environment.sh](../tools/install_environment.sh). Из checkout выполнить `bash tools/install_environment.sh`. Он создаёт `/workspace/.ad-opsec-auditor-dev` из системного Python 3.12, устанавливает только hash-pinned build/test tools, выполняет suite/schema/public guard, сборку, smoke и reproducibility, затем ставит wheel без внешних runtime dependencies и проверяет installed CLI. Не нужен прежний .venv, /workspace/onboarding, secrets или running services. Повторный запуск сохраняет source и user files; отчёт smoke перезаписывается только в task-owned /tmp файле.

Для обычного local development см. [development](development.md), для artifact install — [user guide](user-guide.md). start_skill среды должен использовать установленный CLI и текущие product tests, без прежнего docs-only запрета. Сохранение config draft не является публикацией. Review/save в настройках среды и Publish / «Опубликовать среду» выполняет пользователь. GitHub PR/merge/release независимы от environment snapshot; их результат подтверждается ссылками GitHub, а не этим документом.
