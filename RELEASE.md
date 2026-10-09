# Выпуск и артефакты

AD package 0.1.0a2 соответствует tag v0.1.0a2, не Linux-specific v0.1.0-alpha.2. Старый v0.1.0a1 сохранён. Пока нет реальной AD-приёмки, выпуск prerelease. [Примечания](RELEASE-NOTES.md), [контроль](RELEASE-CHECKLIST.md).

После PR/CI финальный main SHA становится источником неизменного тега. Штатный API один раз создаёт draft нового тега с русским описанием. [Workflow](.github/workflows/release.yml) получает tag, expected_commit и release_id; сборка использует конкретный тег, publisher — проверенный workflow commit main. Он не создаёт release и не меняет тег.

Build job contents:read: проверка commit/версии, закреплённые зависимости, suite/schema/scan, wheel/sdist/zipapp, installed smoke/repro/SHA256SUMS. Publisher job contents:write: точный набор четырёх files, существующий release ID/tag/prerelease, загрузка только отсутствующих assets, API state/digest и скачанные hashes до публикации, patch draft=false, повторная проверка после. Стандартный ephemeral GITHUB_TOKEN передаётся только publish step; новые credentials и локальный обход 401 отсутствуют.

Поставляются ad_opsec_auditor-0.1.0a2-py3-none-any.whl, ad_opsec_auditor-0.1.0a2.tar.gz, ad-opsec-auditor-0.1.0a2.pyz, SHA256SUMS. Контрольные суммы подтверждают сравнение целостности, не подпись владельца. Стандартные исходные архивы GitHub доступны дополнительно. [Установка/удаление](INSTALL.md).

Повторная публикация существующего выпуска только проверяет assets. При несовпадении или частичной загрузке job останавливается; не перезаписывать/удалять чужие файлы. После диагностики повторить тот же разрешённый workflow с тем же tag/commit/release ID. [Подробный процесс](docs/release-workflow.md). Environment Publish и GitHub release независимы.
