from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor
from django.utils import timezone

class Appointment(models.Model):
    # Appointment status options
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    # Patient who booked the appointment
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    # Doctor assigned to the appointment
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    # Date of the appointment
    appointment_date = models.DateField()
    # Time of the appointment
    appointment_time = models.TimeField()
    # Reason for the visit
    reason = models.TextField(help_text='Reason for appointment')
    # Current status of the appointment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # Auto-set when appointment is created
    created_at = models.DateTimeField(auto_now_add=True)
    # Auto-updated on every save
    updated_at = models.DateTimeField(auto_now=True)
    # Optional reason if appointment is cancelled
    cancellation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        # Prevent double-booking: same doctor, date, and time
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        # Show newest appointments first
        ordering = ['-appointment_date', '-appointment_time']
    
    def __str__(self):
        # Readable representation: patient - doctor - date time
        return f"{self.patient.username} - Dr. {self.doctor.user.get_full_name()} - {self.appointment_date} {self.appointment_time}"
    
    def can_cancel(self):
        # Check if appointment can be cancelled (must be pending/confirmed and in the future)
        return self.status in ['pending', 'confirmed'] and self.appointment_date > timezone.now().date()