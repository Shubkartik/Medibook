import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin123'
email = 'admin@medibook.com'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f'User {username} already exists')
else:
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created!')
