from django.db import models
from django.contrib.auth.models import User  # Django's built-in User model
from django.db.models.signals import post_save  # Signal fired after model is saved
from django.dispatch import receiver  # Decorator to connect signals to handlers

class UserProfile(models.Model):
    """
    Extended User Profile Model
    Adds additional fields to Django's default User model
    Uses One-to-One relationship (each User has exactly one Profile)
    
    Purpose: Store role (patient/doctor), phone, and profile image
    without modifying the built-in User model
    """
    
    # Role choices: defines possible user types in the system
    ROLE_CHOICES = (
        ('patient', 'Patient'),  # (database_value, display_value)
        ('doctor', 'Doctor'),
    )
    
    # One-to-One link to User model
    # on_delete=CASCADE: If User is deleted, Profile is also deleted
    # related_name='profile': Access via user.profile (instead of user.userprofile)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # User role: determines access permissions and features
    # Stored as 10-char string 'patient' or 'doctor'
    # default='patient': New users start as patients unless specified
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='patient'
    )
    
    # Phone number: optional field, 15 chars max for international numbers
    # blank=True: Allows empty string in forms
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        default=''
    )
    
    # Profile image: optional, stored in /media/profile_images/
    # blank=True: Optional in forms
    # null=True: Allow NULL in database
    profile_image = models.ImageField(
        upload_to='profile_images/',  # Files saved to MEDIA_ROOT/profile_images/
        blank=True, 
        null=True
    )
    
    # Timestamp: automatically set when profile is created
    # auto_now_add=True: Set once on creation, never changes
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """String representation of the profile"""
        return f"{self.user.username} - {self.role}"


# ==================== DJANGO SIGNALS ====================
# Signals are used to automatically create/update UserProfile
# whenever a User is created or saved. This ensures every
# User always has an associated Profile.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal Handler: Create UserProfile when new User is created
    
    Workflow:
    1. Django creates new User record
    2. post_save signal is fired
    3. This handler checks if User was just created (created=True)
    4. If yes, creates corresponding UserProfile
    
    Parameters:
        sender: The model class (User)
        instance: The actual User object that was saved
        created: Boolean - True if new record, False if updated
        **kwargs: Additional signal arguments (unused)
    """
    if created:  # Only create profile for new users
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal Handler: Save UserProfile when User is saved
    
    Workflow:
    1. Django saves User record
    2. post_save signal is fired
    3. Check if User has a profile attribute
    4. If no profile exists (edge case), create one
    5. Save the profile to update any changes
    
    Why this is needed:
    - Ensures profile is always saved when User is saved
    - Handles edge cases where profile might be missing
    - Syncs any changes made to User model
    
    Parameters:
        sender: The model class (User)
        instance: The actual User object that was saved
        **kwargs: Additional signal arguments (unused)
    """
    # Safety check: if profile doesn't exist, create it
    # hasattr() checks if 'profile' attribute exists on User object
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    
    # Save the profile (updates existing or newly created)
    instance.profile.save()