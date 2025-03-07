/**
 * METRA Form Validation
 * 
 * Handles client-side form validation for all forms in the application
 * Features:
 * - Automatic validation based on HTML5 attributes
 * - Custom validation rules
 * - Real-time validation as user types
 * - Accessible error messages
 * - Support for Bootstrap 5 validation styles
 */

class FormValidator {
    /**
     * Initialize form validation
     */
    constructor() {
        this.initValidation();
    }

    /**
     * Initialize form validation functionality
     */
    initValidation() {
        // Find all forms with data-validate attribute
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            // Add validation to each input
            inputs.forEach(input => {
                // Skip submit buttons and hidden fields
                if (input.type === 'submit' || input.type === 'hidden') return;
                
                // Add blur event to validate when user leaves the field
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                // Add input event for real-time validation
                input.addEventListener('input', () => {
                    // Clear error on typing
                    if (input.classList.contains('is-invalid')) {
                        input.classList.remove('is-invalid');
                        const feedbackEl = input.nextElementSibling;
                        if (feedbackEl && feedbackEl.classList.contains('invalid-feedback')) {
                            feedbackEl.textContent = '';
                        }
                    }
                });
            });
            
            // Form submission validation
            form.addEventListener('submit', (e) => {
                let isValid = true;
                
                // Validate all inputs
                inputs.forEach(input => {
                    // Skip submit buttons and hidden fields
                    if (input.type === 'submit' || input.type === 'hidden') return;
                    
                    if (!this.validateField(input)) {
                        isValid = false;
                    }
                });
                
                // Prevent submission if form is invalid
                if (!isValid) {
                    e.preventDefault();
                    
                    // Focus on the first invalid field
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                    
                    // Announce error for screen readers
                    this.announceFormErrors();
                }
            });
        });
    }

    /**
     * Validate a single field
     * @param {HTMLElement} field - The field to validate
     * @returns {boolean} - Whether the field is valid
     */
    validateField(field) {
        let isValid = true;
        let errorMessage = '';
        
        // Required validation
        if (field.required && !field.value.trim()) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Email validation
        else if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Password strength validation
        else if (field.type === 'password' && field.getAttribute('data-password-strength') && field.value.trim()) {
            if (field.value.length < 8) {
                isValid = false;
                errorMessage = 'Password must be at least 8 characters long';
            } else if (!/[A-Z]/.test(field.value)) {
                isValid = false;
                errorMessage = 'Password must contain at least one uppercase letter';
            } else if (!/[a-z]/.test(field.value)) {
                isValid = false;
                errorMessage = 'Password must contain at least one lowercase letter';
            } else if (!/[0-9]/.test(field.value)) {
                isValid = false;
                errorMessage = 'Password must contain at least one number';
            }
        }
        
        // Password confirmation validation
        else if (field.getAttribute('data-confirm-password')) {
            const passwordField = document.getElementById(field.getAttribute('data-confirm-password'));
            if (passwordField && field.value !== passwordField.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
        }
        
        // Minimum length validation
        else if (field.minLength && field.value.length < field.minLength && field.value.trim()) {
            isValid = false;
            errorMessage = `This field must be at least ${field.minLength} characters long`;
        }
        
        // Maximum length validation
        else if (field.maxLength && field.value.length > field.maxLength) {
            isValid = false;
            errorMessage = `This field must not exceed ${field.maxLength} characters`;
        }
        
        // Phone number validation
        else if (field.type === 'tel' && field.value.trim()) {
            const phoneRegex = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
            if (!phoneRegex.test(field.value)) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }
        
        // Apply validation UI
        this.updateFieldValidationUI(field, isValid, errorMessage);
        
        return isValid;
    }

    /**
     * Update the field's UI based on validation result
     * @param {HTMLElement} field - The field to update
     * @param {boolean} isValid - Whether the field is valid
     * @param {string} errorMessage - Error message to display
     */
    updateFieldValidationUI(field, isValid, errorMessage) {
        // Remove existing validation classes
        field.classList.remove('is-invalid', 'is-valid');
        
        // Add appropriate class
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Handle error message
        let feedbackEl = field.nextElementSibling;
        
        // If there's no feedback element or it's not a feedback div, create one
        if (!feedbackEl || !feedbackEl.classList.contains('invalid-feedback')) {
            feedbackEl = document.createElement('div');
            feedbackEl.className = 'invalid-feedback';
            field.parentNode.insertBefore(feedbackEl, field.nextSibling);
        }
        
        // Set error message
        if (!isValid) {
            feedbackEl.textContent = errorMessage;
        } else {
            feedbackEl.textContent = '';
        }
    }

    /**
     * Announce form errors for screen readers
     */
    announceFormErrors() {
        const errorCount = document.querySelectorAll('.is-invalid').length;
        
        // Create or get the announcer element
        let announcer = document.getElementById('validation-announcer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'validation-announcer';
            announcer.className = 'visually-hidden';
            announcer.setAttribute('aria-live', 'assertive');
            document.body.appendChild(announcer);
        }
        
        // Set the announcement message
        announcer.textContent = `Form contains ${errorCount} error${errorCount !== 1 ? 's' : ''}. Please correct and try again.`;
        
        // Clear the announcement after it's been read
        setTimeout(() => {
            announcer.textContent = '';
        }, 3000);
    }
}

// Initialize validation when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new FormValidator();
});

/**
 * Form Enhancements
 * Adds UI improvements to form elements
 */
class FormEnhancements {
    /**
     * Enhance form elements with custom styling and behavior
     */
    static enhanceFormElements() {
        // Style form icons
        document.querySelectorAll('.form-icon-group').forEach(group => {
            const input = group.querySelector('input, select, textarea');
            const icon = group.querySelector('i');
            
            if (input && icon) {
                // Add input classes
                input.classList.add('form-control', 'ps-5');
                
                // Position icon
                icon.style.position = 'absolute';
                icon.style.left = '15px';
                icon.style.top = '50%';
                icon.style.transform = 'translateY(-50%)';
                icon.style.zIndex = '10';
                
                // Add focus effect
                input.addEventListener('focus', () => {
                    icon.style.color = '#0d6efd'; // Bright blue
                });
                
                input.addEventListener('blur', () => {
                    // If valid, keep blue, otherwise back to default
                    if (input.classList.contains('is-invalid')) {
                        icon.style.color = '#0d6efd'; // Keep bright blue
                    } else if (input.value) {
                        icon.style.color = '#0d6efd'; // Keep bright blue for filled inputs
                    } else {
                        icon.style.color = ''; // Reset to default
                    }
                });
                
                // Set initial state if has value
                if (input.value) {
                    icon.style.color = '#0d6efd'; // Bright blue
                }
                
                // Update parent group positioning
                group.style.position = 'relative';
            }
        });
        
        // Float labels
        document.querySelectorAll('.form-floating').forEach(floating => {
            const input = floating.querySelector('input, textarea, select');
            const label = floating.querySelector('label');
            
            if (input && label) {
                // Set initial state if has value
                if (input.value) {
                    label.classList.add('active');
                }
                
                input.addEventListener('focus', () => {
                    label.classList.add('active');
                });
                
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        label.classList.remove('active');
                    }
                });
            }
        });
    }

    /**
     * Add custom styles to form elements
     */
    static styleFormElements() {
        // Create and insert custom styles
        const style = document.createElement('style');
        style.textContent = `
            .form-control:focus {
                border-color: #0d6efd;
                box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
            }
            
            /* Input group with icon */
            .form-icon-group {
                position: relative;
            }
            
            /* Custom select styling */
            select.form-select {
                background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%230d6efd' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
            }
            
            /* Custom checkbox style */
            .form-check-input:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            
            /* Floating labels */
            .form-floating label {
                transition: all 0.2s ease-in-out;
            }
            
            .form-floating label.active {
                transform: scale(0.85) translateY(-0.5rem) translateX(0.15rem);
                opacity: 1;
                color: #0d6efd;
            }
            
            /* Shake animation for invalid fields */
            .animate-shake {
                animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
            }
            
            @keyframes shake {
                10%, 90% { transform: translateX(-1px); }
                20%, 80% { transform: translateX(2px); }
                30%, 50%, 70% { transform: translateX(-4px); }
                40%, 60% { transform: translateX(4px); }
            }
            
            /* Social login buttons */
            .btn-google {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                color: #0d6efd;
            }
            
            .btn-facebook {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                color: #0d6efd;
            }
            
            .btn-twitter {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                color: #0d6efd;
            }
            
            /* Password strength meter */
            .password-strength-meter {
                height: 5px;
                background-color: #f0f7ff;
                margin-top: 5px;
                border-radius: 3px;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .password-strength-meter .strength-value {
                height: 100%;
                width: 0%;
                transition: width 0.5s ease;
                border-radius: 3px;
                background-color: #0d6efd;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Initialize password strength meter
     */
    static initPasswordStrengthMeter() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        
        passwordInputs.forEach(input => {
            // Create strength meter
            const meterContainer = document.createElement('div');
            meterContainer.className = 'password-strength-meter';
            
            const strengthValue = document.createElement('div');
            strengthValue.className = 'strength-value';
            meterContainer.appendChild(strengthValue);
            
            // Insert after input
            input.parentNode.insertBefore(meterContainer, input.nextSibling);
            
            // Create feedback element
            const feedbackEl = document.createElement('div');
            feedbackEl.className = 'password-feedback mt-1 small';
            feedbackEl.style.color = '#0d6efd';
            input.parentNode.insertBefore(feedbackEl, meterContainer.nextSibling);
            
            // Add event listener
            input.addEventListener('input', () => {
                const value = input.value;
                const strength = this.calculatePasswordStrength(value);
                
                // Update strength meter
                strengthValue.style.width = strength.percent + '%';
                
                // Update feedback
                feedbackEl.textContent = strength.message;
            });
        });
    }

    /**
     * Calculate password strength
     * @param {string} password - Password to evaluate
     * @returns {Object} - Result with percent and message
     */
    static calculatePasswordStrength(password) {
        if (!password) {
            return { 
                percent: 0, 
                message: '' 
            };
        }
        
        let strength = 0;
        let feedback = [];
        
        // Length check
        if (password.length >= 8) {
            strength += 25;
        } else {
            feedback.push('Password should be at least 8 characters');
        }
        
        // Uppercase check
        if (/[A-Z]/.test(password)) {
            strength += 25;
        } else {
            feedback.push('Add uppercase letters');
        }
        
        // Lowercase check
        if (/[a-z]/.test(password)) {
            strength += 25;
        } else {
            feedback.push('Add lowercase letters');
        }
        
        // Number or special char check
        if (/[0-9!@#$%^&*(),.?":{}|<>]/.test(password)) {
            strength += 25;
        } else {
            feedback.push('Add numbers or special characters');
        }
        
        let message;
        if (strength === 0) {
            message = '';
        } else if (strength <= 25) {
            message = 'Password is weak';
        } else if (strength <= 50) {
            message = 'Password is moderate';
        } else if (strength <= 75) {
            message = 'Password is good';
        } else {
            message = 'Password is strong';
        }
        
        if (feedback.length > 0 && strength < 100) {
            message += ': ' + feedback.join(', ');
        }
        
        return {
            percent: strength,
            message: message
        };
    }
}

/**
 * Initialize everything when the DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize form validation on all forms with data-validate attribute
    document.querySelectorAll('form[data-validate]').forEach(form => {
        new FormValidator(form);
    });
    
    // Apply form enhancements
    FormEnhancements.enhanceFormElements();
    FormEnhancements.styleFormElements();
    FormEnhancements.initPasswordStrengthMeter();
});