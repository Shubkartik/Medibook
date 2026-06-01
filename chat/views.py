from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max, Q
from appointments.models import Appointment
from .models import ChatRoom, Message


@login_required
def chat_room(request, room_id):
    # Get chat room or 404
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Only patient and doctor can access this chat
    if request.user not in [room.patient, room.doctor]:
        messages.error(request, 'You do not have access to this chat.')
        return redirect('dashboard')
    
    # Get last 50 messages (newest first)
    chat_msgs = Message.objects.filter(room=room).order_by('-timestamp')[:50]
    
    # Mark all unread messages as read (except sender's own)
    Message.objects.filter(
        room=room, is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    context = {
        'room': room,
        'chat_msgs': chat_msgs,
        'other_user': room.doctor if request.user == room.patient else room.patient,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def start_chat(request, appointment_id):
    # Get appointment or 404
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Verify user is part of this appointment
    if request.user not in [appointment.patient, appointment.doctor.user]:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Chat only available for confirmed appointments
    if appointment.status != 'confirmed':
        messages.error(request, 'Chat is only available for confirmed appointments.')
        return redirect('dashboard')
    
    # Get existing room or create new one
    room, created = ChatRoom.objects.get_or_create(
        appointment=appointment,
        defaults={
            'patient': appointment.patient,
            'doctor': appointment.doctor.user,
        }
    )
    
    return redirect('chat_room', room_id=room.id)


@login_required
def get_unread_count(request):
    # AJAX endpoint to get unread message count
    count = 0
    if request.user.profile.role == 'patient':
        # Count rooms with unread messages for patient
        count = ChatRoom.objects.filter(
            patient=request.user, is_active=True
        ).filter(
            messages__is_read=False
        ).exclude(
            messages__sender=request.user
        ).distinct().count()
    elif request.user.profile.role == 'doctor':
        # Count rooms with unread messages for doctor
        count = ChatRoom.objects.filter(
            doctor=request.user, is_active=True
        ).filter(
            messages__is_read=False
        ).exclude(
            messages__sender=request.user
        ).distinct().count()
    
    return JsonResponse({'unread_count': count})


@login_required
def chat_list(request):
    """List all chat rooms for the user with search functionality"""
    search_query = request.GET.get('search', '')
    
    if request.user.profile.role == 'patient':
        # Get patient's active chat rooms with related data
        chat_rooms = ChatRoom.objects.filter(
            patient=request.user,
            is_active=True
        ).select_related('doctor', 'appointment', 'appointment__doctor')
        
        # Search by doctor name or specialization
        if search_query:
            chat_rooms = chat_rooms.filter(
                Q(doctor__first_name__icontains=search_query) |
                Q(doctor__last_name__icontains=search_query) |
                Q(appointment__doctor__specialization__icontains=search_query)
            )
        
        # Order by most recent message
        chat_rooms = chat_rooms.annotate(
            last_msg=Max('messages__timestamp')
        ).order_by('-last_msg', '-created_at')
        
    elif request.user.profile.role == 'doctor':
        # Get doctor's active chat rooms with related data
        chat_rooms = ChatRoom.objects.filter(
            doctor=request.user,
            is_active=True
        ).select_related('patient', 'appointment', 'appointment__doctor')
        
        # Search by patient name or appointment reason
        if search_query:
            chat_rooms = chat_rooms.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(appointment__reason__icontains=search_query)
            )
        
        # Order by most recent message
        chat_rooms = chat_rooms.annotate(
            last_msg=Max('messages__timestamp')
        ).order_by('-last_msg', '-created_at')
    else:
        chat_rooms = []
    
    # Add extra info for each chat room
    for room in chat_rooms:
        # Count unread messages for current user
        room.unread = room.get_unread_count(request.user)
        # Get last message timestamp
        last_message = room.messages.order_by('-timestamp').first()
        room.last_message_time = last_message.timestamp if last_message else room.created_at
    
    context = {
        'chat_rooms': chat_rooms,
        'search_query': search_query,
    }
    return render(request, 'chat/chat_list.html', context)