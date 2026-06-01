from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    # Verification status options for admin approval
    VERIFICATION_CHOICES = (
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    # Consultation type options
    CONSULTATION_CHOICES = (
        ('in_person', 'In-Person'),
        ('online', 'Online'),
        ('both', 'Both In-Person & Online'),
    )
    
    # Link to User model (one doctor per user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    # Medical specialization (e.g., Cardiologist, Dentist)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    # Years of professional experience
    experience = models.IntegerField(help_text='Years of experience', blank=True, null=True)
    # Educational qualifications (e.g., MBBS, MD)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    # Consultation fee
    fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # Doctor's biography/description
    bio = models.TextField(blank=True, null=True)
    # Working days (comma separated: Monday, Tuesday, etc.)
    available_days = models.CharField(max_length=200, blank=True, null=True, help_text='Comma separated days')
    # Daily consultation start time
    start_time = models.TimeField(blank=True, null=True, help_text='Consultation start time')
    # Daily consultation end time
    end_time = models.TimeField(blank=True, null=True, help_text='Consultation end time')
    # Duration of each appointment slot in minutes
    slot_duration = models.IntegerField(default=30, blank=True, null=True)
    # Whether doctor is currently accepting appointments
    is_available = models.BooleanField(default=True)
    
    # Consultation type preference
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_CHOICES, default='both')
    
    # Clinic/Hospital address details
    clinic_name = models.CharField(max_length=200, blank=True, null=True, help_text='Hospital/Clinic name')
    address_line1 = models.CharField(max_length=300, blank=True, null=True, help_text='Street address')
    address_line2 = models.CharField(max_length=300, blank=True, null=True, help_text='Area/Landmark')
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # License verification fields
    is_verified = models.BooleanField(default=False)  # Quick verified check
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    registration_number = models.CharField(max_length=100, blank=True, null=True)  # Medical license number
    state_council = models.CharField(max_length=100, blank=True, null=True)  # Issuing state council
    license_document = models.FileField(upload_to='license_docs/', blank=True, null=True)  # Uploaded license
    verification_notes = models.TextField(blank=True, null=True)  # Admin notes on verification
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_doctors')
    verified_at = models.DateTimeField(null=True, blank=True)  # When verification was done
    
    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Display doctor name and specialization
        return f"Dr. {self.user.get_full_name()} - {self.specialization or 'Pending'}"
    
    def get_verification_badge(self):
        # Return emoji badge based on verification status
        if self.verification_status == 'approved':
            return '✅ Verified'
        elif self.verification_status == 'pending':
            return '⏳ Pending'
        else:
            return '❌ Rejected'
    
    def get_full_address(self):
        # Build complete address string from individual fields
        parts = []
        if self.clinic_name:
            parts.append(self.clinic_name)
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.pincode:
            parts.append(f'- {self.pincode}')
        return ', '.join(parts) if parts else 'Address not provided'
    
    class Meta:
        # Order by newest doctors first
        ordering = ['-created_at']