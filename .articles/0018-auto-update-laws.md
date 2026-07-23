# Автообновление законов по расписанию

После TASK-0017 corpus перестал быть набором ручных выдержек, но осталась эксплуатационная проблема: локальные тексты могут устареть. Для legal RAG это не второстепенная деталь. Если citation указывает на старую редакцию, система выглядит уверенно, но фактически помогает принять неверное решение.

В TASK-0018 я добавил отдельную cron-обертку вокруг `scripts/fetch_laws.py`. Она проходит по всем configured laws, сохраняет JSON-лог в `data/logs/`, считает `changed`, `skipped` и `failed`, а для изменений и ошибок формирует notification lines. Пока это не отправка во внешний канал, а структурированное событие в логе. Для текущего MVP этого достаточно: cron или compose job может быть проверен по exit code и по JSON-артефакту.

По ходу нашлась более конкретная ошибка. `fetch_law()` считал новый checksum по телу документа, а существующий checksum сравнивал с checksum всего Markdown-файла вместе с frontmatter. Из-за этого deduplication могла не срабатывать даже без изменения текста. Теперь сохраненный checksum читается из frontmatter, а `fetch_law()` возвращает структурированный результат: `changed`, `skipped` или `failed`.

Расписание вынесено в `crontab`: раз в неделю, по понедельникам в 03:00. В `docker-compose.yml` уже есть профиль `cron` с сервисом `laws-updater`; он запускает тот же скрипт и пишет логи в volume. Для этого в Dockerfile появился отдельный lightweight target `laws-updater`: ему нужны `scripts/`, `httpx`, `beautifulsoup4` и `pyyaml`, но не весь API stack с `sentence-transformers`. Это не полноценный scheduler внутри compose, но рабочий building block для cron на host или отдельного orchestrator job.

Проверка началась с тестов, которые падали на старой реализации: `fetch_law()` возвращал `None`, а cron summary не знал про changed/skipped. После правки `python -m pytest tests/test_laws_update_cron.py -q` проходит. Для контейнера добавлен `--check`: он проверяет wiring, количество configured laws и доступность log directory без live-запросов к внешним legal sources. Контейнерная проверка прошла через `docker build --target laws-updater`, `docker run ... python scripts/update_laws_cron.py --check` и `docker compose build laws-updater`.

Отдельный эксплуатационный нюанс — Docker build. Первая попытка smoke-check собирала общий API image и тянула тяжелые ML wheels, включая `torch` и CUDA-пакеты. Это неправильно для cron job: проверка обновления законов не должна зависеть от установки embedding stack. Поэтому `laws-updater` вынесен в отдельный Docker target, а для pip оставлены увеличенные timeout/retries.

Ограничение осталось тем же: юридические выводы не становятся окончательными только потому, что corpus обновляется автоматически. Автообновление снижает риск устаревших citation, но не заменяет проверку юристом и контроль качества источников.
