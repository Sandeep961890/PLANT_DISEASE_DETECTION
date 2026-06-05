/* Upload page handling */
let currentPredictionId = null;
const DASHBOARD_REFRESH_KEY = 'agridetect_dashboard_refresh';
const notify = typeof showAlert === 'function' ? showAlert : (message) => window.alert(message);

function signalDashboardRefresh() {
    try {
        const eventPayload = {
            prediction_id: currentPredictionId,
            timestamp: Date.now()
        };
        localStorage.setItem(DASHBOARD_REFRESH_KEY, JSON.stringify(eventPayload));
        console.log('[Upload] Dashboard refresh signal sent:', eventPayload);
    } catch (error) {
        console.warn('[Upload] Failed to signal dashboard refresh:', error);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const uploadArea = document.getElementById('uploadArea');
    const imageUpload = document.getElementById('imageUpload');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const predictionForm = document.getElementById('predictionForm');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsSection = document.getElementById('resultsSection');

    if (!uploadArea || !imageUpload || !predictionForm) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);
    uploadArea.addEventListener('click', () => imageUpload.click());
    imageUpload.addEventListener('change', () => {
        if (imageUpload.files.length) {
            handleFile(imageUpload.files[0]);
        }
    });

    changeImageBtn?.addEventListener('click', resetPreview);

    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!imageUpload.files.length) {
            notify('Please select a leaf image to analyze.', 'warning');
            return;
        }

        const crop = document.getElementById('crop').value;
        const includeAdvice = document.getElementById('includeAdvice').checked;

        if (!crop) {
            notify('Select a crop before submitting.', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', imageUpload.files[0]);
        formData.append('crop', crop);
        formData.append('include_advice', includeAdvice ? 'true' : 'false');

        predictionForm.classList.add('d-none');
        loadingContainer.classList.remove('d-none');

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                throw new Error(data.error || 'Prediction failed');
            }

            const data = await response.json();
            currentPredictionId = data.prediction_id;
            console.log('[Upload] Prediction successful:', data);
            displayPredictionResults(data);
            signalDashboardRefresh();
            notify('Prediction completed successfully', 'success');

            if (window.opener && typeof window.opener.refreshDashboard === 'function') {
                window.opener.refreshDashboard().catch(() => {});
            }

            console.log('[Upload] Refreshing dashboard if available...');
            if (typeof window.refreshDashboard === 'function') {
                try {
                    await window.refreshDashboard();
                    console.log('[Upload] Dashboard refreshed successfully');
                } catch (e) {
                    console.warn('[Upload] Could not refresh dashboard:', e);
                }
            }
        } catch (error) {
            console.error('[Upload] Error:', error);
            notify(error.message, 'danger');
            predictionForm.classList.remove('d-none');
            loadingContainer.classList.add('d-none');
        }
    });

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFile(files[0]);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            notify('Only image files are supported.', 'danger');
            return;
        }
        if (file.size > 50 * 1024 * 1024) {
            notify('Image must be smaller than 50MB.', 'danger');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            previewImage.src = event.target.result;
            previewContainer.classList.remove('d-none');
            previewContainer.classList.add('preview-card');
            uploadArea.classList.add('d-none');
        };
        reader.readAsDataURL(file);

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageUpload.files = dataTransfer.files;
    }

    function resetPreview() {
        imageUpload.value = '';
        previewImage.src = '';
        previewContainer.classList.add('d-none');
        uploadArea.classList.remove('d-none');
    }
});

function displayPredictionResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const loadingContainer = document.getElementById('loadingContainer');
    const predictionForm = document.getElementById('predictionForm');

    const prediction = data?.prediction || data || {};
    const safeText = (value, fallback = 'Not Available') => {
        const text = value === null || value === undefined ? '' : String(value).trim();
        return text || fallback;
    };

    const statusLabel = diseaseName => {
        return (diseaseName || '').toString().toLowerCase().includes('healthy') ? 'Healthy' : 'Diseased';
    };

    const buildFallbackAdviceCards = payload => `
        <section class="recommendation-section mt-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                <div>
                    <div class="section-kicker">Farmer Guidance</div>
                    <h4 class="mb-0">AI Advice Summary</h4>
                </div>
                <span class="severity-badge ${typeof severityBadgeClass === 'function' ? severityBadgeClass(payload.severity || 'low') : 'severity-low'}">
                    ${typeof severityBadgeLabel === 'function' ? severityBadgeLabel(payload.severity || 'low') : 'Low Severity'}
                </span>
            </div>
            <div class="row g-3">
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-clipboard-check"></i><span>Disease Summary</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.disease_summary, 'No disease summary generated.')).replace(/\n/g, '<br>')}</div></div></div>
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-cloud-rain"></i><span>Causes</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.causes, 'No causes summary generated.')).replace(/\n/g, '<br>')}</div></div></div>
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-syringe"></i><span>Treatment</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.treatment || payload.ai_advice, 'No treatment recommendation generated.')).replace(/\n/g, '<br>')}</div></div></div>
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-seedling"></i><span>Fertilizer</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.fertilizer_recommendation, 'No recommendation generated.')).replace(/\n/g, '<br>')}</div></div></div>
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-flask"></i><span>Dosage</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.dosage)).replace(/\n/g, '<br>')}</div></div></div>
                <div class="col-md-6"><div class="recommendation-card"><div class="recommendation-card__header"><i class="fas fa-shield-heart"></i><span>Prevention Tips</span></div><div class="recommendation-card__body">${escapeHtml(safeText(payload.prevention_tips, 'No prevention tips generated.')).replace(/\n/g, '<br>')}</div></div></div>
            </div>
            <div class="recovery-plan-card mt-3">
                <div class="recommendation-card__header mb-2"><i class="fas fa-calendar-check"></i><span>Recovery Plan</span></div>
                <div class="recommendation-card__body">${escapeHtml(safeText(payload.recovery_plan, 'No recovery plan generated.')).replace(/\n/g, '<br>')}</div>
            </div>
        </section>
    `;

    predictionForm?.classList.add('d-none');
    loadingContainer?.classList.add('d-none');
    resultsSection?.classList.remove('d-none');

    if (!resultsSection) {
        notify('Unable to render prediction results.', 'danger');
        return;
    }

    const confidenceValue = parseFloat(prediction.confidence || 0) * 100;
    const severity = prediction.severity || 'low';
    const severityClass = typeof severityBadgeClass === 'function' ? severityBadgeClass(severity) : 'severity-low';
    const severityLabel = typeof severityBadgeLabel === 'function' ? severityBadgeLabel(severity) : 'Low Severity';
    const fertilizerName = safeText(prediction.fertilizer_name || prediction.fertilizer_recommendation, 'Recommended fertilizer not available');
    const npkValues = safeText(prediction.npk_values, 'N/A');
    const applicationTiming = safeText(prediction.application_timing || prediction.application_schedule, 'Apply when conditions are stable, preferably in early morning.');
    const sprayingInterval = safeText(prediction.spraying_interval, 'Follow the product label or repeat every 7-10 days.');
    const organicAlternative = safeText(prediction.organic_alternative, 'Use compost, vermicompost or foliar organic extracts as a safer support option.');
    const warningHtml = severityLabel.toLowerCase().includes('high')
        ? `<div class="alert alert-warning mb-4"><i class="fas fa-exclamation-triangle"></i> High priority: apply fertilizer guidance and monitor your crop closely.</div>`
        : '';
    const structuredAdviceHtml = typeof buildAgriculturalRecommendationSections === 'function'
        ? buildAgriculturalRecommendationSections(prediction)
        : buildFallbackAdviceCards(prediction);
    const adviceText = safeText(prediction.ai_advice, 'AI advice is not available for this prediction.');

    resultsSection.innerHTML = `
        <div class="result-layout">
            <!-- LEFT PANEL: Image + Summary -->
            <section class="result-left-panel">
                <div class="glass-card preview-card image-preview">
                    <img src="${escapeHtml(prediction.image_path)}" alt="Uploaded Leaf" class="img-fluid rounded">
                </div>

                <div class="result-summary-panel">
                    <div class="section-kicker">Prediction Summary</div>
                    <h4 class="section-title">${escapeHtml(prediction.disease || 'Unknown Disease')}</h4>
                    <div class="result-summary-grid">
                        <div class="summary-item">
                            <span>Crop</span>
                            <strong>${capitalize(prediction.crop)}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Severity</span>
                            <strong>${severityLabel}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Confidence</span>
                            <strong>${prediction.confidence_percent || formatPercent(prediction.confidence || 0)}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Status</span>
                            <strong>${statusLabel(prediction.disease)}</strong>
                        </div>
                    </div>

                    <div class="confidence-block">
                        <div class="confidence-label d-flex justify-content-between align-items-center mb-2">
                            <span>Prediction Confidence</span>
                            <strong>${confidenceValue}%</strong>
                        </div>
                        <div class="confidence-bar-wrapper">
                            <div class="confidence-bar-fill" style="width: ${confidenceValue}%"></div>
                        </div>
                    </div>

                    <div class="d-flex flex-wrap gap-2 align-items-center mt-4 mb-2">
                        <span class="severity-badge ${severityClass}">${severityLabel}</span>
                        <span class="badge bg-info text-dark">${confidenceValue}% confidence</span>
                    </div>

                    <div class="action-group">
                        <button class="btn btn-glow" type="button" onclick="window.downloadPredictionReport()">
                            <i class="fas fa-download me-2"></i> Download Report
                        </button>
                        <button class="btn btn-outline-secondary" type="button" onclick="resetPredictionForm()">
                            <i class="fas fa-redo me-2"></i> Analyze Another
                        </button>
                    </div>
                </div>
            </section>

            <!-- RIGHT PANEL: Treatment Cards -->
            <section class="result-right-panel">
                <div class="treatment-card">
                    <div class="section-kicker">Fertilizer Guidance</div>
                    <h4 class="section-title">Nutrition & Treatment Plan</h4>
                    <div class="result-card-grid">
                        <article class="recommendation-card">
                            <div class="recommendation-card__header"><i class="fas fa-flask"></i> Fertilizer Blend</div>
                            <div class="recommendation-card__body">
                                <p><strong>Name:</strong> ${escapeHtml(fertilizerName)}</p>
                                <p><strong>NPK:</strong> ${escapeHtml(npkValues)}</p>
                                <p><strong>Dosage:</strong> ${escapeHtml(safeText(prediction.dosage))}</p>
                            </div>
                        </article>
                        <article class="recommendation-card">
                            <div class="recommendation-card__header"><i class="fas fa-clock"></i> Application Timing</div>
                            <div class="recommendation-card__body">
                                <p>${escapeHtml(applicationTiming)}</p>
                                <p><strong>Interval:</strong> ${escapeHtml(sprayingInterval)}</p>
                            </div>
                        </article>
                        <article class="recommendation-card prevention-card">
                            <div class="recommendation-card__header"><i class="fas fa-shield-heart"></i> Prevention Tips</div>
                            <div class="recommendation-card__body">
                                <p>${escapeHtml(safeText(prediction.prevention_tips, 'No prevention tips generated.')).replace(/\n/g, '<br>')}</p>
                            </div>
                        </article>
                        <article class="recommendation-card">
                            <div class="recommendation-card__header"><i class="fas fa-leaf"></i> Organic Alternative</div>
                            <div class="recommendation-card__body">
                                <p>${escapeHtml(organicAlternative)}</p>
                            </div>
                        </article>
                    </div>
                </div>

                <div class="glass-card p-4">
                    <div class="section-kicker">AI Agricultural Insight</div>
                    <p style="margin: 1rem 0 0 0; color: var(--text-muted); line-height: 1.7;">
                        ${escapeHtml(adviceText).replace(/\n/g, '<br>')}
                    </p>
                </div>
            </section>
        </div>

        ${structuredAdviceHtml}
    `;

}

function resetPredictionForm() {
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const predictionForm = document.getElementById('predictionForm');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsSection = document.getElementById('resultsSection');

    document.getElementById('crop').value = '';
    document.getElementById('includeAdvice').checked = true;
    document.getElementById('imageUpload').value = '';
    previewImage.src = '';
    previewContainer.classList.add('d-none');
    resultsSection.classList.add('d-none');
    predictionForm.classList.remove('d-none');
    loadingContainer.classList.add('d-none');
    window.currentPredictionId = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
