/* =====================================================
   SMART AGRICULTURAL DISEASE DETECTION
   Complete Modern JavaScript - Full Functionality
   ===================================================== */

// =====================================================
// GLOBAL VARIABLES
// ===================================================

let currentPrediction = null;
let isLoading = false;
const safeEscapeHtml = window.escapeHtml || function (value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
};

// =====================================================
// DOCUMENT READY
// ===================================================

document.addEventListener('DOMContentLoaded', function () {
    console.log("AgriDetect Application Loaded");
    initializeEventListeners();
    setupFormHandlers();
    setupNavigationHighlight();
});

// =====================================================
// UTILITY FUNCTIONS
// ===================================================

/**
 * Show notification toast
 */
function showToast(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="toast ${type}" id="${toastId}" role="alert">
            <div class="toast-body">
                <div class="d-flex align-items-center">
                    <i class="fas fa-${getIconForType(type)} me-2"></i>
                    <div>${message}</div>
                    <button type="button" class="btn-close ms-auto" data-dismiss="toast"></button>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    
    if (duration > 0) {
        setTimeout(() => {
            toastElement.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toastElement.remove(), 300);
        }, duration);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getUploadFileInput() {
    return document.getElementById('imageUpload') || document.getElementById('imageFile');
}

/**
 * Show loading spinner
 */
function showLoading(show = true) {
    let spinner = document.getElementById('loadingSpinner');
    
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.id = 'loadingSpinner';
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="spinner-content">
                <div class="spinner-border" role="status"></div>
                <p class="mt-3">Processing...</p>
            </div>
        `;
        document.body.appendChild(spinner);
    }
    
    if (show) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
    
    isLoading = show;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Format percentage
 */
function formatPercent(value) {
    if (typeof value === 'string') {
        return value;
    }
    return (parseFloat(value) * 100).toFixed(2) + '%';
}

/**
 * Capitalize string
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * API Fetch with error handling
 */
async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

function formatRecommendationText(value) {
    if (value === null || value === undefined) return '';

    return safeEscapeHtml(value)
        .replace(/\n/g, '<br>')
        .trim();
}

function severityFromConfidence(confidence) {
    const score = parseFloat(confidence || 0);
    if (score >= 0.85) return 'high';
    if (score >= 0.6) return 'moderate';
    return 'low';
}

function severityBadgeLabel(severity) {
    const normalized = (severity || '').toString().trim().toLowerCase();
    if (normalized === 'high') return 'High Severity';
    if (normalized === 'moderate') return 'Moderate Severity';
    return 'Low Severity';
}

function severityBadgeClass(severity) {
    const normalized = (severity || '').toString().trim().toLowerCase();
    if (normalized === 'high') return 'severity-high';
    if (normalized === 'moderate') return 'severity-moderate';
    return 'severity-low';
}

function recommendationCard(title, icon, value, columnClass = 'col-md-6') {
    if (!value) return '';

    return `
        <div class="${columnClass}">
            <div class="recommendation-card">
                <div class="recommendation-card__header">
                    <i class="fas fa-${icon}"></i>
                    <span>${safeEscapeHtml(title)}</span>
                </div>
                <div class="recommendation-card__body">
                    ${formatRecommendationText(value)}
                </div>
            </div>
        </div>
    `;
}

function buildAgriculturalRecommendationSections(data) {
    if (!data) return '';

    const severity = (data.severity || severityFromConfidence(data.confidence)).toString().trim().toLowerCase();
    const applicationTiming = data.application_timing || data.application_schedule || '';
    const diseaseSummary = data.disease_summary || '';
    const causes = data.causes || '';
    const treatment = data.treatment || data.ai_advice || '';
    const fertilizerRecommendation = data.fertilizer_recommendation || '';
    const dosage = data.dosage || '';
    const organicAlternative = data.organic_alternative || '';
    const preventionTips = data.prevention_tips || '';
    const recoveryPlan = data.recovery_plan || '';

    return `
        <section class="recommendation-section mt-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                <div>
                    <div class="section-kicker">Farmer Guidance</div>
                    <h4 class="mb-0">Fertilizer & Recovery Plan</h4>
                </div>
                <span class="severity-badge ${severityBadgeClass(severity)}">
                    ${severityBadgeLabel(severity)}
                </span>
            </div>

            <div class="row g-3">
                ${recommendationCard('Disease Summary', 'clipboard-check', diseaseSummary)}
                ${recommendationCard('Causes', 'cloud-rain', causes)}
                ${recommendationCard('Treatment', 'syringe', treatment)}
                ${recommendationCard('Fertilizer Recommendation', 'seedling', fertilizerRecommendation)}
                ${recommendationCard('Dosage', 'flask', dosage)}
                ${recommendationCard('Application Timing', 'clock', applicationTiming)}
                ${recommendationCard('Organic Alternative', 'leaf', organicAlternative)}
                ${recommendationCard('Prevention Tips', 'shield-heart', preventionTips)}
            </div>

            ${recoveryPlan ? `
                <div class="recovery-plan-card mt-3">
                    <div class="recommendation-card__header mb-2">
                        <i class="fas fa-calendar-check"></i>
                        <span>7-Day Recovery Plan</span>
                    </div>
                    <div class="recommendation-card__body">
                        ${formatRecommendationText(recoveryPlan)}
                    </div>
                </div>
            ` : ''}
        </section>
    `;
}

// =====================================================
// EVENT LISTENERS
// ===================================================

function initializeEventListeners() {
    // Setup drag and drop for upload areas
    const uploadAreas = document.querySelectorAll('.upload-area');
    uploadAreas.forEach(area => {
        setupDragAndDrop(area);
    });
}

function setupDragAndDrop(uploadArea) {
    const fileInput = getUploadFileInput();
    
    // Click to browse
    uploadArea.addEventListener('click', function (e) {
        if (!e.target.closest('input[type="file"]') && fileInput) {
            fileInput.click();
        }
    });

    // Drag over
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });

    // Drag leave
    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    });

    // Drop
    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && fileInput) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
}

// =====================================================
// IMAGE PREVIEW
// ===================================================

function handleImagePreview(event) {
    const file = event.target.files[0];
    
    if (!file) {
        hideImagePreview();
        return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showToast('Please select an image file', 'error');
        event.target.value = '';
        hideImagePreview();
        return;
    }

    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
        showToast('File size must be less than 50MB', 'error');
        event.target.value = '';
        hideImagePreview();
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        // Get elements
        const previewDiv = document.getElementById('imagePreview') || document.getElementById('previewImage');
        const previewContainer = document.getElementById('imagePreviewContainer') || document.getElementById('previewContainer');
        const uploadAreaContainer = document.getElementById('uploadAreaContainer') || document.getElementById('uploadArea');
        const submitBtn = document.getElementById('submitBtn') || document.querySelector('#predictionForm button[type="submit"]');
        
        // Update preview content
        if (previewDiv) {
            if (previewDiv.tagName && previewDiv.tagName.toLowerCase() === 'img') {
                previewDiv.src = e.target.result;
            } else {
                previewDiv.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" class="img-fluid rounded shadow-sm">
                    <div class="preview-overlay">
                        <span class="badge bg-success"><i class="fas fa-check"></i> Image Ready</span>
                    </div>
                `;
            }
        }
        
        // Show preview container, hide upload area
        if (previewContainer) previewContainer.style.display = 'block';
        if (uploadAreaContainer && uploadAreaContainer !== previewContainer) uploadAreaContainer.style.display = 'none';
        
        // Enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.add('pulse-animation');
        }
        
        showToast('Image selected successfully!', 'success', 2000);
    };
    
    reader.onerror = function () {
        showToast('Failed to read file', 'error');
        event.target.value = '';
        hideImagePreview();
    };
    
    reader.readAsDataURL(file);
}

function hideImagePreview() {
    const previewContainer = document.getElementById('imagePreviewContainer') || document.getElementById('previewContainer');
    const uploadAreaContainer = document.getElementById('uploadAreaContainer') || document.getElementById('uploadArea');
    const submitBtn = document.getElementById('submitBtn') || document.querySelector('#predictionForm button[type="submit"]');
    const fileInput = getUploadFileInput();
    
    if (previewContainer) previewContainer.style.display = 'none';
    if (uploadAreaContainer) uploadAreaContainer.style.display = 'flex';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.remove('pulse-animation');
    }
    if (fileInput) fileInput.value = '';
}

function showChangeImageOption() {
    const changeImageBtn = document.getElementById('changeImageBtn');
    if (changeImageBtn) {
        changeImageBtn.addEventListener('click', function (e) {
            e.preventDefault();
            hideImagePreview();
            const fileInput = getUploadFileInput();
            if (fileInput) {
                fileInput.click();
            }
        });
    }
}

// =====================================================
// FORM HANDLERS
// ===================================================

function setupFormHandlers() {
    // Image input handler
    const fileInput = document.getElementById('imageFile');
    if (fileInput) {
        fileInput.addEventListener('change', handleImagePreview);
    }
    
    // Change image button handler
    showChangeImageOption();

    // Form submission handlers
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }

    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadSubmit);
    }
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showToast('Username and password required', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            showToast('Login successful!', 'success', 2000);
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            const error = await response.json();
            showToast(error.error || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Login error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegisterSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (!username || !email || !password || !confirmPassword) {
        showToast('All fields required', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, confirm_password: confirmPassword })
        });
        
        if (response.ok) {
            showToast('Registration successful! Redirecting...', 'success', 2000);
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            const error = await response.json();
            showToast(error.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration error: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleUploadSubmit(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('imageFile');
    const cropSelect = document.getElementById('cropSelect');
    const submitBtn = document.getElementById('submitBtn');
    
    // Validation
    if (!fileInput.files || !fileInput.files.length) {
        showToast('Please select an image', 'error');
        return;
    }
    
    if (!cropSelect.value) {
        showToast('Please select a crop type', 'error');
        return;
    }
    
    // Disable button and show loading
    if (submitBtn) submitBtn.disabled = true;
    showLoading(true);
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('crop', cropSelect.value);
        formData.append('include_advice', document.getElementById('includeAdvice').checked);
        
        console.log('Sending prediction request with crop:', cropSelect.value);
        
        // Send to backend
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Prediction result:', result);
            currentPrediction = result;
            displayPredictionResults(result);
            showToast('Prediction successful!', 'success', 2000);
            
            // Reset form after successful prediction
            setTimeout(() => {
                document.getElementById('uploadForm').reset();
                hideImagePreview();
            }, 2000);
        } else {
            const error = await response.json();
            console.error('Prediction error response:', error);
            showToast(error.error || 'Prediction failed', 'error');
        }
    } catch (error) {
        console.error('Prediction exception:', error);
        showToast('Prediction error: ' + error.message, 'error');
    } finally {
        showLoading(false);
        if (submitBtn) submitBtn.disabled = false;
    }
}

// =====================================================
// PREDICTION DISPLAY
// ===================================================

function displayPredictionResults(data) {
    const resultsDiv = document.getElementById('predictionResults');
    if (!resultsDiv) return;
    
    const confidencePercent = parseFloat(data.confidence) * 100;
    const confidenceColor = confidencePercent >= 80 ? 'success' : confidencePercent >= 60 ? 'warning' : 'danger';
    
    let probabilitiesHtml = '';
    if (data.all_probabilities) {
        Object.entries(data.all_probabilities).forEach(([disease, prob]) => {
            const probPercent = parseFloat(prob) * 100;
            probabilitiesHtml += `
                <div class="probability-item">
                    <div class="probability-label">${disease}</div>
                    <div class="probability-bar-container">
                        <div class="probability-bar" style="width: ${probPercent}%">
                            ${probPercent > 5 ? probPercent.toFixed(1) + '%' : ''}
                        </div>
                    </div>
                    <div class="probability-percent">${probPercent.toFixed(1)}%</div>
                </div>
            `;
        });
    }
    
    const adviceHtml = data.ai_advice ? `
        <div class="ai-advice-card">
            <h5 class="ai-advice-title">
                <i class="fas fa-robot ai-advice-icon"></i>
                AI Expert Recommendation
            </h5>
            <div class="ai-advice-content">
                ${safeEscapeHtml(data.ai_advice).replace(/\n/g, '<br>')}
            </div>
        </div>
    ` : '';

    const recommendationHtml = buildAgriculturalRecommendationSections(data);
    
    resultsDiv.innerHTML = `
        <div class="row mt-4">
            <div class="col-lg-6">
                <div class="image-preview">
                    <img src="${data.image_path}" alt="Analyzed Image" class="img-fluid">
                </div>
            </div>
            <div class="col-lg-6">
                <div class="result-card">
                    <div class="result-disease">${data.disease}</div>
                    <div class="result-confidence">
                        Confidence: <strong>${data.confidence_percent}</strong>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill bg-${confidenceColor}" style="width: ${confidencePercent}%">
                            ${confidencePercent.toFixed(1)}%
                        </div>
                    </div>
                    <div class="mt-3">
                        <p><strong>Crop:</strong> ${capitalize(data.crop)}</p>
                        <p><strong>Analysis Date:</strong> ${formatDate(new Date())}</p>
                    </div>
                    <button class="btn btn-outline-light mt-3" onclick="savePredictionFeedback()">
                        <i class="fas fa-thumbs-up"></i> Save Analysis
                    </button>
                </div>
                
                <h5 class="mt-4 mb-3">Disease Probability Distribution</h5>
                <ul class="probability-list">
                    ${probabilitiesHtml}
                </ul>
            </div>
        </div>
        
        ${adviceHtml}

        ${recommendationHtml}
    `;
    
    // Show results and scroll into view
    resultsDiv.style.display = 'block';
    resultsDiv.classList.add('fade-in');
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// =====================================================
// NAVIGATION
// ===================================================

function setupNavigationHighlight() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || currentPath.startsWith(href + '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// =====================================================
// DASHBOARD FUNCTIONS
// ===================================================

async function loadDashboardStats() {
    try {
        const data = await apiFetch('/api/history?limit=1000');
        const predictions = data.predictions || [];
        
        const totalPreds = predictions.length;
        const healthyCount = predictions.filter(p => 
            p.disease && p.disease.toLowerCase().includes('healthy')
        ).length;
        const diseaseCount = totalPreds - healthyCount;
        const avgConfidence = totalPreds > 0
            ? (predictions.reduce((sum, p) => sum + parseFloat(p.confidence || 0), 0) / totalPreds * 100).toFixed(2)
            : 0;
        
        updateDashboardUI(totalPreds, healthyCount, diseaseCount, avgConfidence);
        
        return predictions;
    } catch (error) {
        console.error('Failed to load stats:', error);
        showToast('Failed to load statistics', 'error');
        return [];
    }
}

function updateDashboardUI(total, healthy, disease, avgConfidence) {
    const elements = {
        'totalPreds': total,
        'healthyCount': healthy,
        'diseaseCount': disease,
        'avgConfidence': avgConfidence + '%'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    });
}

// =====================================================
// CHART INITIALIZATION (Chart.js v3.9.1)
// ===================================================

const dashboardCharts = {};

async function initializeCharts() {
    try {
        const data = await apiFetch('/api/history?limit=1000');
        const predictions = data.predictions || [];
        
        // Count crops and diseases
        const cropCounts = {};
        const diseaseCounts = {};
        
        predictions.forEach(pred => {
            cropCounts[pred.crop] = (cropCounts[pred.crop] || 0) + 1;
            diseaseCounts[pred.disease] = (diseaseCounts[pred.disease] || 0) + 1;
        });
        
        // Create Pie Chart
        createPieChart(
            'cropsChart',
            Object.keys(cropCounts),
            Object.values(cropCounts),
            'Crop Distribution'
        );
        
        // Create Bar Chart
        const topDiseases = Object.entries(diseaseCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        createBarChart(
            'diseasesChart',
            topDiseases.map(d => d[0]),
            topDiseases.map(d => d[1]),
            'Top Detected Diseases'
        );
    } catch (error) {
        console.error('Failed to initialize charts:', error);
    }
}

function createPieChart(canvasId, labels, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Destroy old chart - Chart.js v3.9.1 compatibility
    if (dashboardCharts[canvasId]) {
        dashboardCharts[canvasId].destroy();
        dashboardCharts[canvasId] = null;
    }
    
    const existingChart = typeof Chart.getChart === 'function' ? Chart.getChart(ctx) : null;
    if (existingChart) {
        existingChart.destroy();
    }
    
    dashboardCharts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#00f2fe',
                    '#43e97b',
                    '#fa709a'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        color: '#dbeafe',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { family: 'Poppins, sans-serif', size: 12, weight: '600' }
                    }
                },
                title: {
                    display: true,
                    text: title,
                    color: '#f8fbff',
                    font: { size: 14, weight: '700' },
                    padding: 20
                },
                tooltip: {
                    backgroundColor: 'rgba(4, 9, 20, 0.96)',
                    borderColor: 'rgba(46, 196, 255, 0.28)',
                    borderWidth: 1,
                    titleColor: '#ffffff',
                    bodyColor: '#dbeafe',
                    padding: 14,
                    cornerRadius: 14,
                    displayColors: true
                }
            }
        }
    });
}

function createBarChart(canvasId, labels, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Destroy old chart - Chart.js v3.9.1 compatibility
    if (dashboardCharts[canvasId]) {
        dashboardCharts[canvasId].destroy();
        dashboardCharts[canvasId] = null;
    }
    
    const existingChart = typeof Chart.getChart === 'function' ? Chart.getChart(ctx) : null;
    if (existingChart) {
        existingChart.destroy();
    }
    
    dashboardCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Count',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: 'rgba(148, 163, 184, 0.12)' },
                    ticks: {
                        color: '#cbd5e1',
                        font: { family: 'Poppins, sans-serif', weight: '600' }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: '#e2e8f0',
                        font: { family: 'Poppins, sans-serif', weight: '600' }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: title,
                    color: '#f8fbff',
                    font: { size: 14, weight: '700' },
                    padding: 20
                },
                tooltip: {
                    backgroundColor: 'rgba(4, 9, 20, 0.96)',
                    borderColor: 'rgba(46, 196, 255, 0.28)',
                    borderWidth: 1,
                    titleColor: '#ffffff',
                    bodyColor: '#dbeafe',
                    padding: 14,
                    cornerRadius: 14,
                    displayColors: true
                }
            }
        }
    });
}

// =====================================================
// HISTORY TABLE
// ===================================================

async function loadPredictionHistory() {
    try {
        const data = await apiFetch('/api/history?limit=50');
        const predictions = data.predictions || [];
        const tbody = document.getElementById('predictionsBody');
        
        if (!tbody) return;
        
        if (predictions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p>No predictions yet.</p>
                        <a href="/upload" class="btn btn-sm btn-success">Make your first prediction</a>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = predictions.map(pred => `
            <tr>
                <td><small>${formatDate(pred.created_at)}</small></td>
                <td><span class="badge bg-info">${capitalize(pred.crop)}</span></td>
                <td>${pred.disease}</td>
                <td>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar" role="progressbar" 
                             style="width: ${parseFloat(pred.confidence) * 100}%">
                            ${pred.confidence_percent}
                        </div>
                    </div>
                </td>
                <td>
                    ${pred.fertilizer_recommendation ? `
                        <div class="small text-muted recommendation-snippet">
                            ${safeEscapeHtml(pred.fertilizer_recommendation.replace(/\n/g, ' ').slice(0, 120))}${pred.fertilizer_recommendation.length > 120 ? '...' : ''}
                        </div>
                    ` : '-'}
                </td>
                <td>
                    ${pred.ai_advice ? `
                        <div class="small text-muted recommendation-snippet">
                            ${safeEscapeHtml(pred.ai_advice.replace(/\n/g, ' ').slice(0, 140))}${pred.ai_advice.length > 140 ? '...' : ''}
                        </div>
                    ` : '-'}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="viewPredictionDetail(${pred.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

async function viewPredictionDetail(predictionId) {
    try {
        const data = await apiFetch(`/api/prediction/${predictionId}`);
        const pred = data.prediction;
        window.currentViewedPredictionId = predictionId;
        
        const modalBody = document.getElementById('predictionModalBody');
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <img src="${pred.image_path}" class="img-fluid rounded" alt="Leaf Image">
                    </div>
                    <div class="col-md-6">
                        <h5>Prediction Details</h5>
                        <hr>
                        <p><strong>Crop:</strong> ${capitalize(pred.crop)}</p>
                        <p><strong>Disease:</strong> ${pred.disease}</p>
                        <p><strong>Confidence:</strong> ${pred.confidence_percent}</p>
                        <p><strong>Severity:</strong> <span class="severity-badge ${severityBadgeClass(pred.severity || severityFromConfidence(pred.confidence))}">${severityBadgeLabel(pred.severity || severityFromConfidence(pred.confidence))}</span></p>
                        <p><strong>Date:</strong> ${formatDate(pred.created_at)}</p>
                        ${pred.ai_advice ? `
                            <hr>
                            <h5>AI Advice</h5>
                            <div class="border rounded p-3 bg-light" style="max-height:300px;overflow-y:auto;">
                                ${safeEscapeHtml(pred.ai_advice).replace(/\n/g, '<br>')}
                            </div>
                        ` : ''}
                    </div>
                </div>

                ${buildAgriculturalRecommendationSections(pred)}
            `;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('predictionModal'));
        modal.show();
    } catch (error) {
        showToast('Failed to load prediction details', 'error');
    }
}

// =====================================================
// EXPORT FUNCTIONS
// ===================================================

function savePredictionFeedback() {
    if (currentPrediction) {
        showToast('Analysis saved successfully!', 'success');
        setTimeout(() => {
            window.location.href = '/history';
        }, 1500);
    }
}

function downloadPredictionReport(predictionId = window.currentViewedPredictionId) {
    if (!predictionId) {
        showToast('Select a prediction first', 'warning');
        return;
    }

    window.location.href = `/download-report/${predictionId}`;
}

window.formatRecommendationText = formatRecommendationText;
window.severityFromConfidence = severityFromConfidence;
window.severityBadgeLabel = severityBadgeLabel;
window.severityBadgeClass = severityBadgeClass;
window.buildAgriculturalRecommendationSections = buildAgriculturalRecommendationSections;
window.downloadPredictionReport = downloadPredictionReport;

console.log("Chart.js version:", Chart.version);
