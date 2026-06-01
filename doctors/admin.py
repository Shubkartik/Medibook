from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # Columns displayed in admin list view
    list_display = [
        'user_full_name',
        'specialization',
        'registration_number',
        'state_council',
        'verification_status_badge',  # Colored status indicator
        'is_available',
        'created_at'
    ]
    
    # Filter sidebar options
    list_filter = [
        'verification_status',
        'is_available',
        'specialization',
        'state_council'
    ]
    
    # Searchable fields across related models
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'specialization',
        'registration_number',
        'state_council'
    ]
    
    # Non-editable fields
    readonly_fields = ['created_at', 'updated_at', 'verified_at', 'verified_by']
    
    # Bulk actions for admin
    actions = ['approve_doctors', 'reject_doctors']
    
    # Organize form into sections
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'specialization', 'experience', 'qualification', 'fees', 'bio')
        }),
        ('Availability Settings', {
            'fields': ('available_days', 'start_time', 'end_time', 'slot_duration', 'is_available')
        }),
        ('🔍 License Verification', {
            'fields': ('registration_number', 'state_council', 'license_document'),
            'description': 'Verify these details against State Medical Council records'
        }),
        ('✅ Verification Status', {
            'fields': ('verification_status', 'is_verified', 'verification_notes', 'verified_by', 'verified_at'),
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )
    
    # Display doctor's full name
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Doctor Name'
    user_full_name.admin_order_field = 'user__first_name'  # Sort by first name
    
    # Colored verification status badge
    def verification_status_badge(self, obj):
        colors = {
            'pending': '🟡 Pending',
            'approved': '🟢 Approved',
            'rejected': '🔴 Rejected'
        }
        return colors.get(obj.verification_status, 'Unknown')
    verification_status_badge.short_description = 'Status'
    
    # Bulk action: approve selected doctors
    def approve_doctors(self, request, queryset):
        count = 0
        for doctor in queryset:
            if doctor.verification_status != 'approved':
                doctor.verification_status = 'approved'
                doctor.is_verified = True
                doctor.verified_by = request.user  # Track who approved
                doctor.verified_at = timezone.now()
                doctor.verification_notes = f'Approved by {request.user.username}'
                doctor.save()
                count += 1
        self.message_user(request, f'✅ {count} doctor(s) approved successfully!', messages.SUCCESS)
    approve_doctors.short_description = "✅ Approve selected doctors"
    
    # Bulk action: reject selected doctors
    def reject_doctors(self, request, queryset):
        count = 0
        for doctor in queryset:
            if doctor.verification_status != 'rejected':
                doctor.verification_status = 'rejected'
                doctor.is_verified = False
                doctor.verification_notes = f'Rejected by {request.user.username}'
                doctor.save()
                count += 1
        self.message_user(request, f'❌ {count} doctor(s) rejected.', messages.WARNING)
    reject_doctors.short_description = "❌ Reject selected doctors"
    
    # Auto-update verification fields on save
    def save_model(self, request, obj, form, change):
        if obj.verification_status == 'approved' and not obj.is_verified:
            obj.is_verified = True
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
        elif obj.verification_status == 'rejected':
            obj.is_verified = False
        super().save_model(request, obj, form, change)