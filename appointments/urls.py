from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('slots/<int:doctor_id>/<str:date>/', views.get_available_slots, name='get_available_slots'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor-appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('update-status/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
]