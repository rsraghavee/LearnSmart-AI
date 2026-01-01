/**
 * LearnSmart AI - Authentication JavaScript
 * Handles login and registration form submissions with client-side validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the form element (works for both login and register pages)
    const form = document.getElementById('loginForm') || document.getElementById('registerForm');
    const messageDiv = document.getElementById('message');
    
    if (form) {
        // Client-side validation for registration form
        if (form.id === 'registerForm') {
            setupRegistrationValidation(form);
        }
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // Client-side validation
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }
            
            // Additional custom validation for registration
            if (form.id === 'registerForm') {
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirm_password').value;
                
                if (password !== confirmPassword) {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = 'Passwords do not match';
                    return;
                }
            }
            
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Determine the endpoint based on form ID
            const endpoint = form.id === 'loginForm' ? '/login' : '/register';
            
            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Processing...';
            submitButton.disabled = true;
            
            try {
                // Send POST request to the server
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams(data)
                });
                
                const result = await response.json();
                
                // Display message
                if (result.success) {
                    messageDiv.className = 'message success';
                    messageDiv.textContent = result.message;
                    
                    // Redirect after successful login/registration
                    setTimeout(() => {
                        if (result.redirect) {
                            window.location.href = result.redirect;
                        } else if (endpoint === '/login') {
                            window.location.href = '/dashboard';
                        } else {
                            // After registration, redirect to login
                            window.location.href = '/login';
                        }
                    }, 1500);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = result.message;
                }
                
            } catch (error) {
                messageDiv.className = 'message error';
                messageDiv.textContent = 'An error occurred. Please try again.';
                console.error('Error:', error);
            } finally {
                // Reset button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});

/**
 * Setup real-time validation for registration form
 */
function setupRegistrationValidation(form) {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    // Real-time password confirmation validation
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            if (this.value && this.value !== passwordInput.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
        
        passwordInput.addEventListener('input', function() {
            if (confirmPasswordInput.value && this.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity('Passwords do not match');
            } else {
                confirmPasswordInput.setCustomValidity('');
            }
        });
    }
    
    // Real-time username validation (alphanumeric and underscore only)
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            const value = this.value;
            if (value && !/^[a-zA-Z0-9_]+$/.test(value)) {
                this.setCustomValidity('Username can only contain letters, numbers, and underscores');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Real-time name validation (letters and spaces only)
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            const value = this.value;
            if (value && !/^[a-zA-Z\s]+$/.test(value)) {
                this.setCustomValidity('Name can only contain letters and spaces');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

