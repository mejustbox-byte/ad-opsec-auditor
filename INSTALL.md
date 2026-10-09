# Установка, проверка и удаление

## Предпосылки

Python 3.12 и доступ к выбранному выпуску GitHub. CLI не требует AD, RSAT, secrets или сети во время анализа. Реальные данные допускаются только в частной среде. [Стек](TECH-STACK.md), [безопасность](SECURITY.md).

## Wheel: POSIX

Скачать четыре assets v0.1.0a2 в один каталог и проверить SHA256SUMS. Wheel/zipapp не содержат примеры; они находятся в исходном архиве.

```sh
sha256sum -c SHA256SUMS
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ad_opsec_auditor-0.1.0a2-py3-none-any.whl
python3 -m tarfile -e ad_opsec_auditor-0.1.0a2.tar.gz .
.venv/bin/ad-opsec-auditor --version
.venv/bin/ad-opsec-auditor validate ad_opsec_auditor-0.1.0a2/examples/safe.synthetic.json
.venv/bin/ad-opsec-auditor audit ad_opsec_auditor-0.1.0a2/examples/safe.synthetic.json --format markdown
```

Ожидается версия 0.1.0a2, exit 0 и девять синтетических pass. Это не AD-проверка. Из другого каталога использовать абсолютный путь к примеру.

## Wheel: Windows PowerShell

Сначала сравнить `Get-FileHash -Algorithm SHA256` каждого файла с SHA256SUMS. Сравнение включает точное имя и все 64 символа хеша.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --no-index --no-deps ad_opsec_auditor-0.1.0a2-py3-none-any.whl
py -3.12 -m tarfile -e ad_opsec_auditor-0.1.0a2.tar.gz .
.venv\Scriptsd-opsec-auditor.exe --version
.venv\Scriptsd-opsec-auditor.exe validate ad_opsec_auditor-0.1.0a2\examples\safe.synthetic.json
.venv\Scriptsd-opsec-auditor.exe audit ad_opsec_auditor-0.1.0a2\examples\safe.synthetic.json --format markdown
```

Тексты UTF-8; на Windows частный родительский каталог должен иметь утверждённый ACL. POSIX режим 0600 не является гарантом ACL Windows. Hosted Windows CI проверяет установку/CLI, не настоящий AD-стенд.

## Исходники и переносимый запуск

```sh
git clone --branch v0.1.0a2 https://github.com/mejustbox-byte/ad-opsec-auditor.git
cd ad-opsec-auditor
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m unittest discover -s tests -v
```

Для установки из исходников сначала создать venv, установить закреплённые инструменты командой `python -m pip install --only-binary=:all: --require-hashes -r requirements-dev.lock`, затем из корня `python -m pip install --no-index --no-deps --no-build-isolation .`. Использовать Python созданного venv (на POSIX .venv/bin/python, на Windows .venv\Scripts\python.exe). Проверка схемы и сборки: [разработка](docs/development.md).

Без pip: `python3 ad-opsec-auditor-0.1.0a2.pyz audit PATH_TO_SNAPSHOT --format markdown`. Подставить частный файл либо синтетический пример из исходного архива. [Коды выхода и ошибки](RUNBOOK.md).

## Обновление и удаление

Перед обновлением сохранить частные отчёты вне checkout, проверить новый тег/хеши и создать отдельный venv. Не менять существующие теги. Для удаления пакета: `python -m pip uninstall ad-opsec-auditor` через Python его venv; zipapp удалить как обычный файл после проверки владельца. Удаление пакета не удаляет отчёты, снимки или лабораторию; их удаление по согласованному сроку хранения выполняет владелец. Не использовать массовый reset/clean для чужих файлов.
