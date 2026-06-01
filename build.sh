#!/usr/bin/env bash
set -e

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
import django
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin123').exists():
    User.objects.create_superuser('admin123', 'admin@medibook.com', 'admin123')
    print('Superuser created!')
else:
    print('Superuser already exists')
"

echo "Build complete!"
