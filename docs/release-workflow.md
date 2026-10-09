# Публикация существующего prerelease через Actions

Первый релиз: существующий draft ID `407852541`, tag `v0.1.0a1`, immutable product commit `63579e76a7766c06dfc4626da683ad2db782d607`. Тег не передвигается; новый release не создаётся. Local uploads.github.com вернул 401, поэтому публикация использует штатный ephemeral GITHUB_TOKEN только на hosted Actions.

Workflow [release.yml](../.github/workflows/release.yml) запускается вручную с main после отдельного PR и CI. Build job contents:read проверяет tag/HEAD SHA, устанавливает hash-pinned tooling, тестирует именно tagged code, собирает wheel/sdist/zipapp, проверяет установку, повторяемость и SHA256SUMS. Publisher job contents:write скачивает artifact того же run; token передаётся только шагу публикации. Нет новых secrets, paid resources, pull_request_target или токена в файлах/логах.

Publisher проверяет repo/event/main context, tag и release ID, exact четыре файла, локальные hashes и существующие asset states/digests. Заливает только отсутствующие assets; не перезаписывает файлы и не меняет tag. Скачивает файлы draft и сравнивает hashes перед публикацией; затем меняет только draft=false/prerelease=true у существующего release, повторно проверяет API states и скачанные hashes. При mismatch публикация останавливается. Повторный запуск уже опубликованного релиза только проверяет файлы, не изменяет их.

Запуск: `gh workflow run release.yml --ref main --repo mejustbox-byte/ad-opsec-auditor`, либо Run workflow на main в Actions. Публичный release готов только после successful build/publish jobs, draft=false, prerelease=true, четырёх uploaded assets и проверки скачанных checksum. Пустой draft и tagged branch не являются завершением выпуска.

Release automation находится в более новом main commit, чем product tag. Это намеренно: собирается прежний проверенный tag, publisher берётся из прошедшего review workflow commit. В product v0.1.0a1 native Windows AD tests остаются not_run.
