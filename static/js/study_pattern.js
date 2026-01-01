/**
 * LearnSmart AI - Study Pattern Analyzer JavaScript
 * Handles form submission and data display for study patterns
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default if not already set
    const dateInput = document.getElementById('study_date');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Get form element
    const form = document.getElementById('studyPatternForm');
    const messageDiv = document.getElementById('message');
    const patternIdInput = document.getElementById('pattern_id');
    const formTitle = document.getElementById('form-title');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // Client-side validation
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }
            
            // Get form data
            const formData = new FormData(form);
            const patternId = patternIdInput.value;
            
            // Show loading state
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Saving...';
            submitBtn.disabled = true;
            
            try {
                let response;
                // If pattern_id exists, update; otherwise create new
                if (patternId) {
                    // Convert FormData to JSON for PUT request
                    const data = {
                        study_date: formData.get('study_date'),
                        study_hours: formData.get('study_hours'),
                        sleep_hours: formData.get('sleep_hours'),
                        break_time: formData.get('break_time'),
                        screen_time: formData.get('screen_time'),
                        mood_level: formData.get('mood_level')
                    };
                    
                    response = await fetch(`/api/study-pattern/${patternId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                } else {
                    // Create new pattern
                    response = await fetch('/api/study-pattern', {
                        method: 'POST',
                        body: formData
                    });
                }
                
                const result = await response.json();
                
                // Display message
                if (result.success) {
                    messageDiv.className = 'message success';
                    messageDiv.textContent = result.message;
                    
                    // Reset form and cancel edit mode
                    cancelEdit();
                    
                    // Reload page after 1.5 seconds to show updated data
                    setTimeout(() => {
                        window.location.reload();
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
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
    
    // Add input validation for numeric fields
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.value = 0;
            } else if (value > 24) {
                this.value = 24;
            }
        });
    });
});

// Edit pattern function
async function editPattern(patternId) {
    try {
        const response = await fetch(`/api/study-pattern/${patternId}`);
        const result = await response.json();
        
        if (result.success) {
            const pattern = result.pattern;
            
            // Populate form with pattern data
            document.getElementById('pattern_id').value = pattern.id;
            document.getElementById('study_date').value = pattern.study_date;
            document.getElementById('study_hours').value = pattern.study_hours;
            document.getElementById('sleep_hours').value = pattern.sleep_hours;
            document.getElementById('break_time').value = pattern.break_time;
            document.getElementById('screen_time').value = pattern.screen_time;
            document.getElementById('mood_level').value = pattern.mood_level;
            
            // Update UI for edit mode
            document.getElementById('form-title').textContent = 'Edit Study Data';
            document.getElementById('submit-btn').textContent = 'Update Study Data';
            document.getElementById('cancel-btn').style.display = 'block';
            
            // Scroll to form
            document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            alert('Error loading pattern: ' + result.message);
        }
    } catch (error) {
        alert('Error loading pattern. Please try again.');
        console.error('Error:', error);
    }
}

// Delete pattern function
async function deletePattern(patternId, studyDate) {
    if (!confirm(`Are you sure you want to delete the study pattern for ${studyDate}? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/study-pattern/${patternId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Remove pattern card from UI
            const patternCard = document.querySelector(`[data-pattern-id="${patternId}"]`);
            if (patternCard) {
                patternCard.remove();
            }
            
            // Show success message
            const messageDiv = document.getElementById('message');
            messageDiv.className = 'message success';
            messageDiv.textContent = result.message;
            
            // Reload page after 1.5 seconds to refresh data
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            alert('Error deleting pattern: ' + result.message);
        }
    } catch (error) {
        alert('Error deleting pattern. Please try again.');
        console.error('Error:', error);
    }
}

// Cancel edit function
function cancelEdit() {
    // Clear form
    document.getElementById('studyPatternForm').reset();
    document.getElementById('pattern_id').value = '';
    
    // Reset UI
    document.getElementById('form-title').textContent = 'Add Daily Study Data';
    document.getElementById('submit-btn').textContent = 'Save Study Data';
    document.getElementById('cancel-btn').style.display = 'none';
    
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('study_date').value = today;
    
    // Clear message
    document.getElementById('message').textContent = '';
    document.getElementById('message').className = 'message';
}

