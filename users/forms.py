from django import forms
from django.contrib.auth.forms import UserCreationForm  # Built-in registration form
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """
    Custom User Registration Form
    Extends Django's built-in UserCreationForm to add:
    - Email field (required)
    - First & last name (required)
    - Role selection (patient/doctor)
    - Phone number (optional)
    
    Workflow:
    1. User fills registration form with personal details
    2. Form validates all fields on submission
    3. Custom validation checks for duplicate email/username
    4. On save: creates User record then creates/updates UserProfile
    """
    
    # Email field with custom widget styling
    # required=True ensures user must provide email
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',          # CSS class for styling
            'placeholder': 'Enter your email address'  # Placeholder text
        })
    )
    
    # First name field - limited to 30 characters (Django default)
    first_name = forms.CharField(
        max_length=30, 
        required=True,  # Mandatory field
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    # Last name field - limited to 30 characters (Django default)
    last_name = forms.CharField(
        max_length=30, 
        required=True,  # Mandatory field
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    # Role selection using radio buttons
    # Choices come from UserProfile model (Patient/Doctor)
    # RadioSelect renders as clickable radio buttons instead of dropdown
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,  # e.g., [('patient', 'Patient'), ('doctor', 'Doctor')]
        widget=forms.RadioSelect()         # Display as radio buttons
    )
    
    # Phone number field - optional (required=False)
    # Max 15 characters to accommodate international formats
    phone = forms.CharField(
        max_length=15, 
        required=False,  # Optional field
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (optional)'
        })
    )
    
    class Meta:
        # Tells Django which model to use for this form
        model = User
        # Specifies field order in the form
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'phone']
    
    def __init__(self, *args, **kwargs):
        """
        Constructor - Customizes form fields on initialization
        Workflow:
        1. Call parent constructor (UserCreationForm)
        2. Customize username field appearance and help text
        3. Customize password fields with clear instructions
        4. Add CSS classes and placeholders for all fields
        """
        super().__init__(*args, **kwargs)  # Call parent init
        
        # Customize username field
        # Override default widget attributes for better UX
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',           # Bootstrap-style form control
            'placeholder': 'Choose a username'  # Helpful placeholder
        })
        self.fields['username'].help_text = 'Required. Letters, digits and @/./+/-/_ only.'
        
        # Customize password1 field (first password input)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        # HTML list for password requirements - more user-friendly
        self.fields['password1'].help_text = '''
            <ul style="font-size: 0.8rem; color: #666; margin-top: 5px;">
                <li>Your password can't be too similar to your other personal information.</li>
                <li>Your password must contain at least 8 characters.</li>
                <li>Your password can't be a commonly used password.</li>
                <li>Your password can't be entirely numeric.</li>
            </ul>
        '''
        
        # Customize password2 field (password confirmation)
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
    
    def clean_email(self):
        """
        Custom email validation
        Workflow:
        1. Get email from cleaned form data
        2. Check if email already exists in database
        3. If exists, raise ValidationError
        4. If unique, return email
        """
        email = self.cleaned_data.get('email')  # Get validated email
        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email.')
        return email
    
    def clean_username(self):
        """
        Custom username validation
        Workflow:
        1. Get username from cleaned form data
        2. Check if username already exists
        3. Check minimum length requirement
        4. Return validated username
        """
        username = self.cleaned_data.get('username')
        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        # Enforce minimum length of 3 characters
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters long.')
        return username
    
    def save(self, commit=True):
        """
        Save user and profile data
        Workflow:
        1. Create User object without saving (commit=False)
        2. Set email, first_name, last_name from form data
        3. If commit=True, save User to database
        4. Update the auto-created UserProfile with role and phone
        5. Save UserProfile to database
        
        Parameters:
            commit (bool): If True, save to database. If False, return unsaved object.
        """
        # Create User object but don't save yet
        # commit=False allows modifying user before database insertion
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            # Save User to database
            # Django signals auto-create UserProfile after User is saved
            user.save()
            
            # Update the auto-created profile with additional data
            # UserProfile is created by post_save signal when User is saved
            user.profile.role = self.cleaned_data['role']
            user.profile.phone = self.cleaned_data['phone']
            user.profile.save()  # Save profile changes
            
        return user  # Return the created/modified user object