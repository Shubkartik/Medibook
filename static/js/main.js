// ============================================
// Appointment APP - MAIN JAVASCRIPT
// Client-side functionality and UI interactions
// ============================================

// ==================== APP INITIALIZATION ====================
// Wait for DOM to fully load before running any code
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();  // Start all app functionality
});

// Main initialization function - calls all setup functions
function initializeApp() {
    initDarkMode();         // Theme toggle functionality
    initSidebar();          // Mobile responsive sidebar
    initTimeSlots();        // AJAX time slot loading
    initFormValidation();   // Real-time form validation
    initAutoDismissAlerts(); // Auto-hide alert messages
    initSmoothScroll();     // Smooth scrolling for anchors
    initAnimations();       // Scroll-triggered animations
}

// ==================== DARK MODE TOGGLE ====================
/**
 * Dark Mode Implementation
 * Workflow:
 * 1. Get the toggle button element
 * 2. Check localStorage for saved theme preference
 * 3. Apply saved theme on page load
 * 4. Toggle theme on button click
 * 5. Save preference to localStorage
 * 6. Add smooth transition animation
 */
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (!darkModeToggle) return;  // Exit if toggle doesn't exist
    
    // Check localStorage for previously saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        // Apply dark theme attributes
        document.documentElement.setAttribute('data-theme', 'dark');
        darkModeToggle.classList.add('active');  // Show toggle in active state
    }
    
    // Handle toggle button clicks
    darkModeToggle.addEventListener('click', function() {
        this.classList.toggle('active');  // Toggle visual state
        const isDark = this.classList.contains('active');
        
        if (isDark) {
            // Switch to dark mode
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');  // Persist preference
        } else {
            // Switch to light mode
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
        
        // Add smooth transition animation for theme switch
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';  // Reset transition after animation
        }, 300);
    });
}

// ==================== MOBILE SIDEBAR ====================
/**
 * Responsive Sidebar Navigation
 * Workflow:
 * 1. Toggle sidebar open/close on button click
 * 2. Close sidebar when overlay is clicked
 * 3. Close sidebar on Escape key press
 * 4. Update body class for mobile styling
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebarToggle || !sidebar) return;  // Exit if elements missing
    
    // Toggle sidebar when hamburger menu clicked
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');         // Show/hide sidebar
        if (overlay) overlay.classList.toggle('active');  // Show/hide overlay
        document.body.classList.toggle('sidebar-open');    // Prevent body scroll
    });
    
    // Close sidebar when clicking the dark overlay background
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        });
    }
    
    // Accessibility: Close sidebar with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        }
    });
}

// ==================== TIME SLOT SELECTION ====================
/**
 * AJAX Time Slot Loading
 * Workflow:
 * 1. Listen for date input changes
 * 2. Get selected date and doctor ID
 * 3. Show loading spinner while fetching
 * 4. Send AJAX request to get available slots
 * 5. Render time slots or error message
 * 6. Handle slot selection with visual feedback
 */
function initTimeSlots() {
    const timeSlotContainer = document.getElementById('timeSlots');
    const dateInput = document.getElementById('appointmentDate');
    
    if (!timeSlotContainer || !dateInput) return;  // Exit if not on booking page
    
    // Trigger when patient selects a date
    dateInput.addEventListener('change', function() {
        const selectedDate = this.value;
        const doctorId = this.dataset.doctorId;  // Get doctor ID from data attribute
        
        if (!selectedDate || !doctorId) return;
        
        // Show loading indicator while fetching slots
        timeSlotContainer.innerHTML = '<div class="spinner"></div>';
        
        // AJAX request to get available time slots
        fetch(`/appointments/slots/${doctorId}/${selectedDate}/`)
            .then(response => response.json())  // Parse JSON response
            .then(data => {
                if (data.error) {
                    showAlert(data.error, 'error');  // Show error message
                    return;
                }
                renderTimeSlots(data.slots);  // Display available slots
            })
            .catch(error => {
                console.error('Error fetching slots:', error);
                showAlert('Failed to load time slots. Please try again.', 'error');
            });
    });
}

/**
 * Render Time Slot Buttons
 * Creates clickable buttons for each available time slot
 */
function renderTimeSlots(slots) {
    const container = document.getElementById('timeSlots');
    const timeInput = document.getElementById('appointmentTime');
    
    if (!container || !timeInput) return;
    
    container.innerHTML = '';  // Clear previous slots
    
    // If no slots available for selected date
    if (slots.length === 0) {
        container.innerHTML = '<p class="text-center">No slots available for this date.</p>';
        return;
    }
    
    // Create button for each time slot
    slots.forEach(slot => {
        const slotElement = document.createElement('div');
        // Add 'booked' class if slot is unavailable
        slotElement.className = `time-slot ${slot.available ? '' : 'booked'}`;
        slotElement.textContent = slot.time;
        
        // Only allow clicking on available slots
        if (slot.available) {
            slotElement.addEventListener('click', function() {
                // Remove 'selected' class from all other slots (deselect)
                container.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                // Add 'selected' class to clicked slot (highlight)
                this.classList.add('selected');
                // Update hidden input with selected time for form submission
                timeInput.value = slot.time;
                
                // Add subtle pulse animation on selection
                this.style.animation = 'none';
                this.offsetHeight;  // Trigger reflow to restart animation
                this.style.animation = 'pulse 0.3s ease';
            });
        }
        
        container.appendChild(slotElement);
    });
}

// ==================== FORM VALIDATION ====================
/**
 * Real-time Form Validation
 * Workflow:
 * 1. Find all forms with data-validate attribute
 * 2. Validate on form submission (prevent submit if invalid)
 * 3. Validate individual inputs in real-time (on input & blur)
 * 4. Show/hide error messages dynamically
 * 5. Support email, password, phone, and date validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        // Prevent form submission if validation fails
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();  // Stop form submission
            }
        });
        
        // Real-time validation: check as user types
        form.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('input', function() {
                validateInput(input);  // Validate on each keystroke
            });
            
            input.addEventListener('blur', function() {
                validateInput(input);  // Validate when field loses focus
            });
        });
    });
}

// Validate entire form (all required fields)
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    // Check each required input
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;  // Mark form as invalid if any field fails
        }
    });
    
    return isValid;
}

// Validate individual input field
function validateInput(input) {
    // Get or create error message element (placed after input)
    const errorElement = input.nextElementSibling?.classList.contains('error-message') 
        ? input.nextElementSibling 
        : createErrorElement(input);
    
    let errorMessage = '';
    
    // Check 1: Required field empty
    if (input.hasAttribute('required') && !input.value.trim()) {
        errorMessage = 'This field is required.';
    }
    
    // Check 2: Email format validation
    if (input.type === 'email' && input.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // Standard email pattern
        if (!emailRegex.test(input.value.trim())) {
            errorMessage = 'Please enter a valid email address.';
        }
    }
    
    // Check 3: Password minimum length
    if (input.type === 'password' && input.value.trim()) {
        if (input.value.length < 8) {
            errorMessage = 'Password must be at least 8 characters long.';
        }
    }
    
    // Check 4: Phone number format (10 digits)
    if (input.type === 'tel' && input.value.trim()) {
        const phoneRegex = /^[0-9]{10}$/;
        // Remove common separators before validation
        if (!phoneRegex.test(input.value.replace(/[-() ]/g, ''))) {
            errorMessage = 'Please enter a valid 10-digit phone number.';
        }
    }
    
    // Check 5: Date must be in future (unless allow-past class present)
    if (input.type === 'date' && input.value.trim()) {
        const selectedDate = new Date(input.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);  // Compare dates only, not time
        
        if (selectedDate < today && !input.classList.contains('allow-past')) {
            errorMessage = 'Please select a future date.';
        }
    }
    
    // Update UI based on validation result
    if (errorMessage) {
        input.classList.add('is-invalid');      // Red border
        input.classList.remove('is-valid');     // Remove green border
        errorElement.textContent = errorMessage;
        errorElement.style.display = 'block';   // Show error message
        return false;  // Validation failed
    } else {
        input.classList.remove('is-invalid');   // Remove red border
        input.classList.add('is-valid');        // Green border (valid)
        errorElement.style.display = 'none';    // Hide error message
        return true;  // Validation passed
    }
}

// Create error message element dynamically
function createErrorElement(input) {
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.style.color = 'var(--danger-color)';
    errorElement.style.fontSize = '0.75rem';
    errorElement.style.marginTop = '0.25rem';
    errorElement.style.display = 'none';  // Hidden by default
    input.parentNode.insertBefore(errorElement, input.nextSibling);  // Insert after input
    return errorElement;
}

// ==================== AUTO-DISMISS ALERTS ====================
/**
 * Alert Message Auto-Dismiss
 * Workflow:
 * 1. Find all alert messages on page
 * 2. Auto-dismiss after 5 seconds with animation
 * 3. Allow manual close with close button
 * 4. Remove element from DOM after animation
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.style.animation = 'slideOutUp 0.5s ease forwards';  // Slide out animation
            setTimeout(() => {
                alert.remove();  // Remove from DOM after animation completes
            }, 500);
        }, 5000);  // 5 second delay
        
        // Manual close button functionality
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'slideOutUp 0.5s ease forwards';
                setTimeout(() => {
                    alert.remove();
                }, 500);
            });
        }
    });
}

// ==================== SMOOTH SCROLL ====================
/**
 * Smooth Scrolling for Anchor Links
 * Intercepts clicks on #hash links and scrolls smoothly
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();  // Prevent default jump behavior
                target.scrollIntoView({
                    behavior: 'smooth',  // Smooth scrolling animation
                    block: 'start'       // Align to top of element
                });
            }
        });
    });
}

// ==================== SCROLL ANIMATIONS ====================
/**
 * Intersection Observer for Scroll-triggered Animations
 * Workflow:
 * 1. Watch elements with .animate-on-scroll class
 * 2. When they enter viewport (10% visible)
 * 3. Add .animate-fade-in class to trigger animation
 * 4. Stop observing once animated (performance)
 */
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,           // Trigger when 10% of element is visible
        rootMargin: '0px 0px -50px 0px'  // Slightly before element enters viewport
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {  // Element is in viewport
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);  // Stop watching (animate once)
            }
        });
    }, observerOptions);
    
    // Start observing all elements with animation class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// ==================== UTILITY FUNCTIONS ====================

// Confirmation dialog wrapper
function confirmAction(message, callback) {
    if (confirm(message)) {  // Browser native confirm dialog
        callback();  // Execute callback if user confirms
    }
}

// Show loading spinner in element
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.style.margin = '20px auto';
    spinner.style.display = 'block';
    element.appendChild(spinner);
    return spinner;  // Return for later removal
}

// Remove loading spinner
function hideLoading(spinner) {
    if (spinner) {
        spinner.remove();
    }
}

// ==================== ALERT SYSTEM ====================
/**
 * Dynamic Alert Message Display
 * Creates alert messages programmatically with auto-dismiss
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;  // Exit if no alert container
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;  // Apply type-specific styling
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after specified duration
    setTimeout(() => {
        alert.style.animation = 'slideOutUp 0.5s ease forwards';
        setTimeout(() => {
            alert.remove();
        }, 500);
    }, duration);
    
    // Scroll to make alert visible
    alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Get appropriate icon for alert type
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';  // Default to info icon
}

// ==================== APPOINTMENT CANCELLATION ====================
/**
 * Cancel Appointment Function
 * Workflow:
 * 1. Show confirmation dialog
 * 2. Create hidden form dynamically
 * 3. Add CSRF token for security
 * 4. Submit form to cancel endpoint
 */
function cancelAppointment(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        // Create form element dynamically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/appointments/cancel/${appointmentId}/`;
        
        // Add CSRF token (required for Django POST requests)
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCookie('csrftoken');  // Get CSRF token from cookies
        
        // Add cancellation reason
        const reasonInput = document.createElement('input');
        reasonInput.type = 'hidden';
        reasonInput.name = 'cancellation_reason';
        reasonInput.value = 'Cancelled by patient';
        
        // Assemble and submit form
        form.appendChild(csrfInput);
        form.appendChild(reasonInput);
        document.body.appendChild(form);
        form.submit();  // Trigger Django view
    }
}

// ==================== CSRF TOKEN ====================
/**
 * Get CSRF Token from Cookies
 * Required for Django's CSRF protection on AJAX/dynamic POST requests
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');  // Split all cookies
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if cookie name matches
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ==================== PASSWORD STRENGTH ====================
/**
 * Password Strength Meter
 * Workflow:
 * 1. Analyze password complexity
 * 2. Check: length >= 8, >= 12
 * 3. Check: uppercase, numbers, special characters
 * 4. Update strength indicator with color
 */
function checkPasswordStrength(password) {
    const strengthMeter = document.getElementById('passwordStrength');
    if (!strengthMeter) return;
    
    let strength = 0;  // Strength score (0-5)
    
    // Length checks
    if (password.length >= 8) strength++;   // Minimum length
    if (password.length >= 12) strength++;  // Good length
    
    // Character variety checks
    if (/[A-Z]/.test(password)) strength++;           // Has uppercase
    if (/[0-9]/.test(password)) strength++;           // Has numbers
    if (/[^A-Za-z0-9]/.test(password)) strength++;    // Has special chars
    
    // Visual feedback - 5 levels
    const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['#ef4444', '#f59e0b', '#f59e0b', '#10b981', '#059669'];
    
    strengthMeter.textContent = strengthText[strength];
    strengthMeter.style.color = strengthColors[strength];
    strengthMeter.style.fontWeight = '600';
}

// Initialize password strength checker on page load
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);  // Check on each keystroke
        });
    }
});

// ==================== PRINT & EXPORT ====================

// Print appointment details
function printAppointment(appointmentId) {
    window.print();  // Triggers browser print dialog
}

// Export appointment to calendar (ICS format)
function exportToCalendar(appointmentData) {
    const icsContent = generateICS(appointmentData);  // Generate calendar file
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);  // Create download URL
    link.download = 'appointment.ics';       // Filename for download
    link.click();  // Trigger download
}

// Generate ICS calendar file content
function generateICS(data) {
    return `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:${data.date}T${data.time.replace(':', '')}00
DTEND:${data.date}T${data.endTime.replace(':', '')}00
SUMMARY:Doctor Appointment - Dr. ${data.doctorName}
DESCRIPTION:${data.description}
LOCATION:${data.location}
END:VEVENT
END:VCALENDAR`;
}