/* Dashboard page JavaScript */

const dashboardState = {
    allPredictions: [],
    filteredPredictions: [],
    currentPage: 1,
    pageSize: 8,
    sortBy: 'created_at',
    sortOrder: 'DESC',
    searchTerm: '',
    cropFilter: 'all',
    statusFilter: 'all',
    startDate: '',
    endDate: '',
    isLoading: true,
    pendingRefresh: false
};

const DASHBOARD_REFRESH_KEY = 'agridetect_dashboard_refresh';

window.currentPredictionId = null;

// =====================================================
// UTILITY FUNCTIONS (Fallback if main_modern.js not loaded)
// =====================================================

const dashboardEscapeHtml = window.escapeHtml || function(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
};

const dashboardFormatDate = window.formatDate || function(dateString) {
    if (!dateString) return '—';
    try {
        const date = new Date(dateString);
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('en-US', options);
    } catch (e) {
        console.warn('[Dashboard] Date format error:', e);
        return dateString;
    }
};

const dashboardFormatPercent = window.formatPercent || function(value) {
    if (typeof value === 'string') return value;
    return (parseFloat(value) * 100).toFixed(2) + '%';
};

const dashboardCapitalize = window.capitalize || function(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

const dashboardApiFetch = window.apiFetch || async function(url, options = {}) {
    console.log('[Dashboard] Using fallback apiFetch for:', url);
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
        console.error('[Dashboard] API Fetch Error:', error);
        throw error;
    }
};

// =====================================================
// CHART MANAGEMENT
// =====================================================

const dashboardVizCharts = {};
let dashboardChartResizeFrame = null;

window.addEventListener('resize', () => {
    if (dashboardChartResizeFrame) {
        cancelAnimationFrame(dashboardChartResizeFrame);
    }

    dashboardChartResizeFrame = requestAnimationFrame(() => {
        Object.values(dashboardVizCharts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', async () => {
    bindDashboardEvents();
    setupDashboardBroadcast();
    renderLoadingState();
    await loadDashboardData();
    setupChartRevealEffects();
});

function bindDashboardEvents() {
    const filterForm = document.getElementById('dashboardFilterForm');
    const searchInput = document.getElementById('searchInput');
    const cropFilter = document.getElementById('cropFilter');
    const statusFilter = document.getElementById('statusFilter');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const resetFilters = document.getElementById('resetFilters');
    const applyFiltersButton = document.getElementById('applyFilters');

    filterForm?.addEventListener('submit', event => {
        event.preventDefault();
        applyFilters();
    });

    searchInput?.addEventListener('input', () => {
        dashboardState.searchTerm = searchInput.value;
        dashboardState.currentPage = 1;
        applyFilters();
    });

    cropFilter?.addEventListener('change', () => {
        dashboardState.cropFilter = cropFilter.value;
        dashboardState.currentPage = 1;
        applyFilters();
    });

    statusFilter?.addEventListener('change', () => {
        dashboardState.statusFilter = statusFilter.value;
        dashboardState.currentPage = 1;
        applyFilters();
    });

    startDate?.addEventListener('change', () => {
        dashboardState.startDate = startDate.value;
        dashboardState.currentPage = 1;
        applyFilters();
    });

    endDate?.addEventListener('change', () => {
        dashboardState.endDate = endDate.value;
        dashboardState.currentPage = 1;
        applyFilters();
    });

    resetFilters?.addEventListener('click', resetFilterState);
    applyFiltersButton?.addEventListener('click', applyFilters);

    searchInput?.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            applyFilters();
        }
    });

    document.querySelectorAll('.table-sort-btn').forEach(button => {
        button.addEventListener('click', () => changeSort(button.dataset.sort));
    });
}

function setupDashboardBroadcast() {
    window.addEventListener('storage', event => {
        if (event.key !== DASHBOARD_REFRESH_KEY) return;
        console.log('[Dashboard] Received external refresh event:', event.newValue);
        if (document.hidden) {
            dashboardState.pendingRefresh = true;
            return;
        }
        loadDashboardData().catch(error => console.warn('[Dashboard] Refresh failed:', error));
    });

    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && dashboardState.pendingRefresh) {
            dashboardState.pendingRefresh = false;
            console.log('[Dashboard] Visible again after external update, refreshing dashboard.');
            loadDashboardData().catch(error => console.warn('[Dashboard] Visibility refresh failed:', error));
        }
    });
}

function renderLoadingState() {
    const tbody = document.getElementById('predictionsBody');
    if (tbody) {
        tbody.innerHTML = Array.from({ length: 4 }).map(() => `
            <tr class="table-skeleton-row">
                <td><span class="skeleton skeleton-line"></span></td>
                <td><span class="skeleton skeleton-pill"></span></td>
                <td><span class="skeleton skeleton-line"></span></td>
                <td><span class="skeleton skeleton-line short"></span></td>
                <td><span class="skeleton skeleton-pill"></span></td>
                <td><span class="skeleton skeleton-actions"></span></td>
            </tr>
        `).join('');
    }

    updateTableSummary(0, 0);
}

async function loadDashboardData() {
    dashboardState.isLoading = true;
    dashboardState.pendingRefresh = false;
    renderLoadingState();
    console.log('[Dashboard] ========== LOADING DASHBOARD DATA ==========');
    console.log('[Dashboard] Loading predictions from API...');

    try {
        const apiUrl = '/api/history?limit=1000&sort_by=created_at&sort_order=DESC';
        console.log('[Dashboard] API URL:', apiUrl);
        
        const response = await dashboardApiFetch(apiUrl);
        console.log('[Dashboard] ✓ API Response received:', response);
        console.log('[Dashboard] Response type:', typeof response);
        console.log('[Dashboard] Response keys:', Object.keys(response || {}));
        
        // Validate response structure
        if (!response || typeof response !== 'object') {
            throw new Error('Invalid API response format: expected object, got ' + typeof response);
        }
        
        if (response.success !== true) {
            console.warn('[Dashboard] ⚠ API returned success=false:', response);
        }
        
        const predictions = Array.isArray(response.predictions) ? response.predictions : [];
        console.log('[Dashboard] ✓ Predictions array extracted, count:', predictions.length);
        
        if (predictions.length > 0) {
            console.log('[Dashboard] First prediction sample:', predictions[0]);
            console.log('[Dashboard] Last prediction sample:', predictions[predictions.length - 1]);
        }
        
        dashboardState.allPredictions = predictions;
        dashboardState.currentPage = 1;
        dashboardState.isLoading = false;
        dashboardState.lastLoadedAt = Date.now();
        
        console.log('[Dashboard] ✓ Dashboard state updated');
        console.log('[Dashboard] Total predictions stored:', dashboardState.allPredictions.length);
        
        applyFilters();
        console.log('[Dashboard] ✓ Filters applied, rendering...');
        console.log('[Dashboard] ========== DASHBOARD LOAD COMPLETE ==========');
    } catch (error) {
        dashboardState.isLoading = false;
        console.error('[Dashboard] ✗ ERROR loading dashboard data:', error);
        console.error('[Dashboard] Error message:', error.message);
        console.error('[Dashboard] Stack:', error.stack);
        const tbody = document.getElementById('predictionsBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-5">
                        <i class="fas fa-triangle-exclamation fa-2x mb-3"></i>
                        <div>Unable to load dashboard data.</div>
                    </td>
                </tr>
            `;
        }
    }
}

function resetFilterState() {
    dashboardState.searchTerm = '';
    dashboardState.cropFilter = 'all';
    dashboardState.statusFilter = 'all';
    dashboardState.startDate = '';
    dashboardState.endDate = '';
    dashboardState.currentPage = 1;
    dashboardState.sortBy = 'created_at';
    dashboardState.sortOrder = 'DESC';

    const searchInput = document.getElementById('searchInput');
    const cropFilter = document.getElementById('cropFilter');
    const statusFilter = document.getElementById('statusFilter');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');

    if (searchInput) searchInput.value = '';
    if (cropFilter) cropFilter.value = 'all';
    if (statusFilter) statusFilter.value = 'all';
    if (startDate) startDate.value = '';
    if (endDate) endDate.value = '';

    document.querySelectorAll('.table-sort-btn').forEach(button => {
        const isActive = button.dataset.sort === dashboardState.sortBy;
        button.classList.toggle('active', isActive);
        button.classList.toggle('sort-desc', isActive && dashboardState.sortOrder === 'DESC');
    });

    applyFilters();
}

async function refreshDashboard() {
    console.log('[Dashboard] Refreshing dashboard data...');
    await loadDashboardData();
    console.log('[Dashboard] Dashboard refresh complete');
}

window.refreshDashboard = refreshDashboard;

function applyFilters() {
    console.log('[Dashboard] ===== APPLYING FILTERS =====');
    const search = dashboardState.searchTerm.trim().toLowerCase();
    let filtered = [...dashboardState.allPredictions];
    console.log('[Dashboard] Starting with total predictions:', filtered.length);

    if (dashboardState.cropFilter && dashboardState.cropFilter !== 'all') {
        const oldLength = filtered.length;
        filtered = filtered.filter(prediction => (prediction.crop || '').toLowerCase() === dashboardState.cropFilter.toLowerCase());
        console.log(`[Dashboard] After crop filter (${dashboardState.cropFilter}): ${oldLength} -> ${filtered.length}`);
    }

    if (dashboardState.statusFilter === 'healthy') {
        const oldLength = filtered.length;
        filtered = filtered.filter(prediction => (prediction.disease || '').toLowerCase().includes('healthy'));
        console.log(`[Dashboard] After healthy status filter: ${oldLength} -> ${filtered.length}`);
    } else if (dashboardState.statusFilter === 'diseased') {
        const oldLength = filtered.length;
        filtered = filtered.filter(prediction => !(prediction.disease || '').toLowerCase().includes('healthy'));
        console.log(`[Dashboard] After diseased status filter: ${oldLength} -> ${filtered.length}`);
    }

    if (dashboardState.startDate) {
        const oldLength = filtered.length;
        const startBoundary = new Date(`${dashboardState.startDate}T00:00:00`);
        filtered = filtered.filter(prediction => prediction.created_at && new Date(prediction.created_at) >= startBoundary);
        console.log(`[Dashboard] After start date filter: ${oldLength} -> ${filtered.length}`);
    }

    if (dashboardState.endDate) {
        const oldLength = filtered.length;
        const endBoundary = new Date(`${dashboardState.endDate}T23:59:59`);
        filtered = filtered.filter(prediction => prediction.created_at && new Date(prediction.created_at) <= endBoundary);
        console.log(`[Dashboard] After end date filter: ${oldLength} -> ${filtered.length}`);
    }

    if (search) {
        const oldLength = filtered.length;
        filtered = filtered.filter(prediction => {
            const dateText = (prediction.created_at || '').toLowerCase();
            const confidenceText = (prediction.confidence_percent || '').toLowerCase();
            return [prediction.crop, prediction.disease, dateText, confidenceText, String(prediction.confidence || '')]
                .some(value => (value || '').toLowerCase().includes(search));
        });
        console.log(`[Dashboard] After search filter: ${oldLength} -> ${filtered.length}`);
    }

    filtered.sort((left, right) => {
        const sortKey = dashboardState.sortBy;
        const orderMultiplier = dashboardState.sortOrder === 'ASC' ? 1 : -1;

        if (sortKey === 'confidence') {
            return (parseFloat(left.confidence || 0) - parseFloat(right.confidence || 0)) * orderMultiplier;
        }

        if (sortKey === 'created_at') {
            return (new Date(left.created_at || 0) - new Date(right.created_at || 0)) * orderMultiplier;
        }

        const valueA = (left[sortKey] || '').toString().toLowerCase();
        const valueB = (right[sortKey] || '').toString().toLowerCase();
        return valueA.localeCompare(valueB) * orderMultiplier;
    });

    dashboardState.filteredPredictions = filtered;
    const totalPages = Math.ceil(filtered.length / dashboardState.pageSize) || 1;
    dashboardState.currentPage = Math.min(dashboardState.currentPage, totalPages);

    console.log('[Dashboard] Final filtered count:', filtered.length);
    console.log('[Dashboard] Total pages:', totalPages);
    console.log('[Dashboard] ===== RENDERING TABLE =====');
    
    renderPredictionTable();
    renderPagination();
    renderDashboardMetrics();
    window.requestAnimationFrame(() => renderCharts());
    updateFilterSummary();
    
    console.log('[Dashboard] ===== FILTER APPLICATION COMPLETE =====');
}

function renderPredictionTable() {
    const tbody = document.getElementById('predictionsBody');
    if (!tbody) {
        console.error('[Dashboard] ✗ ERROR: tbody#predictionsBody not found in DOM!');
        return;
    }
    
    console.log('[Dashboard] ✓ Found tbody element');

    const start = (dashboardState.currentPage - 1) * dashboardState.pageSize;
    const end = start + dashboardState.pageSize;
    const pageItems = dashboardState.filteredPredictions.slice(start, end);

    console.log(`[Dashboard] Rendering page ${dashboardState.currentPage}: items ${start}-${end} of ${dashboardState.filteredPredictions.length}`);
    console.log(`[Dashboard] Page items to render: ${pageItems.length}`);

    if (!pageItems.length) {
        console.log('[Dashboard] ℹ No items to render, showing empty state');
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state-row text-center py-5">
                    <div class="empty-state-icon"><i class="fas fa-filter-circle-xmark"></i></div>
                    <h4 class="mb-2">No matching predictions</h4>
                    <p class="text-muted mb-0">Adjust the search or filters to reveal history entries.</p>
                </td>
            </tr>
        `;
        updateTableSummary(0, dashboardState.filteredPredictions.length);
        return;
    }

    // Destroy existing charts before updating table
    Object.keys(dashboardVizCharts).forEach(chartId => {
        destroyDashboardChart(chartId);
    });
    
    console.log('[Dashboard] Building HTML for ' + pageItems.length + ' predictions...');
    
    try {
        tbody.innerHTML = pageItems.map((prediction, index) => {
            const diseaseName = prediction.disease || 'Unknown';
            const cropName = prediction.crop || 'Unknown';
            const statusClass = getStatusClass(diseaseName);
            const indicatorClass = getDiseaseIndicatorClass(diseaseName);
            const confidenceValue = Math.max(0, Math.min(100, parseFloat(prediction.confidence || 0) * 100 || 0));

            if (index === 0) {
                console.log('[Dashboard] Rendering prediction sample:', {
                    id: prediction.id,
                    disease: diseaseName,
                    crop: cropName,
                    confidence: prediction.confidence,
                    created_at: prediction.created_at
                });
            }

            return `
                <tr>
                    <td>
                        <div class="table-date-cell">
                            <span class="table-date-main">${dashboardFormatDate(prediction.created_at)}</span>
                        </div>
                    </td>
                    <td>
                        <span class="crop-chip crop-${cropName.toLowerCase()}">
                            <i class="fas fa-seedling"></i>
                            ${dashboardCapitalize(cropName)}
                        </span>
                    </td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <span class="disease-indicator ${indicatorClass}"></span>
                            <span class="table-disease-name">${dashboardEscapeHtml(diseaseName)}</span>
                        </div>
                    </td>
                    <td>
                        <div class="confidence-chip">
                            <span class="confidence-value">${prediction.confidence_percent || dashboardFormatPercent(prediction.confidence || 0)}</span>
                            <span class="confidence-track"><span style="width: ${confidenceValue}%"></span></span>
                        </div>
                    </td>
                    <td>
                        <span class="status-badge ${statusClass}">${statusLabel(diseaseName)}</span>
                    </td>
                    <td>
                        <div class="action-group">
                            <button class="btn btn-outline-primary btn-sm action-btn" type="button" onclick="viewPrediction(${prediction.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-secondary btn-sm action-btn" type="button" onclick="window.downloadPredictionReport(${prediction.id})">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
        
        console.log('[Dashboard] ✓ HTML rendered successfully');
    } catch (renderError) {
        console.error('[Dashboard] ✗ ERROR rendering rows:', renderError);
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger py-5">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <div>Error rendering table: ${dashboardEscapeHtml(renderError.message)}</div>
                </td>
            </tr>
        `;
        return;
    }

    updateTableSummary(pageItems.length, dashboardState.filteredPredictions.length);
    console.log('[Dashboard] ✓ Table render complete');
}

function updateTableSummary(visibleCount, totalCount) {
    const info = document.getElementById('tableSummary');
    const resultsInfo = document.getElementById('tableResultsInfo');
    const totalPages = Math.ceil(totalCount / dashboardState.pageSize) || 1;

    if (info) {
        info.textContent = `${totalCount} records matched · Page ${dashboardState.currentPage} of ${totalPages}`;
    }

    if (resultsInfo) {
        resultsInfo.textContent = `${visibleCount} visible of ${totalCount}`;
    }
}

function updateFilterSummary() {
    const filterSummary = document.getElementById('filterSummary');
    if (!filterSummary) return;

    const summaryParts = [];
    if (dashboardState.cropFilter !== 'all') summaryParts.push(dashboardCapitalize(dashboardState.cropFilter));
    if (dashboardState.statusFilter !== 'all') summaryParts.push(dashboardCapitalize(dashboardState.statusFilter));
    if (dashboardState.searchTerm) summaryParts.push(`"${dashboardState.searchTerm}"`);
    filterSummary.textContent = summaryParts.length ? `Active filters: ${summaryParts.join(' · ')}` : 'All filters cleared';
}

function renderPagination() {
    const container = document.getElementById('paginationContainer');
    if (!container) return;

    const totalPages = Math.ceil(dashboardState.filteredPredictions.length / dashboardState.pageSize) || 1;
    container.innerHTML = '';

    if (totalPages <= 1) {
        container.appendChild(buildPageItem(1, '1', true, true));
        return;
    }

    container.appendChild(buildPageItem(dashboardState.currentPage - 1, '‹', false, dashboardState.currentPage === 1));

    const pages = getVisiblePages(totalPages, dashboardState.currentPage);
    pages.forEach(page => {
        if (page === '...') {
            const li = document.createElement('li');
            li.className = 'page-item disabled';
            li.innerHTML = '<span class="page-link">…</span>';
            container.appendChild(li);
            return;
        }

        container.appendChild(buildPageItem(page, String(page), dashboardState.currentPage === page, false));
    });

    container.appendChild(buildPageItem(dashboardState.currentPage + 1, '›', false, dashboardState.currentPage === totalPages));
}

function buildPageItem(page, label, active = false, disabled = false) {
    const li = document.createElement('li');
    li.className = `page-item ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`.trim();

    const button = document.createElement('a');
    button.className = 'page-link';
    button.href = '#';
    button.textContent = label;

    button.addEventListener('click', event => {
        event.preventDefault();
        const totalPages = Math.ceil(dashboardState.filteredPredictions.length / dashboardState.pageSize) || 1;
        if (!disabled && page >= 1 && page <= totalPages && dashboardState.currentPage !== page) {
            dashboardState.currentPage = page;
            renderPredictionTable();
            renderPagination();
            scrollTableIntoView();
        }
    });

    li.appendChild(button);
    return li;
}

function getVisiblePages(totalPages, currentPage) {
    if (totalPages <= 5) {
        return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    const pages = [1];
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);

    if (start > 2) pages.push('...');
    for (let page = start; page <= end; page += 1) {
        pages.push(page);
    }
    if (end < totalPages - 1) pages.push('...');
    pages.push(totalPages);
    return pages;
}

function scrollTableIntoView() {
    const tableShell = document.querySelector('.dashboard-table-shell');
    if (tableShell && typeof tableShell.scrollIntoView === 'function') {
        tableShell.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function changeSort(sortKey) {
    if (dashboardState.sortBy === sortKey) {
        dashboardState.sortOrder = dashboardState.sortOrder === 'ASC' ? 'DESC' : 'ASC';
    } else {
        dashboardState.sortBy = sortKey;
        dashboardState.sortOrder = 'ASC';
    }

    document.querySelectorAll('.table-sort-btn').forEach(button => {
        const isActive = button.dataset.sort === dashboardState.sortBy;
        button.classList.toggle('active', isActive);
        button.classList.toggle('sort-desc', isActive && dashboardState.sortOrder === 'DESC');
    });

    applyFilters();
}

function renderDashboardMetrics() {
    const predictions = dashboardState.filteredPredictions;
    const total = predictions.length;
    const healthy = predictions.filter(prediction => (prediction.disease || '').toLowerCase().includes('healthy')).length;
    const diseased = total - healthy;
    const averageConfidence = total > 0
        ? (predictions.reduce((sum, prediction) => sum + parseFloat(prediction.confidence || 0), 0) / total) * 100
        : 0;

    const diseaseCounts = predictions.reduce((counts, prediction) => {
        const key = prediction.disease || 'Unknown';
        counts[key] = (counts[key] || 0) + 1;
        return counts;
    }, {});

    const cropCounts = predictions.reduce((counts, prediction) => {
        const key = prediction.crop || 'Unknown';
        counts[key] = (counts[key] || 0) + 1;
        return counts;
    }, {});

    const mostCommonDisease = Object.entries(diseaseCounts).sort((left, right) => right[1] - left[1])[0];
    const mostCommonCrop = Object.entries(cropCounts).sort((left, right) => right[1] - left[1])[0];

    animateMetric('totalPreds', total, { decimals: 0 });
    animateMetric('healthyCount', healthy, { decimals: 0 });
    animateMetric('diseaseCount', diseased, { decimals: 0 });
    animateMetric('avgConfidence', averageConfidence, { decimals: 1, suffix: '%' });

    setMetricText('commonDisease', mostCommonDisease ? mostCommonDisease[0] : '—');
    setMetricText('commonCrop', mostCommonCrop ? dashboardCapitalize(mostCommonCrop[0]) : '—');
}

function animateMetric(elementId, value, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const decimals = Number.isInteger(options.decimals) ? options.decimals : 0;
    const suffix = options.suffix || '';
    const duration = 650;
    const startValue = 0;
    const endValue = Number.isFinite(value) ? value : 0;
    const startTime = performance.now();

    const step = currentTime => {
        const elapsed = Math.min((currentTime - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - elapsed, 3);
        const displayValue = startValue + (endValue - startValue) * eased;
        element.textContent = `${displayValue.toFixed(decimals)}${suffix}`;

        if (elapsed < 1) {
            requestAnimationFrame(step);
        }
    };

    requestAnimationFrame(step);
}

function setMetricText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

function renderCharts() {
    const predictions = dashboardState.filteredPredictions;

    const cropCounts = predictions.reduce((counts, prediction) => {
        const key = prediction.crop || 'Unknown';
        counts[key] = (counts[key] || 0) + 1;
        return counts;
    }, {});

    const diseaseCounts = predictions.reduce((counts, prediction) => {
        const key = prediction.disease || 'Unknown';
        counts[key] = (counts[key] || 0) + 1;
        return counts;
    }, {});

    const healthyCount = predictions.filter(prediction => (prediction.disease || '').toLowerCase().includes('healthy')).length;
    const diseasedCount = predictions.length - healthyCount;

    const timeSeries = predictions
        .slice()
        .sort((left, right) => new Date(left.created_at || 0) - new Date(right.created_at || 0))
        .reduce((series, prediction) => {
            if (!prediction.created_at) return series;
            const dateKey = new Date(prediction.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            series[dateKey] = (series[dateKey] || 0) + 1;
            return series;
        }, {});

    renderChartState('cropDistributionChart', Object.keys(cropCounts).length > 0);
    renderChartState('healthDoughnutChart', predictions.length > 0);
    renderChartState('diseaseFrequencyChart', Object.keys(diseaseCounts).length > 0);
    renderChartState('predictionsLineChart', Object.keys(timeSeries).length > 0);

    createPremiumPieChart(
        'cropDistributionChart',
        Object.keys(cropCounts),
        Object.values(cropCounts),
        'Crop Distribution'
    );

    createPremiumDoughnutChart(
        'healthDoughnutChart',
        ['Healthy', 'Diseased'],
        [healthyCount, diseasedCount],
        'Health Ratio'
    );

    const sortedDiseases = Object.entries(diseaseCounts)
        .sort((left, right) => right[1] - left[1])
        .slice(0, 8);

    createPremiumBarChart(
        'diseaseFrequencyChart',
        sortedDiseases.map(row => row[0]),
        sortedDiseases.map(row => row[1]),
        'Disease Frequency',
        'Detections'
    );

    createPremiumLineChart(
        'predictionsLineChart',
        Object.keys(timeSeries),
        Object.values(timeSeries),
        'Predictions Over Time'
    );
}
function getDashboardCanvas(canvasId) {
    return document.getElementById(canvasId);
}

function destroyDashboardChart(canvasId) {
    const canvas = getDashboardCanvas(canvasId);
    const existingChart = dashboardVizCharts[canvasId] || (typeof Chart !== 'undefined' && typeof Chart.getChart === 'function' && canvas ? Chart.getChart(canvas) : null);

    if (existingChart && typeof existingChart.destroy === 'function') {
        existingChart.destroy();
    }

    dashboardVizCharts[canvasId] = null;
}

function registerDashboardChart(canvasId, chart) {
    dashboardVizCharts[canvasId] = chart;
    return chart;
}

function getDashboardGradient(canvas, topColor, bottomColor) {
    const ctx = canvas.getContext('2d');
    const height = canvas.parentElement?.clientHeight || canvas.height || 320;
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, topColor);
    gradient.addColorStop(1, bottomColor);
    return gradient;
}

function buildPremiumTooltipOptions() {
    return {
        backgroundColor: 'rgba(4, 9, 20, 0.96)',
        borderColor: 'rgba(46, 196, 255, 0.28)',
        borderWidth: 1,
        titleColor: '#ffffff',
        bodyColor: '#dbeafe',
        padding: 14,
        cornerRadius: 14,
        displayColors: true,
        usePointStyle: true,
        boxPadding: 5,
        titleFont: {
            family: 'Poppins, sans-serif',
            size: 13,
            weight: '700'
        },
        bodyFont: {
            family: 'Poppins, sans-serif',
            size: 12,
            weight: '600'
        }
    };
}

function buildPremiumLegendOptions(position = 'bottom', showLegend = true) {
    return {
        display: showLegend,
        position,
        labels: {
            color: '#dbeafe',
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 18,
            boxWidth: 10,
            boxHeight: 10,
            font: {
                family: 'Poppins, sans-serif',
                size: 12,
                weight: '600'
            }
        }
    };
}

function buildPremiumCartesianOptions({ horizontal = false, showLegend = false, legendPosition = 'bottom' } = {}) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        resizeDelay: 120,
        animation: {
            duration: 1100,
            easing: 'easeOutQuart'
        },
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: buildPremiumLegendOptions(legendPosition, showLegend),
            tooltip: buildPremiumTooltipOptions()
        },
        layout: {
            padding: {
                top: 10,
                right: 12,
                bottom: 10,
                left: 10
            }
        },
        scales: horizontal ? {
            x: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(148, 163, 184, 0.14)'
                },
                ticks: {
                    color: '#cbd5e1',
                    precision: 0,
                    font: {
                        family: 'Poppins, sans-serif',
                        weight: '600'
                    }
                }
            },
            y: {
                grid: {
                    display: false
                },
                ticks: {
                    color: '#e2e8f0',
                    font: {
                        family: 'Poppins, sans-serif',
                        weight: '600'
                    }
                }
            }
        } : {
            x: {
                grid: {
                    color: 'rgba(148, 163, 184, 0.12)'
                },
                ticks: {
                    color: '#cbd5e1',
                    font: {
                        family: 'Poppins, sans-serif',
                        weight: '600'
                    }
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(148, 163, 184, 0.12)'
                },
                ticks: {
                    color: '#cbd5e1',
                    precision: 0,
                    font: {
                        family: 'Poppins, sans-serif',
                        weight: '600'
                    }
                }
            }
        }
    };
}

function renderChartState(canvasId, hasData) {
    const canvas = document.getElementById(canvasId);
    const emptyState = document.getElementById(`${canvasId}Empty`);

    if (canvas) {
        canvas.classList.toggle('is-empty', !hasData);
    }

    if (emptyState) {
        emptyState.classList.toggle('d-none', hasData);
    }
}

function createPremiumLineChart(canvasId, labels, data, title = '') {
    const canvas = getDashboardCanvas(canvasId);
    if (!canvas) return null;

    destroyDashboardChart(canvasId);

    const hasData = labels.length > 0 && data.length > 0;
    const chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: hasData ? labels : ['No data'],
            datasets: [{
                label: title || 'Predictions',
                data: hasData ? data : [0],
                backgroundColor: getDashboardGradient(canvas, 'rgba(46, 196, 255, 0.34)', 'rgba(46, 196, 255, 0.02)'),
                borderColor: 'rgba(46, 196, 255, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.42,
                pointRadius: hasData ? 3.5 : 0,
                pointHoverRadius: 7,
                pointHitRadius: 20,
                pointBorderWidth: 2,
                pointBackgroundColor: '#07101f',
                pointBorderColor: 'rgba(46, 196, 255, 1)',
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderColor: '#7df9ff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            animation: {
                duration: 1100,
                easing: 'easeOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            layout: {
                padding: {
                    top: 10,
                    right: 12,
                    bottom: 10,
                    left: 10
                }
            },
            plugins: {
                legend: buildPremiumLegendOptions('bottom', false),
                tooltip: {
                    ...buildPremiumTooltipOptions(),
                    callbacks: {
                        label(context) {
                            return `Predictions: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.10)'
                    },
                    ticks: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Poppins, sans-serif',
                            weight: '600'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: Math.max(1, ...(hasData ? data : [1])),
                    ticks: {
                        precision: 0,
                        color: '#cbd5e1',
                        font: {
                            family: 'Poppins, sans-serif',
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.12)'
                    }
                }
            }
        }
    });

    return registerDashboardChart(canvasId, chart);
}

function createPremiumDoughnutChart(canvasId, labels, data, title = '') {
    const canvas = getDashboardCanvas(canvasId);
    if (!canvas) return null;

    destroyDashboardChart(canvasId);

    const hasData = data.some(value => Number(value) > 0);
    const chart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: hasData ? labels : ['No data'],
            datasets: [{
                data: hasData ? data : [1],
                backgroundColor: hasData
                    ? [
                        'rgba(61, 220, 132, 0.96)',
                        'rgba(46, 196, 255, 0.90)'
                    ]
                    : ['rgba(148, 163, 184, 0.30)'],
                borderColor: 'rgba(7, 14, 28, 0.92)',
                borderWidth: 3,
                hoverOffset: 12,
                radius: '88%',
                cutout: '68%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            animation: {
                duration: 1100,
                easing: 'easeOutQuart'
            },
            layout: {
                padding: {
                    top: 12,
                    right: 14,
                    bottom: 10,
                    left: 14
                }
            },
            plugins: {
                legend: buildPremiumLegendOptions('bottom', true),
                tooltip: {
                    ...buildPremiumTooltipOptions(),
                    callbacks: {
                        label(context) {
                            const value = Number(context.parsed) || 0;
                            const total = context.dataset.data.reduce((sum, item) => sum + Number(item || 0), 0) || 1;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    return registerDashboardChart(canvasId, chart);
}

function createPremiumPieChart(canvasId, labels, data, title = '') {
    const canvas = getDashboardCanvas(canvasId);
    if (!canvas) return null;

    destroyDashboardChart(canvasId);

    const hasData = labels.length > 0 && data.some(value => Number(value) > 0);
    const chart = new Chart(canvas, {
        type: 'pie',
        data: {
            labels: hasData ? labels : ['No data'],
            datasets: [{
                data: hasData ? data : [1],
                backgroundColor: hasData
                    ? [
                        'rgba(46, 196, 255, 0.96)',
                        'rgba(61, 220, 132, 0.94)',
                        'rgba(78, 161, 255, 0.92)',
                        'rgba(139, 92, 246, 0.92)',
                        'rgba(251, 191, 36, 0.88)'
                    ]
                    : ['rgba(148, 163, 184, 0.30)'],
                borderColor: 'rgba(7, 14, 28, 0.92)',
                borderWidth: 3,
                hoverOffset: 12,
                radius: '88%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            animation: {
                duration: 1100,
                easing: 'easeOutQuart'
            },
            layout: {
                padding: {
                    top: 12,
                    right: 12,
                    bottom: 12,
                    left: 12
                }
            },
            plugins: {
                legend: buildPremiumLegendOptions('bottom', true),
                tooltip: {
                    ...buildPremiumTooltipOptions(),
                    callbacks: {
                        label(context) {
                            const value = Number(context.parsed) || 0;
                            const total = context.dataset.data.reduce((sum, item) => sum + Number(item || 0), 0) || 1;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    return registerDashboardChart(canvasId, chart);
}

function createPremiumBarChart(canvasId, labels, data, title = '', datasetLabel = 'Count') {
    const canvas = getDashboardCanvas(canvasId);
    if (!canvas) return null;

    destroyDashboardChart(canvasId);

    const hasData = labels.length > 0 && data.length > 0;
    const chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: hasData ? labels : ['No data'],
            datasets: [{
                label: datasetLabel,
                data: hasData ? data : [0],
                backgroundColor: hasData
                    ? 'rgba(46, 196, 255, 0.82)'
                    : 'rgba(148, 163, 184, 0.30)',
                borderColor: hasData
                    ? 'rgba(46, 196, 255, 1)'
                    : 'rgba(148, 163, 184, 0.4)',
                borderWidth: 1,
                borderRadius: 14,
                borderSkipped: false,
                barThickness: 'flex',
                maxBarThickness: 30,
                hoverBackgroundColor: hasData ? 'rgba(90, 222, 255, 0.98)' : 'rgba(148, 163, 184, 0.42)',
                hoverBorderColor: 'rgba(125, 249, 255, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 120,
            animation: {
                duration: 1100,
                easing: 'easeOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            layout: {
                padding: {
                    top: 10,
                    right: 12,
                    bottom: 10,
                    left: 10
                }
            },
            plugins: {
                legend: buildPremiumLegendOptions('bottom', false),
                tooltip: {
                    ...buildPremiumTooltipOptions(),
                    callbacks: {
                        label(context) {
                            return `${datasetLabel}: ${context.parsed.x}`;
                        }
                    }
                }
            },
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.12)'
                    },
                    ticks: {
                        color: '#cbd5e1',
                        precision: 0,
                        font: {
                            family: 'Poppins, sans-serif',
                            weight: '600'
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#e2e8f0',
                        font: {
                            family: 'Poppins, sans-serif',
                            weight: '600'
                        }
                    }
                }
            }
        }
    });

    return registerDashboardChart(canvasId, chart);
}

function setupChartRevealEffects() {
    const cards = document.querySelectorAll('.chart-card, .metric-card, .dashboard-hero-card');
    if (!('IntersectionObserver' in window) || cards.length === 0) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '0px 0px -10% 0px'
    });

    cards.forEach(card => observer.observe(card));
}

function getStatusClass(diseaseName) {
    return (diseaseName || '').toLowerCase().includes('healthy') ? 'status-healthy' : 'status-diseased';
}

function statusLabel(diseaseName) {
    return (diseaseName || '').toLowerCase().includes('healthy') ? 'Healthy' : 'Diseased';
}

function getDiseaseIndicatorClass(diseaseName) {
    const normalized = (diseaseName || '').toLowerCase();
    if (normalized.includes('healthy')) return 'indicator-healthy';
    if (normalized.includes('blight')) return 'indicator-blue';
    if (normalized.includes('rust')) return 'indicator-amber';
    if (normalized.includes('mosaic')) return 'indicator-purple';
    return 'indicator-cyan';
}

async function viewPrediction(predictionId) {
    try {
        const response = await dashboardApiFetch(`/api/prediction/${predictionId}`);
        const pred = response.prediction || response;

        if (!pred) {
            throw new Error('Prediction data missing');
        }

        window.currentPredictionId = pred.id;
        const severity = pred.severity || 'low';
        const severityClass = typeof severityBadgeClass === 'function' ? severityBadgeClass(severity) : 'severity-low';
        const severityLabelText = typeof severityBadgeLabel === 'function' ? severityBadgeLabel(severity) : dashboardCapitalize(severity);

        const modalBody = document.getElementById('predictionModalBody');
        if (modalBody) {
            const structuredAdviceHtml = typeof buildAgriculturalRecommendationSections === 'function'
                ? buildAgriculturalRecommendationSections(pred)
                : '';

            modalBody.innerHTML = `
                <div class="prediction-detail-grid">
                    <div class="prediction-preview-panel">
                        <img src="${pred.image_path}" class="img-fluid rounded-4" alt="Leaf Image">
                    </div>
                    <div class="prediction-summary-panel">
                        <div class="detail-hero">
                            <p class="section-kicker mb-2">Prediction Snapshot</p>
                            <h4 class="section-title mb-2">${dashboardEscapeHtml(pred.disease || 'Unknown Disease')}</h4>
                            <p class="text-muted mb-0">AI-generated analysis for ${dashboardCapitalize(pred.crop || 'Unknown crop')}.</p>
                        </div>
                        <div class="detail-badge-row">
                            <span class="detail-badge"><i class="fas fa-seedling"></i> ${dashboardCapitalize(pred.crop || 'Unknown')}</span>
                            <span class="detail-badge ${severityClass}">${severityLabelText}</span>
                            <span class="detail-badge"><i class="fas fa-shield-heart"></i> ${pred.confidence_percent || dashboardFormatPercent(pred.confidence || 0)}</span>
                        </div>
                        <div class="detail-info-grid">
                            <div><span>Date</span><strong>${dashboardFormatDate(pred.created_at)}</strong></div>
                            <div><span>Fertilizer</span><strong>${dashboardEscapeHtml(pred.fertilizer_recommendation || 'N/A')}</strong></div>
                            <div><span>Treatment</span><strong>${dashboardEscapeHtml(pred.treatment || pred.ai_advice || 'Not available')}</strong></div>
                            <div><span>Severity</span><strong>${severityLabelText}</strong></div>
                        </div>
                    </div>
                </div>
                ${pred.ai_advice ? `
                    <div class="ai-advice-card mt-4">
                        <div class="card-header">AI Advice</div>
                        <div class="card-body"><p>${dashboardEscapeHtml(pred.ai_advice).replace(/\n/g, '<br>')}</p></div>
                    </div>
                ` : ''}
                ${structuredAdviceHtml}
            `;
        }

        const modal = new bootstrap.Modal(document.getElementById('predictionModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading prediction details:', error);
        showAlert('Unable to load prediction details.', 'danger');
    }
}

