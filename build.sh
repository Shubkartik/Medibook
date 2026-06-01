#!/usr/bin/env bash
set -e

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin123', 'admin@medibook.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists')"

echo "Build complete!"
