from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor
from appointments.models import Appointment


class MedicalRecord(models.Model):
    """Patient medical history maintained by doctor"""
    # Patient whose record this belongs to
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    # Doctor maintaining this record
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_records')
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Medical details
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)  # Known allergies
    chronic_conditions = models.TextField(blank=True, null=True)  # Long-term conditions
    current_medications = models.TextField(blank=True, null=True)  # Ongoing medications
    notes = models.TextField(blank=True, null=True)  # General medical notes
    
    class Meta:
        # One record per patient-doctor pair
        unique_together = ['patient', 'doctor']
    
    def __str__(self):
        return f"Medical Record: {self.patient.get_full_name()} - Dr. {self.doctor.user.get_full_name()}"


class Prescription(models.Model):
    """Digital prescription created by doctor for patient"""
    # Linked to specific appointment
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    # Patient receiving prescription
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    # Doctor issuing prescription
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    
    # Prescription details
    diagnosis = models.TextField(help_text='Diagnosis/Findings')  # Doctor's diagnosis
    symptoms = models.TextField(help_text='Patient symptoms', blank=True, null=True)
    notes = models.TextField(help_text='Additional notes/instructions', blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)  # Next visit date
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Whether prescription is still valid
    
    def __str__(self):
        return f"Prescription for {self.patient.get_full_name()} on {self.created_at.strftime('%d-%m-%Y')}"
    
    class Meta:
        # Newest prescriptions first
        ordering = ['-created_at']


class PrescribedMedicine(models.Model):
    """Medicines prescribed in a prescription"""
    # Link to parent prescription
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    # Medicine details
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text='e.g., 500mg')  # Medicine strength
    frequency = models.CharField(max_length=100, help_text='e.g., Twice a day')  # How often to take
    duration = models.CharField(max_length=100, help_text='e.g., 5 days')  # How long to take
    instructions = models.TextField(blank=True, null=True, help_text='e.g., Take after food')  # Special instructions
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"