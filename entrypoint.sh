#!/bin/sh

# Check if database is running before proceeding
if [ "$DATABASE" = "postgres" ]; then
    echo "Check if database is running..."

    # Use netcat to wait until the database host and port are available
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "The database is up and running :-D"
fi

# ADDED: Export path to fix ModuleNotFoundError
export PYTHONPATH=$PYTHONPATH:/usr/src/app


python manage.py migrate


# This line was already correct and runs the server
exec python /usr/src/app/manage.py runserver 0.0.0.0:8000

