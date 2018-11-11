#!/bin/sh
set -e

while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
    echo "MySQL is unavailable - sleeping"
    sleep 1;
done

echo "MySQL is up - continuing"

exec "$@"
