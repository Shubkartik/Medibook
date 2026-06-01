#!/usr/bin/env bash
set -e

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@medibook.com', 'Admin@2024')" | python manage.py shell || true

echo "Build complete!"
