from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.patient_medical_history, name='patient_medical_history'),
    path('prescription/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('create-prescription/<int:appointment_id>/', views.create_prescription, name='create_prescription'),
    path('edit-prescription/<int:prescription_id>/', views.edit_prescription, name='edit_prescription'),
    path('delete-prescription/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
    path('doctor-prescriptions/', views.doctor_prescriptions, name='doctor_prescriptions'),
    path('update-record/<int:patient_id>/', views.update_medical_record, name='update_medical_record'),
]