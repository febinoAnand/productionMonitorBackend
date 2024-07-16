#!/bin/ash

echo "Applying Migrations"
python manage.py migrate

echo "Creating Super User"
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username=admin --email=admin@febinosolutions.com --noinput

exec "$@"