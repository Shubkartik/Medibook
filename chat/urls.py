from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('start/<int:appointment_id>/', views.start_chat, name='start_chat'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]