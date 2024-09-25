#!/bin/ash
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "Applying Migrations"
python manage.py migrate

echo "Creating Super User"
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username=admin --email=admin@febinosolutions.com --noinput

# exec "$@"
python manage.py runserver 0.0.0.0:8000 --noreload