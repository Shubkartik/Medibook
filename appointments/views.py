from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from doctors.models import Doctor
from django.core.paginator import Paginator

@login_required
def patient_dashboard(request):
    """
    Patient Dashboard View
    Workflow: 
    1. Check if logged-in user has 'patient' role
    2. Fetch upcoming appointments (future dates with pending/confirmed status)
    3. Fetch past appointments (dates before today)
    4. Calculate total and pending appointment counts
    5. Display dashboard with appointment statistics
    """
    # Role-based access - only patients allowed
    if request.user.profile.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get next 5 upcoming active appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=timezone.now().date(),  # Future dates only
        status__in=['pending', 'confirmed']  # Active statuses
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    # Get last 5 past appointments
    past_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__lt=timezone.now().date()  # Past dates only
    ).order_by('-appointment_date')[:5]  # Most recent first
    
    # Dashboard statistics
    total_appointments = Appointment.objects.filter(patient=request.user).count()
    pending_appointments = Appointment.objects.filter(
        patient=request.user, 
        status='pending'
    ).count()
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
    }
    return render(request, 'patient/dashboard.html', context)

@login_required
def book_appointment(request, doctor_id):
    """
    Book Appointment View
    Workflow:
    1. Verify user is a patient
    2. Get doctor by ID (must be available and verified)
    3. POST: validate slot availability, create appointment
    4. GET: show available dates based on doctor's schedule
    """
    # Only patients can book
    if request.user.profile.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('dashboard')
    
    # Get verified and available doctor
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_available=True, is_verified=True)
    
    if request.method == 'POST':
        # Extract form data
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        # Check for double booking
        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['pending', 'confirmed']  # Check only active bookings
        ).exists()
        
        if existing:
            messages.error(request, 'This slot is already booked.')
            return redirect('book_appointment', doctor_id=doctor_id)
        
        # Create pending appointment
        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status='pending'  # Default status
        )
        
        messages.success(request, 'Appointment booked successfully!')
        return redirect('my_appointments')
    
    # Generate available dates for next 7 days
    available_dates = []
    today = timezone.now().date()
    for i in range(1, 8):  # Next 7 days
        date = today + timedelta(days=i)
        day_name = date.strftime('%A')  # Get weekday name
        # Check if doctor works on this day
        if doctor.available_days and day_name.lower() in [d.strip().lower() for d in doctor.available_days.split(',')]:
            available_dates.append(date.strftime('%Y-%m-%d'))
    
    return render(request, 'patient/book_appointment.html', {
        'doctor': doctor,
        'available_dates': available_dates,
    })

@login_required
def get_available_slots(request, doctor_id, date):
    """
    AJAX Endpoint for Available Time Slots
    Workflow:
    1. Get doctor by ID
    2. Parse the date parameter
    3. Calculate time slots based on doctor's working hours and slot duration
    4. Check which slots are already booked
    5. Return JSON with available/booked slots
    """
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    
    # Parse date string
    try:
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)
    
    slots = []
    # Start and end times for the day
    current_time = datetime.combine(appointment_date, doctor.start_time)
    end_time = datetime.combine(appointment_date, doctor.end_time)
    
    # Generate slots based on duration
    while current_time + timedelta(minutes=doctor.slot_duration) <= end_time:
        time_slot = current_time.time()
        
        # Check if slot is already taken
        is_booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=time_slot,
            status__in=['pending', 'confirmed']
        ).exists()
        
        slots.append({
            'time': time_slot.strftime('%H:%M'),
            'available': not is_booked  # True = free slot
        })
        
        # Increment by slot duration
        current_time += timedelta(minutes=doctor.slot_duration)
    
    return JsonResponse({'slots': slots})

@login_required
def my_appointments(request):
    """
    Patient's Appointments List View
    Workflow:
    1. Verify patient role
    2. Filter by status if provided
    3. Split into upcoming and past appointments
    4. Paginate results (10 per page)
    """
    if request.user.profile.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Optional status filter from URL
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.filter(patient=request.user)
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    today = timezone.now().date()
    # Separate upcoming and past appointments
    upcoming = appointments.filter(
        appointment_date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date', 'appointment_time')
    
    past = appointments.filter(appointment_date__lt=today).order_by('-appointment_date')
    
    # Paginate main appointment list
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'patient/my_appointments.html', {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'page_obj': page_obj,
        'status_filter': status_filter,
    })

@login_required
def cancel_appointment(request, appointment_id):
    """
    Cancel Appointment View
    Workflow:
    1. Get appointment (must belong to current patient)
    2. Check if cancellation is allowed
    3. POST: cancel with reason, update status
    4. GET: show cancellation confirmation page
    """
    # Verify appointment belongs to patient
    appointment = get_object_or_404(Appointment, pk=appointment_id, patient=request.user)
    
    # Check cancellation eligibility
    if not appointment.can_cancel():
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        # Process cancellation
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.POST.get('cancellation_reason', 'Cancelled by patient')
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('my_appointments')
    
    # Show confirmation page
    return render(request, 'patient/cancel_appointment.html', {'appointment': appointment})

@login_required
def doctor_appointments(request):
    """
    Doctor's Appointments Dashboard
    Workflow:
    1. Verify doctor role
    2. Get doctor profile
    3. Filter appointments by status if specified
    4. Paginate results (15 per page)
    """
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get doctor profile
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=doctor)
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Paginate results
    paginator = Paginator(appointments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'doctor/appointments.html', {
        'appointments': page_obj,
        'status_filter': status_filter,
    })

@login_required
def update_appointment_status(request, appointment_id, status):
    """
    Doctor Updates Appointment Status
    Workflow:
    1. Verify user is a doctor
    2. Get appointment and verify ownership
    3. Update status (confirmed/cancelled)
    4. Redirect back to appointments list
    """
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get appointment and verify ownership
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Ensure doctor owns this appointment
    if appointment.doctor != doctor:
        messages.error(request, 'This appointment does not belong to you.')
        return redirect('doctor_appointments')
    
    # Update status if valid
    if status in ['confirmed', 'cancelled']:
        appointment.status = status
        if status == 'cancelled':
            appointment.cancellation_reason = 'Cancelled by doctor'
        appointment.save()
        messages.success(request, f'Appointment {status} successfully.')
    
    return redirect('doctor_appointments')