/**
 * LearnSmart AI - History Management JavaScript
 * Handles tab switching and data loading for history page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
            
            // Load data for the active tab
            loadTabData(targetTab);
        });
    });
    
    // Load initial tab data
    loadTabData('study-patterns');
});

/**
 * Load data for the specified tab
 */
async function loadTabData(tabName) {
    switch(tabName) {
        case 'study-patterns':
            await loadStudyPatterns();
            break;
        case 'burnout-predictions':
            await loadBurnoutPredictions();
            break;
    }
}

/**
 * Load and display study patterns history
 */
async function loadStudyPatterns() {
    const tbody = document.getElementById('studyPatternsBody');
    const countBadge = document.getElementById('studyPatternsCount');
    
    try {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">Loading data...</td></tr>';
        
        const response = await fetch('/api/history/study-patterns?limit=100');
        const data = await response.json();
        
        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="7" class="error-cell">Error: ${data.message}</td></tr>`;
            return;
        }
        
        if (!data.patterns || data.patterns.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-cell">No study patterns found. Start tracking your study patterns!</td></tr>';
            countBadge.textContent = '0';
            return;
        }
        
        countBadge.textContent = data.count;
        
        let html = '';
        data.patterns.forEach(pattern => {
            const date = new Date(pattern.study_date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            
            const createdDate = new Date(pattern.created_at);
            const formattedCreated = createdDate.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const moodClass = pattern.mood_level.toLowerCase();
            
            html += `
                <tr>
                    <td>${formattedDate}</td>
                    <td>${parseFloat(pattern.study_hours).toFixed(1)}h</td>
                    <td>${parseFloat(pattern.sleep_hours).toFixed(1)}h</td>
                    <td>${parseFloat(pattern.break_time).toFixed(1)}h</td>
                    <td>${parseFloat(pattern.screen_time).toFixed(1)}h</td>
                    <td><span class="mood-badge-table mood-${moodClass}">${pattern.mood_level}</span></td>
                    <td>${formattedCreated}</td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading study patterns:', error);
        tbody.innerHTML = '<tr><td colspan="7" class="error-cell">Error loading data. Please try again.</td></tr>';
    }
}

/**
 * Load and display burnout predictions history
 */
async function loadBurnoutPredictions() {
    const tbody = document.getElementById('burnoutPredictionsBody');
    const countBadge = document.getElementById('burnoutPredictionsCount');
    
    try {
        tbody.innerHTML = '<tr><td colspan="9" class="loading-cell">Loading data...</td></tr>';
        
        const response = await fetch('/api/history/burnout-predictions?limit=100');
        const data = await response.json();
        
        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="9" class="error-cell">Error: ${data.message}</td></tr>`;
            return;
        }
        
        if (!data.predictions || data.predictions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="empty-cell">No burnout predictions found. Add study data to get predictions!</td></tr>';
            countBadge.textContent = '0';
            return;
        }
        
        countBadge.textContent = data.count;
        
        let html = '';
        data.predictions.forEach(prediction => {
            const date = new Date(prediction.study_date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            
            const createdDate = new Date(prediction.created_at);
            const formattedCreated = createdDate.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const riskClass = prediction.predicted_risk.toLowerCase();
            
            html += `
                <tr>
                    <td>${formattedDate}</td>
                    <td>${parseFloat(prediction.study_hours).toFixed(1)}h</td>
                    <td>${parseFloat(prediction.sleep_hours).toFixed(1)}h</td>
                    <td>${parseFloat(prediction.break_time).toFixed(1)}h</td>
                    <td>${parseFloat(prediction.screen_time).toFixed(1)}h</td>
                    <td>${prediction.mood_score}/10</td>
                    <td><span class="risk-badge-table risk-${riskClass}">${prediction.predicted_risk}</span></td>
                    <td>${parseFloat(prediction.confidence || 0).toFixed(1)}%</td>
                    <td>${formattedCreated}</td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading burnout predictions:', error);
        tbody.innerHTML = '<tr><td colspan="9" class="error-cell">Error loading data. Please try again.</td></tr>';
    }
}

