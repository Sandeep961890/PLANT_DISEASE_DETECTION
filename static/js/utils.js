/* Shared utility helpers */

if (!window.__agridetectUtilsLoaded) {
    window.__agridetectUtilsLoaded = true;

    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function showAlert(message, type = 'info', containerId = 'alertContainer') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${escapeHtml(message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        container.innerHTML = alertHtml;

        if (type !== 'danger') {
            window.setTimeout(() => {
                const alertNode = container.firstChild;
                if (alertNode) {
                    alertNode.classList.remove('show');
                }
            }, 5000);
        }
    }

    function formatDate(dateString) {
        if (!dateString) return 'Not Available';

        const date = new Date(dateString);
        if (Number.isNaN(date.getTime())) return 'Not Available';

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function capitalize(value) {
        if (value === null || value === undefined) return 'Not Available';
        const text = String(value).trim();
        if (!text) return 'Not Available';
        return text.charAt(0).toUpperCase() + text.slice(1);
    }

    function safeJsonParse(value, fallback = null) {
        if (value === null || value === undefined || value === '') return fallback;
        if (typeof value === 'object') return value;
        try {
            return JSON.parse(value);
        } catch (error) {
            console.error('safeJsonParse failed:', error);
            return fallback;
        }
    }

    window.escapeHtml = escapeHtml;
    window.showAlert = showAlert;
    window.formatDate = formatDate;
    window.capitalize = capitalize;
    window.safeJsonParse = safeJsonParse;
}