# Цепочка поставок и реестр лицензий

## Собственный код

ad-opsec-auditor: MIT, [исходный текст](LICENSE), [русское пояснение](LICENSE.ru.md). Атрибуция: участники проекта GITHUB-OPSEC ad-opsec-auditor, 2026. Метаданные package License-Expression=MIT; LICENSE и LICENSE.ru.md включаются и сравниваются в wheel/исходном архиве/zipapp. Исторические assets v0.1.0a1 не перепаковываются.

Во время работы используются только Python 3.12 и его стандартная библиотека (лицензия PSF и связанные уведомления поставки Python). Наши wheel/zipapp не включают интерпретатор Python или сторонние библиотеки; это не освобождает поставщика Python от своих уведомлений.

## Инструменты разработки, не включаемые в runtime wheel

| Зависимость | Версия | Лицензия |
| --- | --- | --- |
| setuptools | 80.9.0 | MIT |
| wheel | 0.45.1 | MIT |
| build | 1.2.2.post1 | MIT |
| packaging | 25.0 | Apache-2.0 OR BSD-2-Clause |
| pyproject-hooks | 1.2.0 | MIT |
| jsonschema | 4.25.1 | MIT |
| attrs | 25.3.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| referencing | 0.36.2 | MIT |
| rpds-py | 0.27.1 | MIT |
| typing-extensions | 4.15.0 | PSF-2.0 |
| colorama (Windows) | 0.4.6 | BSD-3-Clause |

Версии/SHA256: [lock](requirements-dev.lock), зависимости сборки: [pyproject](pyproject.toml). Лицензии сверяются по upstream METADATA/LICENSE; исходные поставки находятся на https://pypi.org/. Это реестр текущего набора, не юридическая гарантия всех будущих обновлений. При добавлении/обновлении проверить прямые/транзитивные версии, хеши, лицензии, включение уведомлений и безопасную установку.

GitHub Actions checkout/setup-python/upload-artifact/download-artifact закреплены SHA в workflow; исходные лицензии MIT находятся в соответствующих публичных repositories actions/*. Они не встраиваются в runtime package. GitHub CLI используется только инфраструктурой публикации, не пользовательским анализатором.

## Целостность и меры

Официальный HTTPS, TLS и --require-hashes/--only-binary сохранены. Не изменять ожидаемый SHA, чтобы принять повреждённый файл. CI не получает частных данных; publisher token временный с job contents:write. Новых secrets нет. Тег/commit/package version проверяются перед сборкой, asset state/digest и скачанные SHA256 — до/после публикации. Хеш не подпись автора и не независимый аудит цепочки поставок.

Шаблонный scan дополняет ручной анализ; supply-chain compromise, скомпрометированный maintainer/host и ложная аттестация источника остаются рисками. [Контроли](THREAT-MODEL.md), [условия выпуска](RELEASE-CHECKLIST.md). Приватные уязвимости не публиковать с действующими secrets; [процесс сообщения](SECURITY.md).
