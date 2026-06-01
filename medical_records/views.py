from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from appointments.models import Appointment
from doctors.models import Doctor
from .models import MedicalRecord, Prescription, PrescribedMedicine
from datetime import date


@login_required
def patient_medical_history(request):
    """View medical records and prescriptions for patient"""
    # Only patients can access
    if request.user.profile.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get patient's medical records
    medical_records = MedicalRecord.objects.filter(patient=request.user)
    
    # Get all prescriptions (newest first)
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-created_at')
    
    context = {
        'medical_records': medical_records,
        'prescriptions': prescriptions,
    }
    return render(request, 'medical_records/patient_history.html', context)


@login_required
def view_prescription(request, prescription_id):
    """View a specific prescription details"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Only patient and doctor can view
    if request.user not in [prescription.patient, prescription.doctor.user]:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get all medicines in this prescription
    medicines = prescription.medicines.all()
    
    context = {
        'prescription': prescription,
        'medicines': medicines,
    }
    return render(request, 'medical_records/view_prescription.html', context)


@login_required
def create_prescription(request, appointment_id):
    """Doctor creates prescription for a confirmed appointment"""
    # Only doctors can create prescriptions
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Only doctors can create prescriptions.')
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Verify doctor owns this appointment
    if appointment.doctor != doctor:
        messages.error(request, 'Access denied.')
        return redirect('doctor_dashboard')
    
    # Only confirmed appointments can have prescriptions
    if appointment.status != 'confirmed':
        messages.error(request, 'Can only prescribe for confirmed appointments.')
        return redirect('doctor_appointments')
    
    if request.method == 'POST':
        # Get prescription details
        diagnosis = request.POST.get('diagnosis', '')
        symptoms = request.POST.get('symptoms', '')
        notes = request.POST.get('notes', '')
        follow_up_date = request.POST.get('follow_up_date', None)
        
        # Get medicine lists from form arrays
        medicine_names = request.POST.getlist('medicine_name[]')
        medicine_dosages = request.POST.getlist('dosage[]')
        medicine_frequencies = request.POST.getlist('frequency[]')
        medicine_durations = request.POST.getlist('duration[]')
        medicine_instructions = request.POST.getlist('instructions[]')
        
        # Diagnosis is required
        if not diagnosis:
            messages.error(request, 'Diagnosis is required.')
            return redirect('create_prescription', appointment_id=appointment_id)
        
        # Create the prescription
        prescription = Prescription.objects.create(
            appointment=appointment,
            patient=appointment.patient,
            doctor=doctor,
            diagnosis=diagnosis,
            symptoms=symptoms,
            notes=notes,
            follow_up_date=follow_up_date if follow_up_date else None
        )
        
        # Add each medicine to prescription
        for i in range(len(medicine_names)):
            if medicine_names[i].strip():  # Skip empty medicine entries
                PrescribedMedicine.objects.create(
                    prescription=prescription,
                    medicine_name=medicine_names[i],
                    dosage=medicine_dosages[i] if i < len(medicine_dosages) else '',
                    frequency=medicine_frequencies[i] if i < len(medicine_frequencies) else '',
                    duration=medicine_durations[i] if i < len(medicine_durations) else '',
                    instructions=medicine_instructions[i] if i < len(medicine_instructions) else ''
                )
        
        # Update patient's medical record with new info
        medical_record, created = MedicalRecord.objects.get_or_create(
            patient=appointment.patient,
            doctor=doctor
        )
        if symptoms:
            medical_record.notes = f"{medical_record.notes or ''}\n\nSymptoms ({date.today()}): {symptoms}"
        if diagnosis:
            medical_record.notes = f"{medical_record.notes or ''}\n\nDiagnosis ({date.today()}): {diagnosis}"
        medical_record.save()
        
        messages.success(request, '✅ Prescription created successfully!')
        return redirect('view_prescription', prescription_id=prescription.id)
    
    context = {
        'appointment': appointment,
        'patient': appointment.patient,
        'today': date.today(),
    }
    return render(request, 'medical_records/create_prescription.html', context)


@login_required
def doctor_prescriptions(request):
    """Doctor views all prescriptions they've created"""
    # Only doctors can access
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    # Get all prescriptions by this doctor (newest first)
    prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')
    
    context = {
        'prescriptions': prescriptions,
    }
    return render(request, 'medical_records/doctor_prescriptions.html', context)


@login_required
def update_medical_record(request, patient_id):
    """Doctor updates patient's medical record"""
    # Only doctors can update records
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(User, id=patient_id)
    
    # Get existing or create new medical record
    medical_record, created = MedicalRecord.objects.get_or_create(
        patient=patient,
        doctor=doctor
    )
    
    if request.method == 'POST':
        # Update record fields
        medical_record.blood_group = request.POST.get('blood_group', '')
        medical_record.allergies = request.POST.get('allergies', '')
        medical_record.chronic_conditions = request.POST.get('chronic_conditions', '')
        medical_record.current_medications = request.POST.get('current_medications', '')
        medical_record.notes = request.POST.get('notes', '')
        medical_record.save()
        
        messages.success(request, 'Medical record updated successfully!')
        return redirect('doctor_prescriptions')
    
    context = {
        'medical_record': medical_record,
        'patient': patient,
    }
    return render(request, 'medical_records/update_record.html', context)


@login_required
def edit_prescription(request, prescription_id):
    """Doctor edits an existing prescription"""
    # Only doctors can edit
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Only doctors can edit prescriptions.')
        return redirect('dashboard')
    
    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Verify prescription belongs to this doctor
    if prescription.doctor != doctor:
        messages.error(request, 'Access denied.')
        return redirect('doctor_prescriptions')
    
    if request.method == 'POST':
        # Get updated prescription details
        diagnosis = request.POST.get('diagnosis', '')
        symptoms = request.POST.get('symptoms', '')
        notes = request.POST.get('notes', '')
        follow_up_date = request.POST.get('follow_up_date', None)
        
        # Get updated medicine lists
        medicine_names = request.POST.getlist('medicine_name[]')
        medicine_dosages = request.POST.getlist('dosage[]')
        medicine_frequencies = request.POST.getlist('frequency[]')
        medicine_durations = request.POST.getlist('duration[]')
        medicine_instructions = request.POST.getlist('instructions[]')
        
        # Validate required fields
        if not diagnosis:
            messages.error(request, 'Diagnosis is required.')
            return redirect('edit_prescription', prescription_id=prescription_id)
        
        has_medicine = any(name.strip() for name in medicine_names)
        if not has_medicine:
            messages.error(request, 'At least one medicine is required.')
            return redirect('edit_prescription', prescription_id=prescription_id)
        
        # Update prescription fields
        prescription.diagnosis = diagnosis
        prescription.symptoms = symptoms
        prescription.notes = notes
        prescription.follow_up_date = follow_up_date if follow_up_date else None
        prescription.save()
        
        # Replace all medicines (delete old, add new)
        prescription.medicines.all().delete()
        for i in range(len(medicine_names)):
            if medicine_names[i].strip():
                PrescribedMedicine.objects.create(
                    prescription=prescription,
                    medicine_name=medicine_names[i],
                    dosage=medicine_dosages[i] if i < len(medicine_dosages) else '',
                    frequency=medicine_frequencies[i] if i < len(medicine_frequencies) else '',
                    duration=medicine_durations[i] if i < len(medicine_durations) else '',
                    instructions=medicine_instructions[i] if i < len(medicine_instructions) else ''
                )
        
        messages.success(request, '✅ Prescription updated successfully!')
        return redirect('view_prescription', prescription_id=prescription.id)
    
    # GET request - show edit form with existing data
    medicines = prescription.medicines.all()
    
    context = {
        'prescription': prescription,
        'medicines': medicines,
        'patient': prescription.patient,
        'is_edit': True,  # Flag to show edit mode in template
    }
    return render(request, 'medical_records/edit_prescription.html', context)


@login_required
def delete_prescription(request, prescription_id):
    """Doctor deletes a prescription"""
    # Only doctors can delete
    if request.user.profile.role != 'doctor':
        messages.error(request, 'Only doctors can delete prescriptions.')
        return redirect('dashboard')
    
    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Verify prescription belongs to this doctor
    if prescription.doctor != doctor:
        messages.error(request, 'Access denied.')
        return redirect('doctor_prescriptions')
    
    # POST confirms deletion
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, 'Prescription deleted successfully!')
        return redirect('doctor_prescriptions')
    
    # GET shows confirmation page
    return render(request, 'medical_records/delete_prescription.html', {'prescription': prescription})