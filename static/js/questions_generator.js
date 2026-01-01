/**
 * LearnSmart AI - Questions Generator JavaScript
 * Handles file upload, question generation, and copy/download functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const uploadForm = document.getElementById('uploadForm');
    const uploadMessage = document.getElementById('uploadMessage');
    const generateBtn = document.getElementById('generateBtn');
    const questionsContainer = document.getElementById('questionsContainer');
    const questionsList = document.getElementById('questionsList');
    const topicsDisplay = document.getElementById('topicsDisplay');
    const copyAllBtn = document.getElementById('copyAllBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    
    let currentQuestions = [];
    
    // File input change handler
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file size (10MB)
            if (file.size > 10 * 1024 * 1024) {
                showMessage('File size exceeds 10MB limit', 'error');
                fileInput.value = '';
                return;
            }
            
            // Validate file type
            const fileExt = file.name.split('.').pop().toLowerCase();
            if (!['pdf', 'txt'].includes(fileExt)) {
                showMessage('Invalid file type. Only PDF and TXT files are allowed.', 'error');
                fileInput.value = '';
                return;
            }
            
            // Show file info
            fileName.textContent = file.name;
            fileInfo.style.display = 'flex';
            document.querySelector('.upload-prompt').style.display = 'none';
        }
    });
    
    // Remove file handler
    removeFileBtn.addEventListener('click', function() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        document.querySelector('.upload-prompt').style.display = 'block';
        uploadMessage.style.display = 'none';
    });
    
    // Drag and drop handlers
    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileUploadArea.style.borderColor = '#2980b9';
        fileUploadArea.style.backgroundColor = '#e3f2fd';
    });
    
    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileUploadArea.style.borderColor = '#3498db';
        fileUploadArea.style.backgroundColor = '#f8f9fa';
    });
    
    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        fileUploadArea.style.borderColor = '#3498db';
        fileUploadArea.style.backgroundColor = '#f8f9fa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
    
    // Form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showMessage('Please select a file', 'error');
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating Questions...';
        uploadMessage.style.display = 'none';
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/generate-questions', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                currentQuestions = result.questions;
                displayQuestions(result.questions, result.topics);
                
                // Reset form
                fileInput.value = '';
                fileInfo.style.display = 'none';
                document.querySelector('.upload-prompt').style.display = 'block';
                
                // Reload previous questions
                loadPreviousQuestions();
            } else {
                showMessage(result.message, 'error');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showMessage('An error occurred. Please try again.', 'error');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Questions';
        }
    });
    
    // Copy all questions
    copyAllBtn.addEventListener('click', function() {
        if (currentQuestions.length === 0) return;
        
        const text = currentQuestions.map((q, index) => {
            return `${index + 1}. [${q.type}] ${q.question}`;
        }).join('\n\n');
        
        navigator.clipboard.writeText(text).then(() => {
            showMessage('All questions copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Error copying:', err);
            showMessage('Failed to copy. Please try again.', 'error');
        });
    });
    
    // Download questions
    downloadBtn.addEventListener('click', function() {
        if (currentQuestions.length === 0) return;
        
        const text = currentQuestions.map((q, index) => {
            return `${index + 1}. [${q.type}] ${q.question}`;
        }).join('\n\n');
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `generated_questions_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showMessage('Questions downloaded successfully!', 'success');
    });
    
    // Display questions
    function displayQuestions(questions, topics) {
        questionsContainer.style.display = 'block';
        questionsList.innerHTML = '';
        
        // Display topics
        if (topics && topics.length > 0) {
            topicsDisplay.innerHTML = `
                <h4>Key Topics Identified:</h4>
                <div class="topics-tags">
                    ${topics.map(topic => `<span class="topic-tag">${topic}</span>`).join('')}
                </div>
            `;
        } else {
            topicsDisplay.innerHTML = '';
        }
        
        // Display questions
        questions.forEach((question, index) => {
            const questionItem = document.createElement('div');
            questionItem.className = 'question-item';
            
            const typeClass = question.type.toLowerCase().replace(/\s+/g, '-');
            
            questionItem.innerHTML = `
                <div class="question-header">
                    <span class="question-type ${typeClass}">${question.type}</span>
                </div>
                <p class="question-text">${question.question}</p>
                <div class="question-actions">
                    <button class="btn-copy-question" onclick="copyQuestion('${question.question.replace(/'/g, "\\'")}')">
                        Copy
                    </button>
                </div>
            `;
            
            questionsList.appendChild(questionItem);
        });
        
        // Scroll to questions
        questionsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Copy individual question
    window.copyQuestion = function(questionText) {
        navigator.clipboard.writeText(questionText).then(() => {
            showMessage('Question copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Error copying:', err);
            showMessage('Failed to copy. Please try again.', 'error');
        });
    };
    
    // Show message
    function showMessage(message, type) {
        uploadMessage.className = `message ${type}`;
        uploadMessage.textContent = message;
        uploadMessage.style.display = 'block';
        
        if (type === 'success') {
            setTimeout(() => {
                uploadMessage.style.display = 'none';
            }, 3000);
        }
    }
    
    // Load previous questions
    async function loadPreviousQuestions() {
        try {
            const response = await fetch('/api/user-questions?limit=10');
            const data = await response.json();
            
            const previousList = document.getElementById('previousQuestionsList');
            
            if (!data.success || !data.questions || data.questions.length === 0) {
                previousList.innerHTML = '<p class="empty-state">No previous questions found. Generate your first set of questions!</p>';
                return;
            }
            
            let html = '';
            data.questions.forEach(question => {
                const date = new Date(question.created_at);
                const formattedDate = date.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                html += `
                    <div class="previous-question-item">
                        <div class="previous-question-meta">
                            <span>${question.source_filename}</span>
                            <span>${formattedDate}</span>
                        </div>
                        <p class="previous-question-text">[${question.question_type}] ${question.question_text}</p>
                    </div>
                `;
            });
            
            previousList.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading previous questions:', error);
            document.getElementById('previousQuestionsList').innerHTML = 
                '<p class="error-text">Error loading previous questions.</p>';
        }
    }
    
    // Load previous questions on page load
    loadPreviousQuestions();
});


