/**
 * LearnSmart AI - Dashboard JavaScript
 * Handles dashboard interactions, Chart.js visualizations, and dynamic content
 */

// Global chart instances
let weeklyStudyChart = null;
let sleepProductivityChart = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Initialize charts
    initializeWeeklyStudyChart();
    initializeSleepProductivityChart();
    
    // Load recent study history
    loadRecentStudyHistory();
    
    // Add animation to course cards
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

/**
 * Initialize Weekly Study Hours Chart
 * Displays study hours for the past 7 days
 */
async function initializeWeeklyStudyChart() {
    try {
        const response = await fetch('/api/dashboard/weekly-study-hours');
        const data = await response.json();
        
        if (!data.success) {
            console.error('Error loading weekly study data:', data.message);
            showChartError('weeklyStudyChart', 'Unable to load study hours data');
            return;
        }
        
        const ctx = document.getElementById('weeklyStudyChart');
        if (!ctx) return;
        
        // Format dates for display (show day name)
        const formattedDates = data.dates.map(date => {
            const d = new Date(date);
            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            return days[d.getDay()];
        });
        
        // Destroy existing chart if it exists
        if (weeklyStudyChart) {
            weeklyStudyChart.destroy();
        }
        
        weeklyStudyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: formattedDates,
                datasets: [{
                    label: 'Study Hours',
                    data: data.study_hours,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 2,
                    borderRadius: 5,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Study Hours: ${context.parsed.y.toFixed(1)}h`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 12,
                        ticks: {
                            callback: function(value) {
                                return value + 'h';
                            }
                        },
                        title: {
                            display: true,
                            text: 'Hours'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Day'
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error initializing weekly study chart:', error);
        showChartError('weeklyStudyChart', 'Error loading chart data');
    }
}

/**
 * Initialize Sleep vs Productivity Chart
 * Shows correlation between sleep hours and productivity score
 */
async function initializeSleepProductivityChart() {
    try {
        const response = await fetch('/api/dashboard/sleep-vs-productivity');
        const data = await response.json();
        
        if (!data.success) {
            console.error('Error loading sleep vs productivity data:', data.message);
            showChartError('sleepProductivityChart', 'Unable to load sleep/productivity data');
            return;
        }
        
        if (data.sleep_hours.length === 0) {
            showChartError('sleepProductivityChart', 'No data available yet');
            return;
        }
        
        const ctx = document.getElementById('sleepProductivityChart');
        if (!ctx) return;
        
        // Destroy existing chart if it exists
        if (sleepProductivityChart) {
            sleepProductivityChart.destroy();
        }
        
        sleepProductivityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates.map(date => {
                    const d = new Date(date);
                    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [
                    {
                        label: 'Sleep Hours',
                        data: data.sleep_hours,
                        borderColor: 'rgba(155, 89, 182, 1)',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Productivity Score',
                        data: data.productivity_scores,
                        borderColor: 'rgba(46, 204, 113, 1)',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y1',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    return `Sleep: ${context.parsed.y.toFixed(1)}h`;
                                } else {
                                    return `Productivity: ${context.parsed.y.toFixed(1)}/100`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        max: 12,
                        title: {
                            display: true,
                            text: 'Sleep Hours'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + 'h';
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Productivity Score'
                        },
                        ticks: {
                            callback: function(value) {
                                return value;
                            }
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error initializing sleep vs productivity chart:', error);
        showChartError('sleepProductivityChart', 'Error loading chart data');
    }
}

/**
 * Load and display recent study history
 */
async function loadRecentStudyHistory() {
    try {
        const response = await fetch('/api/study-pattern?limit=7');
        const data = await response.json();
        
        const historyList = document.getElementById('recentHistoryList');
        if (!historyList) return;
        
        if (!data.success || !data.patterns || data.patterns.length === 0) {
            historyList.innerHTML = `
                <div class="empty-history">
                    <p>No study history available yet.</p>
                    <p>Start tracking your study patterns to see your history!</p>
                    <a href="/study-pattern" class="btn btn-primary">Add Study Data</a>
                </div>
            `;
            return;
        }
        
        // Sort by date (newest first)
        const sortedPatterns = data.patterns.sort((a, b) => {
            return new Date(b.study_date) - new Date(a.study_date);
        });
        
        let html = '<div class="history-items">';
        
        sortedPatterns.forEach(pattern => {
            const date = new Date(pattern.study_date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                weekday: 'short', 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            
            // Get mood badge color
            const moodClass = pattern.mood_level.toLowerCase();
            
            html += `
                <div class="history-item">
                    <div class="history-date">${formattedDate}</div>
                    <div class="history-details">
                        <div class="history-metric">
                            <span class="metric-label">📚 Study:</span>
                            <span class="metric-value">${parseFloat(pattern.study_hours).toFixed(1)}h</span>
                        </div>
                        <div class="history-metric">
                            <span class="metric-label">😴 Sleep:</span>
                            <span class="metric-value">${parseFloat(pattern.sleep_hours).toFixed(1)}h</span>
                        </div>
                        <div class="history-metric">
                            <span class="metric-label">☕ Break:</span>
                            <span class="metric-value">${parseFloat(pattern.break_time).toFixed(1)}h</span>
                        </div>
                        <div class="history-metric">
                            <span class="metric-label">💻 Screen:</span>
                            <span class="metric-value">${parseFloat(pattern.screen_time).toFixed(1)}h</span>
                        </div>
                        <div class="history-metric">
                            <span class="metric-label">Mood:</span>
                            <span class="mood-badge-small mood-${moodClass}">${pattern.mood_level}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        historyList.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading recent study history:', error);
        const historyList = document.getElementById('recentHistoryList');
        if (historyList) {
            historyList.innerHTML = '<p class="error-text">Error loading study history. Please try again later.</p>';
        }
    }
}

/**
 * Show error message in chart container
 */
function showChartError(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (canvas && canvas.parentElement) {
        canvas.parentElement.innerHTML = `
            <div class="chart-error">
                <p>${message}</p>
                <p class="error-hint">Add more study data to see visualizations</p>
            </div>
        `;
    }
}

/**
 * Fetch courses from API (optional function)
 * Can be used to dynamically load courses
 */
async function fetchCourses() {
    try {
        const response = await fetch('/api/courses');
        const data = await response.json();
        
        if (data.success) {
            console.log('Courses loaded:', data.courses);
            // Update UI with courses if needed
        }
    } catch (error) {
        console.error('Error fetching courses:', error);
    }
}
