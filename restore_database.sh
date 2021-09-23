#!/bin/bash
set -eux
# su postgres -c "createdb moscow2021 || true"
su postgres -c "psql moscow2021 < /data/backups/observer-20210920_210000.sql"
