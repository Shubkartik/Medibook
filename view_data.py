# superuser credentials
#SUPERUSER_USERNAME = "admin"
#SUPERUSER_PASSWORD = "admin123"

# how to open django admin panel
# http://127.0.0.1:8000/admin/ in this insert superuser credentials to login and manage the database through admin panel


# view_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from doctors.models import Doctor
from appointments.models import Appointment

print("\n" + "="*60)
print("MEDIBOOK - DATABASE VIEWER")
print("="*60)

# Users
print("\n REGISTERED USERS:")
print("-"*60)
for user in User.objects.all():
    print(f"Username: {user.username}")
    print(f"Full Name: {user.get_full_name()}")
    print(f"Email: {user.email}")
    print(f"Role: {user.profile.role}")
    print(f"Phone: {user.profile.phone}")
    print(f"Password: {user.password[:30]}... (hashed)")
    print(f"Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)

# Doctors
print("\n DOCTORS:")
print("-"*60)
for doc in Doctor.objects.all():
    print(f"Dr. {doc.user.get_full_name()}")
    print(f"Specialization: {doc.specialization}")
    print(f"Experience: {doc.experience} years")
    print(f"Fees: ₹{doc.fees}")
    print(f"Available: {doc.available_days}")
    print(f"Timings: {doc.start_time} - {doc.end_time}")
    print("-"*60)

# Appointments
print("\n APPOINTMENTS:")
print("-"*60)
for apt in Appointment.objects.all():
    print(f"Patient: {apt.patient.get_full_name()}")
    print(f"Doctor: Dr. {apt.doctor.user.get_full_name()}")
    print(f"Date: {apt.appointment_date}")
    print(f"Time: {apt.appointment_time}")
    print(f"Status: {apt.status.upper()}")
    print(f"Reason: {apt.reason[:50]}")
    print(f"Booked: {apt.created_at.strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)

# Stats
print("\n📊 STATISTICS:")
print("-"*60)
print(f"Total Users: {User.objects.count()}")
print(f"Total Patients: {UserProfile.objects.filter(role='patient').count()}")
print(f"Total Doctors: {UserProfile.objects.filter(role='doctor').count()}")
print(f"Total Appointments: {Appointment.objects.count()}")
print(f"Pending: {Appointment.objects.filter(status='pending').count()}")
print(f"Confirmed: {Appointment.objects.filter(status='confirmed').count()}")
print(f"Cancelled: {Appointment.objects.filter(status='cancelled').count()}")
print("="*60)