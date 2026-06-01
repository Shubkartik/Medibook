from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('update-profile/', views.update_doctor_profile, name='update_doctor_profile'),
]