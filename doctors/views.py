from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q  # Complex OR queries
from .models import Doctor
from appointments.models import Appointment
from django.utils import timezone


@login_required
def doctor_dashboard(request):
    """
    Doctor Dashboard View
    Workflow:
    1. Verify user has 'doctor' role
    2. Check if doctor profile exists (redirect to create if not)
    3. Calculate appointment statistics (total, pending, confirmed, today's)
    4. Fetch 5 most recent appointments
    5. Display dashboard with all metrics
    """
    # Only doctors can access
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied. You are not a doctor.')
        return redirect('dashboard')
    
    # Get doctor profile or redirect to create one
    doctor = None
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('update_doctor_profile')
    
    # Appointment statistics for dashboard cards
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='pending').count()
    confirmed_appointments = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    # Today's active appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor, 
        appointment_date=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).count()
    
    # Recent 5 appointments for quick view
    recent_appointments = Appointment.objects.filter(doctor=doctor).order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'today_appointments': today_appointments,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'doctor/dashboard.html', context)


@login_required
def doctor_list(request):
    # Search and filter parameters
    search_query = request.GET.get('search', '')
    specialization = request.GET.get('specialization', '')
    
    # Only show verified and available doctors to patients
    doctors = Doctor.objects.filter(
        is_available=True,
        is_verified=True,
        verification_status='approved'
    )
    
    # Search by name or specialization
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
    # Filter by specialization
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)
    
    # Get unique specializations for filter dropdown
    specializations = Doctor.objects.filter(
        is_available=True,
        is_verified=True,
        verification_status='approved'
    ).exclude(
        specialization__isnull=True
    ).exclude(
        specialization=''
    ).values_list('specialization', flat=True).distinct()
    
    # Paginate results (6 per page)
    paginator = Paginator(doctors, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'specializations': specializations,
        'search_query': search_query,
        'selected_specialization': specialization,
    }
    return render(request, 'patient/doctor_list.html', context)


@login_required
def update_doctor_profile(request):
    # Only doctors can update profile
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get existing or create new doctor profile with defaults
    doctor, created = Doctor.objects.get_or_create(
        user=request.user,
        defaults={
            'specialization': '',
            'experience': 0,
            'qualification': '',
            'fees': 0,
            'available_days': '',
            'start_time': '09:00',
            'end_time': '17:00',
            'slot_duration': 30,
            'bio': '',
            'is_verified': False,
            'verification_status': 'pending'
        }
    )
    
    if request.method == 'POST':
        # Extract form data
        specialization = request.POST.get('specialization', '')
        experience = request.POST.get('experience', 0)
        qualification = request.POST.get('qualification', '')
        fees = request.POST.get('fees', 0)
        bio = request.POST.get('bio', '')
        available_days = request.POST.get('available_days', '')
        start_time = request.POST.get('start_time', '09:00')
        end_time = request.POST.get('end_time', '17:00')
        slot_duration = request.POST.get('slot_duration', 30)
        registration_number = request.POST.get('registration_number', '')
        state_council = request.POST.get('state_council', '')
        # Address fields
        doctor.consultation_type = request.POST.get('consultation_type', 'both')
        doctor.clinic_name = request.POST.get('clinic_name', '')
        doctor.address_line1 = request.POST.get('address_line1', '')
        doctor.address_line2 = request.POST.get('address_line2', '')
        doctor.city = request.POST.get('city', '')
        doctor.state = request.POST.get('state', '')
        doctor.pincode = request.POST.get('pincode', '')
        
        # Validate required fields
        errors = []
        if not specialization:
            errors.append('Specialization is required.')
        if not registration_number:
            errors.append('Registration number is required for verification.')
        if not state_council:
            errors.append('State Medical Council is required for verification.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Update doctor profile fields
            doctor.specialization = specialization
            doctor.experience = int(experience) if experience else 0
            doctor.qualification = qualification
            doctor.fees = float(fees) if fees else 0
            doctor.bio = bio
            doctor.available_days = available_days
            doctor.start_time = start_time
            doctor.end_time = end_time
            doctor.slot_duration = int(slot_duration) if slot_duration else 30
            doctor.registration_number = registration_number
            doctor.state_council = state_council
            
            # Handle license document upload
            if 'license_document' in request.FILES:
                doctor.license_document = request.FILES['license_document']
            
            # Reset verification status on profile update
            if not doctor.is_verified:
                doctor.verification_status = 'pending'
            
            doctor.save()
            
            messages.success(request, '✅ Profile saved! Your license details are pending admin verification.')
            return redirect('doctor_dashboard')
    
    return render(request, 'doctor/profile.html', {'doctor': doctor})