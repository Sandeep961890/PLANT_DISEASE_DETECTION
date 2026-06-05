/* Futuristic UI Core Utilities */

if (typeof Chart !== 'undefined' && !window.__agridetectChartDefaultsApplied) {
    window.__agridetectChartDefaultsApplied = true;
    Chart.defaults.color = '#d8e6f3';
    Chart.defaults.font.family = 'Poppins, sans-serif';
    if (Chart.defaults.plugins && Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.boxWidth = 10;
        Chart.defaults.plugins.legend.labels.boxHeight = 10;
    }
}

function getExistingChart(canvasOrId) {
    if (!canvasOrId || typeof Chart === 'undefined') return null;

    if (typeof Chart.getChart === 'function') {
        try {
            return Chart.getChart(canvasOrId);
        } catch (err) {
            // Continue to fallback if selector is invalid
        }
    }

    const canvas = typeof canvasOrId === 'string' ? document.getElementById(canvasOrId) : canvasOrId;
    if (!canvas) return null;
    return canvas.chart || null;
}

function destroyChartIfExists(canvasOrId) {
    const chart = getExistingChart(canvasOrId);
    if (chart && typeof chart.destroy === 'function') {
        chart.destroy();
    }
}

function showAlert(message, type = 'info', containerId = 'alertContainer') {
    const container = document.getElementById(containerId);
    if (!container) {
        window.alert(message);
        return;
    }

    container.innerHTML = '';

    const alertWrapper = document.createElement('div');
    alertWrapper.className = `alert alert-${type} alert-dismissible fade show`;
    alertWrapper.role = 'alert';
    alertWrapper.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.appendChild(alertWrapper);

    if (type !== 'danger') {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertWrapper);
            if (bsAlert) bsAlert.close();
        }, 4500);
    }
}

function showLoadingModal(message = 'Processing...') {
    const modal = document.getElementById('loadingModal');
    if (!modal) return;
    const body = modal.querySelector('.modal-body');
    if (body) body.textContent = message;
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function hideLoadingModal() {
    const modal = document.getElementById('loadingModal');
    if (!modal) return;
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
}

function formatDate(dateString) {
    if (!dateString) return '';
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function formatPercent(value) {
    if (value === null || value === undefined) return '0%';
    if (typeof value === 'string' && value.includes('%')) return value;
    const parsed = parseFloat(value);
    if (Number.isNaN(parsed)) return '0%';
    return `${(parsed * 100).toFixed(2)}%`;
}

function capitalize(str) {
    if (!str) return '';
    return String(str).charAt(0).toUpperCase() + String(str).slice(1);
}

function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

window.getExistingChart = getExistingChart;
window.destroyChartIfExists = destroyChartIfExists;
window.showAlert = showAlert;
window.showLoadingModal = showLoadingModal;
window.hideLoadingModal = hideLoadingModal;
window.formatDate = formatDate;
window.formatPercent = formatPercent;
window.capitalize = capitalize;
window.escapeHtml = escapeHtml;
