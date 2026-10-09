# Установка и запуск v0.1.0a1

Требуется Python 3.12. Инструмент не подключается к AD и не требует credential. Все bundled examples synthetic. Реальные snapshots хранить и анализировать только в частной среде; не загружать их в public GitHub или этот cloud workspace.

## Из исходников

```sh
python3 -m ad_opsec_auditor --version
python3 -m ad_opsec_auditor schema > snapshot.schema.json
python3 -m ad_opsec_auditor validate examples/safe.synthetic.json
python3 -m ad_opsec_auditor audit examples/risky.synthetic.json --format markdown
```

Risky example ожидаемо возвращает exit 1. Exit codes: 0 = validate success / audit all pass; 1 = audit has fail; 2 = invalid input/arguments/I/O; 3 = no fail, but unknown/not_run. Validate не оценивает безопасность и не обещает audit exit 0. Пустой/неполный snapshot валиден, но отсутствующие checks имеют not_run; missing facts/evidence и partial coverage дают unknown.

## Из prerelease artifacts

Скачать wheel, zipapp и SHA256SUMS со страницы GitHub Release, проверить sha256 (Unix `sha256sum -c SHA256SUMS`, Windows `Get-FileHash -Algorithm SHA256`). Проверить, что выбран именно нужный version и commit; checksums не удостоверяют автора.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ad_opsec_auditor-0.1.0a1-py3-none-any.whl
.venv/bin/ad-opsec-auditor --version
.venv/bin/ad-opsec-auditor audit examples/safe.synthetic.json --format json --output report.json
python3 ad-opsec-auditor-0.1.0a1.pyz audit examples/safe.synthetic.json --format markdown
```

Windows: `py -3.12 -m venv .venv`, затем `.venv\Scripts\python.exe -m pip install --no-index --no-deps ...` и `.venv\Scripts\ad-opsec-auditor.exe ...`. Wheel/zipapp не включают examples; получить их из source archive или checkout release tag. Destination --output создаётся эксклюзивно; существующий файл, symlink и директория отвергаются. Parent должен существовать. При stdout данные идут только туда; диагностические сообщения без входных значений — в stderr.

## Вход и доверие

См. [контракт](input-contract.md), опубликованную [JSON Schema](../schemas/snapshot-v1.schema.json) и примеры. Evidence — логические записи с ID, source, UTC timestamp и description. Их тексты не исполняются, paths/URL не открываются. Автор snapshot отвечает за истинность, достаточность и scope evidence. Анализатор обнаруживает structural errors и missing coverage, но не ложь в аттестации.

Pass означает соответствие конкретному baseline по заявленным facts, не «лес безопасен». Fail содержит severity, confidence, failed predicates и remediation. Unknown означает недостаточность evidence, not_run — сбор не запускался. Report включает hash точных input bytes и версии engine/rules; он детерминирован и не использует текущее время.

## Лабораторная проверка

Все реальные Windows AD проверки сейчас not_run. Следовать [lab runbook](lab.md) для isolated Windows testing. Native collector отсутствует; сначала lab owner вручную подтверждает facts и готовит private normalized snapshot. CLI результаты сверяются с независимыми наблюдениями. Synthetic/hosted Windows tests не считаются laboratory acceptance.
