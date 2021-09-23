## Дешифровка данных электронного голосования в Москве (сентябрь 2021)

В репозитории уже содержится файл с расшифрованными голосами из базы голосования `votes-dump.json.bz2`
Но можно повторить всю процедуру расшифровки самостоятельно.

Краткая инструкция по использованию скриптов

1. Скачиваем [SQL базу голосования](https://observer.mos.ru/all/servers/1/txs) и распакованный файл кладем в директорию `./backups`
2. Запускаем postgres в докере `docker-compose up -d`
3. Копируем скрипт для загрузки данных в базу в директорию c бэкапом `cp restore_database.sh backups/`
4. Запускаем восстановление базы из бэкапа `docker exec -it e-voting_postgres_1 /data/backups/restore_database.sh`
5. Устанавливаем необходимые зависимости для скрипта дешифровки `pip3 install -r requirements.txt`
6. Запускаем скрипт дешифровки `./dump_votes.py`
7. После всех манипуляций имеет смысл погасить докер-образы и удалить неиспользуемый больше сторадж для базы `docker-compose down; docker volume prune`
