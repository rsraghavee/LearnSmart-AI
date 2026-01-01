/**
 * LearnSmart AI - Academic Performance Tracker JavaScript
 * Handles form submission and matrix table display
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('academicForm');
    const messageDiv = document.getElementById('message');
    
    // Load existing data
    loadAcademicPerformance();
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }
            
            const formData = new FormData(form);
            const data = {
                class_semester: formData.get('class_semester'),
                exam_name: formData.get('exam_name'),
                subject_name: formData.get('subject_name'),
                marks_scored: parseFloat(formData.get('marks_scored')),
                total_marks: parseFloat(formData.get('total_marks'))
            };
            
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Adding...';
            submitButton.disabled = true;
            
            try {
                const response = await fetch('/api/academic-performance', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    messageDiv.className = 'message success';
                    messageDiv.textContent = result.message;
                    form.reset();
                    
                    // Reload data after 1 second
                    setTimeout(() => {
                        loadAcademicPerformance();
                        messageDiv.textContent = '';
                        messageDiv.className = 'message';
                    }, 1000);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = result.message;
                }
                
            } catch (error) {
                messageDiv.className = 'message error';
                messageDiv.textContent = 'An error occurred. Please try again.';
                console.error('Error:', error);
            } finally {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});

/**
 * Load and display academic performance data in matrix format
 */
async function loadAcademicPerformance() {
    const container = document.getElementById('performance-tables');
    
    try {
        container.innerHTML = '<p class="loading-text">Loading academic performance data...</p>';
        
        const response = await fetch('/api/academic-performance');
        const result = await response.json();
        
        if (!result.success) {
            container.innerHTML = `<p class="error-text">Error: ${result.message}</p>`;
            return;
        }
        
        const data = result.data;
        
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No academic performance records found.</p>
                    <p>Add your first record using the form above!</p>
                </div>
            `;
            return;
        }
        
        // Build matrix tables for each class/semester
        let html = '';
        
        for (const [classSemester, exams] of Object.entries(data)) {
            html += buildMatrixTable(classSemester, exams);
        }
        
        container.innerHTML = html;
        
        // Add delete handlers
        attachDeleteHandlers();
        
    } catch (error) {
        container.innerHTML = '<p class="error-text">Error loading data. Please try again.</p>';
        console.error('Error:', error);
    }
}

/**
 * Build a matrix table for a class/semester
 */
function buildMatrixTable(classSemester, exams) {
    // Collect all unique subjects across all exams
    const allSubjects = new Set();
    for (const examData of Object.values(exams)) {
        for (const subject of Object.keys(examData)) {
            allSubjects.add(subject);
        }
    }
    
    const subjects = Array.from(allSubjects).sort();
    const examNames = Object.keys(exams).sort();
    
    if (subjects.length === 0 || examNames.length === 0) {
        return '';
    }
    
    let html = `
        <div class="class-section">
            <h3 class="class-title">${escapeHtml(classSemester)}</h3>
            <div class="matrix-table-wrapper">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th class="exam-col">Exam Name</th>
    `;
    
    // Add subject columns
    for (const subject of subjects) {
        html += `<th>${escapeHtml(subject)}</th>`;
    }
    
    html += `
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Add exam rows
    for (const examName of examNames) {
        html += `<tr>`;
        html += `<td class="exam-name">${escapeHtml(examName)}</td>`;
        
        for (const subject of subjects) {
            const cellData = exams[examName][subject];
            if (cellData) {
                const percentage = ((cellData.marks_scored / cellData.total_marks) * 100).toFixed(1);
                html += `
                    <td class="marks-cell" data-record-id="${cellData.id}">
                        <span class="marks-value">${cellData.marks_scored}/${cellData.total_marks}</span>
                        <span class="marks-percentage">(${percentage}%)</span>
                        <button class="delete-cell-btn" onclick="deleteRecord(${cellData.id}, '${escapeHtml(classSemester)}', '${escapeHtml(examName)}', '${escapeHtml(subject)}')" title="Delete">×</button>
                    </td>
                `;
            } else {
                html += `<td class="empty-cell">-</td>`;
            }
        }
        
        html += `</tr>`;
    }
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Delete a record
 */
async function deleteRecord(recordId, classSemester, examName, subject) {
    if (!confirm(`Are you sure you want to delete the record for ${examName} - ${subject} in ${classSemester}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/academic-performance/${recordId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reload data
            loadAcademicPerformance();
            
            // Show success message
            const messageDiv = document.getElementById('message');
            messageDiv.className = 'message success';
            messageDiv.textContent = result.message;
            
            setTimeout(() => {
                messageDiv.textContent = '';
                messageDiv.className = 'message';
            }, 2000);
        } else {
            alert('Error deleting record: ' + result.message);
        }
    } catch (error) {
        alert('Error deleting record. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Attach delete handlers (placeholder for future use)
 */
function attachDeleteHandlers() {
    // Handlers are already attached via onclick in buildMatrixTable
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


