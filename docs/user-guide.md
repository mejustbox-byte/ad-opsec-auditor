# Установка и использование 0.1.0a2

Требуется Python 3.12. CLI не подключается к AD и не требует учётных данных. Примеры синтетические. Реальные снимки разрешены только в утверждённой частной среде, не в публичном GitHub или этом облачном workspace.

## Из исходников

```sh
python3 -m ad_opsec_auditor --version
python3 -m ad_opsec_auditor schema > snapshot.schema.json
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/risky.synthetic.json --format markdown
```

Рискованный пример ожидаемо возвращает 1. Коды: 0 — успешная validate или все результаты audit равны pass; 1 — есть fail; 2 — неверный ввод/аргументы/ошибка файла; 3 — нет fail, но есть unknown/not_run. Validate подтверждает структуру, не безопасность. Отсутствующая проверка даёт not_run; неполное покрытие, отсутствующие факты или свидетельства дают unknown.

## Из артефактов предварительного выпуска

Со страницы GitHub Release v0.1.0a2 скачать wheel, исходный архив, zipapp и SHA256SUMS в один каталог. Проверить `sha256sum -c SHA256SUMS`; на Windows сравнить `Get-FileHash -Algorithm SHA256` с manifest. Выбранный тег/commit проверять отдельно: хеши не удостоверяют автора.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ad_opsec_auditor-0.1.0a2-py3-none-any.whl
python3 -m tarfile -e ad_opsec_auditor-0.1.0a2.tar.gz .
.venv/bin/ad-opsec-auditor --version
.venv/bin/ad-opsec-auditor audit ad_opsec_auditor-0.1.0a2/examples/safe.synthetic.json --format markdown
python3 ad-opsec-auditor-0.1.0a2.pyz audit ad_opsec_auditor-0.1.0a2/examples/risky.synthetic.json --format json
```

Windows: `py -3.12 -m venv .venv`, `.venv\Scripts\python.exe` и `.venv\Scripts\ad-opsec-auditor.exe`. Wheel и zipapp содержат код и схему; примеры находятся в исходном архиве. Тексты помощи/Markdown записываются в UTF-8, JSON сохраняет русские строки с корректным стандартным экранированием.

`--output NEW_FILE` создаёт только новый файл. Существующие файлы, symlink и директории отвергаются; родительский каталог должен существовать. Вход не перезаписывается. Без --output отчёт идёт в stdout; безопасная диагностика — в stderr.

## Контракт и ограничения

[Контракт](input-contract.md), [схема](../schemas/snapshot-v1.schema.json), [лаборатория](lab.md). Свидетельства — ID, источник, время UTC и краткое описание. Их текст не исполняется, пути/URL не открываются. Оператор отвечает за истинность, достаточность и область данных; анализатор проверяет структуру и полноту заявленных полей, а не истинность аттестации.

Pass означает соответствие baseline-v1 по заявленным фактам. Fail содержит критичность, уверенность, нарушенные условия и рекомендации. Unknown означает нехватку данных; not_run — отсутствие запуска сбора. Отчёт включает SHA256 точных входных байтов и версии; результат детерминирован и не использует текущее время. Проверки реальной инфраструктуры пока not_run; сборщик не поставляется.
