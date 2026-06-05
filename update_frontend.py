from pathlib import Path

files = {
    'templates/base.html': """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{% block title %}AgriDetect – Futuristic AI Farming Dashboard{% endblock %}</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@500;700;900&family=Poppins:wght@400;500;600&display=swap\" rel=\"stylesheet\">
    <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css\">
    <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css\">
    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/style_modern.css') }}\">
    {% block extra_css %}{% endblock %}
</head>
<body class=\"futuristic-body\">
    <div class=\"background-layers\"></div>
    <div id=\"alertContainer\" class=\"alert-container\"></div>

    <nav class=\"navbar navbar-expand-lg futuristic-nav py-3\">
        <div class=\"container-fluid\">
            <a class=\"navbar-brand d-flex align-items-center gap-3\" href=\"/\">
                <span class=\"brand-icon\"><i class=\"fas fa-microscope\"></i></span>
                <div>
                    <div class=\"brand-title\">AgriDetect</div>
                    <div class=\"brand-subtitle\">AI Smart Farming</div>
                </div>
            </a>
            <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#navbarNav\" aria-controls=\"navbarNav\" aria-expanded=\"false\" aria-label=\"Toggle navigation\">
                <span class=\"navbar-toggler-icon\"></span>
            </button>
            <div class=\"collapse navbar-collapse\" id=\"navbarNav\">
                <ul class=\"navbar-nav ms-auto align-items-lg-center\">
                    {% if current_user %}
                        <li class=\"nav-item\">
                            <a class=\"nav-link\" href=\"/dashboard\"><i class=\"fas fa-chart-line\"></i> Dashboard</a>
                        </li>
                        <li class=\"nav-item\">
                            <a class=\"nav-link\" href=\"/upload\"><i class=\"fas fa-cloud-upload-alt\"></i> Predict</a>
                        </li>
                        <li class=\"nav-item\">
                            <a class=\"nav-link\" href=\"/advisor\"><i class=\"fas fa-robot\"></i> AI Advisor</a>
                        </li>
                        <li class=\"nav-item dropdown\">
                            <a class=\"nav-link dropdown-toggle\" href=\"#\" id=\"userDropdown\" role=\"button\" data-bs-toggle=\"dropdown\" aria-expanded=\"false\">
                                <i class=\"fas fa-user-circle\"></i> {{ current_user.username }}
                            </a>
                            <ul class=\"dropdown-menu dropdown-menu-end futuristic-dropdown\" aria-labelledby=\"userDropdown\">
                                <li><a class=\"dropdown-item\" href=\"/profile\">Profile</a></li>
                                <li><a class=\"dropdown-item\" href=\"/history\">History</a></li>
                                <li><hr class=\"dropdown-divider\"></li>
                                <li><a class=\"dropdown-item\" href=\"/logout\">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class=\"nav-item\">
                            <a class=\"nav-link\" href=\"/login\"><i class=\"fas fa-sign-in-alt\"></i> Login</a>
                        </li>
                        <li class=\"nav-item\">
                            <a class=\"nav-link\" href=\"/register\"><i class=\"fas fa-user-plus\"></i> Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class=\"page-content\">
        {% block content %}{% endblock %}
    </main>

    <footer class=\"futuristic-footer py-5\">
        <div class=\"container\">
            <div class=\"row gy-4\">
                <div class=\"col-md-4\">
                    <h5>AgriDetect</h5>
                    <p>Futuristic crop disease analytics and AI advisory for smart farming operations.</p>
                </div>
                <div class=\"col-md-4\">
                    <h5>Quick Links</h5>
                    <ul class=\"footer-links list-unstyled\">
                        <li><a href=\"/dashboard\">Dashboard</a></li>
                        <li><a href=\"/upload\">Predict</a></li>
                        <li><a href=\"/advisor\">AI Advisor</a></li>
                    </ul>
                </div>
                <div class=\"col-md-4\">
                    <h5>Contact</h5>
                    <p><i class=\"fas fa-envelope\"></i> support@agridetect.ai</p>
                    <p><i class=\"fas fa-phone\"></i> +1 (555) 123-4567</p>
                </div>
            </div>
            <div class=\"footer-bottom text-center mt-4\">
                <small>&copy; 2026 AgriDetect. All rights reserved.</small>
            </div>
        </div>
    </footer>

    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js\"></script>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js\"></script>
    <script src=\"{{ url_for('static', filename='js/app.js') }}\"></script>
    <script src=\"{{ url_for('static', filename='js/main_modern.js') }}\"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
""",
    'static/css/style_modern.css': """/* Futuristic AI Smart Farming Dashboard - Glassmorphism Theme */
:root {
    --bg-dark: #020617;
    --bg-darker: #030b1a;
    --panel: rgba(5, 18, 42, 0.75);
    --panel-strong: rgba(8, 26, 52, 0.95);
    --border-glow: rgba(0, 245, 255, 0.28);
    --border-soft: rgba(0, 245, 255, 0.12);
    --text-light: #e6f7ff;
    --text-muted: rgba(230, 247, 255, 0.72);
    --cyan: #00f5ff;
    --emerald: #22c55e;
    --deep-blue: #0f172a;
    --shadow: 0 30px 90px rgba(0, 0, 0, 0.35);
    --radius: 24px;
    --transition: 0.35s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    min-height: 100%;
    scroll-behavior: smooth;
}

body {
    font-family: 'Inter', 'Poppins', sans-serif;
    color: var(--text-light);
    background: radial-gradient(circle at top left, rgba(0, 245, 255, 0.14), transparent 25%),
                radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.12), transparent 20%),
                linear-gradient(180deg, #020617 0%, #071128 55%, #0f172a 100%);
    background-attachment: fixed;
    position: relative;
}

body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.05), transparent 35%),
                linear-gradient(45deg, rgba(34, 197, 94, 0.04), transparent 40%);
    pointer-events: none;
}

.background-layers {
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle at 20% 10%, rgba(0, 245, 255, 0.18), transparent 15%),
                      radial-gradient(circle at 80% 20%, rgba(34, 197, 94, 0.12), transparent 14%),
                      linear-gradient(180deg, transparent 0%, rgba(2, 6, 23, 0.55) 100%);
    pointer-events: none;
    z-index: 0;
}

.futuristic-body, .page-content, .navbar, .footer-bottom {
    position: relative;
    z-index: 1;
}

.page-content {
    padding-top: 1rem;
    padding-bottom: 4rem;
}

.futuristic-nav {
    background: rgba(4, 16, 35, 0.92);
    border-bottom: 1px solid rgba(0, 245, 255, 0.12);
    box-shadow: inset 0 -1px 0 rgba(0, 245, 255, 0.08);
}

.navbar-brand {
    color: var(--text-light) !important;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.12em;
    font-size: 1.1rem;
}

.brand-title {
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    line-height: 1.1;
}

.brand-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.navbar .nav-link {
    color: rgba(230, 247, 255, 0.8) !important;
    font-weight: 500;
    transition: color var(--transition), transform var(--transition);
}

.navbar .nav-link:hover,
.navbar .nav-link.active {
    color: var(--cyan) !important;
    transform: translateY(-1px);
}

.futuristic-dropdown {
    background: rgba(4, 16, 35, 0.96);
    border: 1px solid rgba(0, 245, 255, 0.14);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.35);
}

.footer-links a {
    color: var(--text-muted);
    text-decoration: none;
}

.footer-links a:hover {
    color: var(--cyan);
}

.futuristic-footer {
    background: rgba(3, 8, 23, 0.95);
    border-top: 1px solid rgba(0, 245, 255, 0.08);
    color: var(--text-muted);
}

.futuristic-footer h5 {
    color: var(--text-light);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-section {
    position: relative;
    overflow: hidden;
    padding: 4rem 0;
}

.hero-section::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle at 10% 20%, rgba(0, 245, 255, 0.12), transparent 18%),
                      radial-gradient(circle at 90% 10%, rgba(34, 197, 94, 0.12), transparent 14%);
    pointer-events: none;
}

.hero-section .hero-panel {
    background: rgba(7, 17, 37, 0.76);
    border: 1px solid rgba(0, 245, 255, 0.12);
    backdrop-filter: blur(18px);
    border-radius: 28px;
    padding: 3rem;
    box-shadow: var(--shadow);
}

.hero-title,
.section-title {
    font-family: 'Orbitron', sans-serif;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 0.18em;
}

.hero-title {
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    line-height: 1.05;
}

.hero-copy {
    color: var(--text-muted);
    font-size: 1.05rem;
    max-width: 760px;
}

.section-subtitle {
    color: var(--text-muted);
    letter-spacing: 0.06em;
}

.glass-card,
.frosted-card,
.card.glass-card {
    background: rgba(5, 18, 42, 0.75);
    border: 1px solid rgba(0, 245, 255, 0.12);
    backdrop-filter: blur(18px);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
    border-radius: var(--radius);
    color: var(--text-light);
}

.card {
    background: transparent;
    border: none;
}

.card-header {
    background: transparent;
    border-bottom: none;
    padding-bottom: 0;
}

.card .card-body {
    padding: 1.75rem;
}

.glow-border {
    border: 1px solid rgba(0, 245, 255, 0.16);
    box-shadow: 0 0 0 1px rgba(0, 245, 255, 0.06), 0 30px 80px rgba(0, 0, 0, 0.18);
}

.btn-glow,
.btn-success,
.btn-primary,
.btn-outline-primary,
.btn-outline-secondary {
    border-radius: 999px;
    font-weight: 600;
    transition: transform var(--transition), box-shadow var(--transition), background var(--transition);
}

.btn-glow,
.btn-success,
.btn-primary {
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.95), rgba(34, 197, 94, 0.85));
    color: #020617;
    box-shadow: 0 18px 45px rgba(0, 245, 255, 0.22);
}

.btn-glow:hover,
.btn-success:hover,
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 24px 60px rgba(0, 245, 255, 0.28);
}

.btn-outline-primary,
.btn-outline-secondary {
    color: var(--cyan);
    border: 1px solid rgba(0, 245, 255, 0.35);
    background: rgba(255, 255, 255, 0.02);
}

.btn-outline-primary:hover,
.btn-outline-secondary:hover {
    color: var(--bg-dark);
    background: rgba(0, 245, 255, 0.12);
    border-color: rgba(0, 245, 255, 0.55);
}

.form-control,
.form-select,
.form-control:focus,
.form-select:focus {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(0, 245, 255, 0.18);
    color: var(--text-light);
    box-shadow: none;
}

.form-label {
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 0.05em;
}

::placeholder {
    color: rgba(230, 247, 255, 0.45);
}

.alert-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    width: clamp(280px, 18vw, 360px);
    z-index: 1050;
}

.alert {
    border-radius: 18px;
    border: 1px solid rgba(0, 245, 255, 0.15);
    background: rgba(4, 16, 35, 0.96);
    color: var(--text-light);
}

.alert a {
    color: var(--cyan);
}

.section-card {
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.section-title-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.section-title-wrapper .section-title {
    margin-bottom: 0;
}

.section-title-wrapper .section-copy {
    color: var(--text-muted);
    font-size: 0.95rem;
}

.stat-panel {
    padding: 1.75rem;
    border: 1px solid rgba(0, 245, 255, 0.12);
    border-radius: 26px;
    background: rgba(5, 18, 42, 0.7);
}

.stat-panel .stat-label {
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.8rem;
    margin-bottom: 0.75rem;
}

.stat-panel .stat-value {
    font-size: 2.5rem;
    font-family: 'Orbitron', sans-serif;
    color: var(--cyan);
}

.stat-panel .stat-note {
    color: var(--text-muted);
    margin-top: 0.5rem;
}

.glow-card {
    border-radius: 28px;
    background: rgba(5, 18, 42, 0.78);
    border: 1px solid rgba(0, 245, 255, 0.12);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
}

.glow-card .card-body {
    padding: 2rem;
}

.card-title {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.table-responsive {
    border-radius: 28px;
    overflow: hidden;
    border: 1px solid rgba(0, 245, 255, 0.12);
}

.table {
    color: var(--text-light);
    background: rgba(5, 18, 42, 0.6);
}

.table thead {
    background: rgba(0, 245, 255, 0.12);
}

.table th,
.table td {
    vertical-align: middle;
    border: none;
    padding: 1rem 1.25rem;
}

.table tbody tr {
    transition: transform var(--transition), background var(--transition);
}

.table tbody tr:hover {
    background: rgba(0, 245, 255, 0.08);
    transform: translateX(4px);
}

.badge {
    border-radius: 999px;
    padding: 0.65em 0.95em;
    font-weight: 600;
}

.badge-success {
    background: rgba(34, 197, 94, 0.15);
    color: var(--emerald);
}

.badge-info {
    background: rgba(0, 245, 255, 0.12);
    color: var(--cyan);
}

.result-card,
.advice-card,
.recommendation-card,
.probability-card {
    border-radius: 28px;
    background: rgba(5, 18, 42, 0.78);
    border: 1px solid rgba(0, 245, 255, 0.12);
    padding: 1.8rem;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
}

.upload-area {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    min-height: 320px;
    border: 2px dashed rgba(0, 245, 255, 0.28);
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.03);
    cursor: pointer;
    transition: border-color var(--transition), transform var(--transition), box-shadow var(--transition);
}

.upload-area:hover {
    border-color: rgba(0, 245, 255, 0.58);
    transform: translateY(-2px);
    box-shadow: 0 20px 45px rgba(0, 245, 255, 0.08);
}

.upload-area.dragover {
    border-color: rgba(34, 197, 94, 0.8);
    background: rgba(0, 245, 255, 0.05);
}

.upload-area i {
    font-size: 3.5rem;
    color: var(--cyan);
    animation: float 3s ease-in-out infinite;
}

.upload-area p,
.upload-area strong {
    color: var(--text-light);
}

.preview-card {
    border-radius: 28px;
    background: rgba(5, 18, 42, 0.82);
    border: 1px solid rgba(0, 245, 255, 0.12);
    padding: 1.25rem;
    overflow: hidden;
}

.preview-card img {
    width: 100%;
    border-radius: 20px;
    object-fit: cover;
    border: 1px solid rgba(0, 245, 255, 0.12);
}

.prediction-summary {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.prediction-tile {
    border-radius: 20px;
    background: rgba(3, 10, 26, 0.9);
    border: 1px solid rgba(0, 245, 255, 0.12);
    padding: 1.25rem;
}

.prediction-tile h4 {
    color: var(--cyan);
    font-family: 'Orbitron', sans-serif;
    margin-bottom: 0.5rem;
}

.prediction-tile p {
    color: var(--text-muted);
    margin-bottom: 0;
}

.confidence-bar-wrapper {
    position: relative;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    height: 24px;
    overflow: hidden;
    border: 1px solid rgba(0, 245, 255, 0.12);
}

.confidence-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, rgba(0, 245, 255, 0.9), rgba(34, 197, 94, 0.9));
    transition: width 0.5s ease;
}

.confidence-bar-label {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-light);
    font-weight: 700;
    font-size: 0.9rem;
}

.severity-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.65rem 1rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.severity-low {
    background: rgba(34, 197, 94, 0.12);
    color: #a7f3d0;
    border: 1px solid rgba(34, 197, 94, 0.24);
}

.severity-moderate {
    background: rgba(245, 158, 11, 0.14);
    color: #fcd34d;
    border: 1px solid rgba(245, 158, 11, 0.28);
}

.severity-high {
    background: rgba(239, 68, 68, 0.14);
    color: #fecaca;
    border: 1px solid rgba(239, 68, 68, 0.28);
}

.ai-advice-card {
    border-radius: 28px;
    border: 1px solid rgba(0, 245, 255, 0.14);
    background: rgba(4, 16, 35, 0.85);
    overflow: hidden;
}

.ai-advice-card .card-body,
.recommendation-card .card-body {
    padding: 1.75rem;
}

.ai-advice-card .card-header,
.recommendation-card .card-header {
    background: rgba(0, 245, 255, 0.08);
    border-bottom: 1px solid rgba(0, 245, 255, 0.08);
    color: var(--cyan);
    font-weight: 700;
}

.probability-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.probability-item {
    display: grid;
    grid-template-columns: 1fr 3fr 60px;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1rem;
}

.probability-label {
    color: var(--text-muted);
    font-size: 0.95rem;
    word-break: break-word;
}

.probability-bar-container {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(0, 245, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
    height: 16px;
}

.probability-bar {
    height: 100%;
    background: linear-gradient(90deg, rgba(0, 245, 255, 0.85), rgba(34, 197, 94, 0.85));
    transition: width 0.6s ease;
}

.probability-percent {
    text-align: right;
    color: var(--text-light);
    font-weight: 700;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-14px); }
}

@media (max-width: 992px) {
    .hero-section {
        padding: 3rem 0;
    }
    .hero-title {
        font-size: 2.6rem;
    }
}
""",
    'static/js/app.js': """/* Futuristic UI Core Utilities */

function getExistingChart(ctx) {
    if (!ctx) return null;
    if (typeof Chart.getChart === 'function') {
        return Chart.getChart(ctx);
    }
    if (ctx && ctx.chart) {
        return ctx.chart;
    }
    const canvas = ctx.canvas || ctx;
    if (canvas && canvas.chart) {
        return canvas.chart;
    }
    return null;
}

function destroyChartIfExists(ctx) {
    const chart = getExistingChart(ctx);
    if (chart && typeof chart.destroy === 'function') {
        chart.destroy();
    }
}

function showAlert(message, type = 'info', containerId = 'alertContainer') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const alertHtml = `
        <div class=\"alert alert-${type} alert-dismissible fade show\" role=\"alert\">
            ${message}
            <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button>
        </div>
    `;

    container.innerHTML = alertHtml;

    if (type !== 'danger') {
        setTimeout(() => {
            const alertNode = container.firstChild;
            if (alertNode) {
                alertNode.classList.remove('show');
                alertNode.classList.add('hide');
            }
        }, 5000);
    }
}

function showLoadingModal(message = 'Processing...') {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        document.querySelector('#loadingModal .modal-body').textContent = message;
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

function hideLoadingModal() {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) bsModal.hide();
    }
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
    return (parseFloat(value) * 100).toFixed(2) + '%';
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

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
        showAlert(error.message, 'danger');
        throw error;
    }
}

function createPieChart(canvasId, labels, data, title = '') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    destroyChartIfExists(ctx);

    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(0, 245, 255, 0.9)',
                    'rgba(34, 197, 94, 0.9)',
                    'rgba(14, 165, 233, 0.85)',
                    'rgba(79, 70, 229, 0.85)',
                    'rgba(14, 165, 233, 0.6)'
                ],
                borderColor: 'rgba(255, 255, 255, 0.12)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e6f7ff'
                    }
                },
                title: {
                    display: !!title,
                    text: title,
                    color: '#e6f7ff',
                    font: {
                        family: 'Orbitron, sans-serif',
                        size: 18,
                        weight: '700'
                    }
                }
            }
        }
    });
}

function createBarChart(canvasId, labels, data, title = '', label = 'Count') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    destroyChartIfExists(ctx);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(0, 245, 255, 0.78)',
                borderColor: 'rgba(0, 245, 255, 1)',
                borderWidth: 1,
                borderRadius: 12,
                barThickness: 24
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: !!title,
                    text: title,
                    color: '#e6f7ff',
                    font: {
                        family: 'Orbitron, sans-serif',
                        size: 18,
                        weight: '700'
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.08)' },
                    ticks: { color: '#e6f7ff' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.08)' },
                    ticks: { color: '#e6f7ff' }
                }
            }
        }
    });
}

window.downloadPredictionReport = function(predictionId) {
    const id = predictionId || window.currentPredictionId;
    if (!id) {
        showAlert('No prediction selected for report download.', 'warning');
        return;
    }
    window.location.href = `/api/report/${id}`;
};
""",
    'static/js/dashboard.js': """/* Dashboard page JavaScript */
let dashboardCharts = {};
window.currentPredictionId = null;

document.addEventListener('DOMContentLoaded', async function () {
    await loadDashboardStats();
    await loadPredictionHistory();
    await initializeCharts();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/history?limit=1000');
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        const data = await response.json();
        const predictions = data.predictions || [];
        const totalPreds = predictions.length;
        const healthyCount = predictions.filter(pred =>
            pred.disease && pred.disease.toLowerCase().includes('healthy')
        ).length;
        const diseaseCount = totalPreds - healthyCount;
        const avgConfidence = totalPreds > 0
            ? (
                predictions.reduce((sum, pred) => sum + parseFloat(pred.confidence || 0), 0) /
                totalPreds * 100
            ).toFixed(2)
            : '0.00';

        document.getElementById('totalPreds').textContent = totalPreds;
        document.getElementById('healthyCount').textContent = healthyCount;
        document.getElementById('diseaseCount').textContent = diseaseCount;
        document.getElementById('avgConfidence').textContent = `${avgConfidence}%`;

        return predictions;
    } catch (error) {
        console.error('Error loading stats:', error);
        showAlert('Failed to load statistics. Refresh to retry.', 'warning');
        return [];
    }
}

async function loadPredictionHistory() {
    try {
        const response = await fetch('/api/history?limit=50');
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        const data = await response.json();
        const predictions = data.predictions || [];
        const tbody = document.getElementById('predictionsBody');

        if (!predictions.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan=\"7\" class=\"text-center text-muted py-5\">
                        <i class=\"fas fa-inbox fa-2x mb-3\"></i>
                        <div>No predictions yet.<br><a href='/upload' class='link-cyan'>Make your first prediction</a></div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = predictions.map(pred => `
            <tr>
                <td>${formatDate(pred.created_at)}</td>
                <td><span class=\"badge bg-info\">${capitalize(pred.crop)}</span></td>
                <td>${escapeHtml(pred.disease)}</td>
                <td>
                    <div class=\"confidence-bar-wrapper\">
                        <div class=\"confidence-bar-fill\" style=\"width: ${parseFloat(pred.confidence) * 100}%\"></div>
                        <span class=\"confidence-bar-label\">${pred.confidence_percent}</span>
                    </div>
                </td>
                <td>${pred.fertilizer_recommendation ? escapeHtml(pred.fertilizer_recommendation.slice(0, 80)) + (pred.fertilizer_recommendation.length > 80 ? '...' : '') : '-'}</td>
                <td>${pred.ai_advice ? escapeHtml(pred.ai_advice.slice(0, 80)) + (pred.ai_advice.length > 80 ? '...' : '') : '-'}</td>
                <td>
                    <button class=\"btn btn-outline-primary btn-sm\" onclick=\"viewPrediction(${pred.id})\">
                        <i class=\"fas fa-eye\"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading predictions:', error);
        showAlert('Failed to load prediction history.', 'danger');
    }
}

async function viewPrediction(predictionId) {
    try {
        const response = await fetch(`/api/prediction/${predictionId}`);
        if (!response.ok) {
            throw new Error('Failed to load prediction');
        }
        const data = await response.json();
        const pred = data.prediction;
        if (!pred) {
            throw new Error('Prediction data missing');
        }

        window.currentPredictionId = pred.id;

        const severity = pred.severity || 'low';
        const severityClass = typeof severityBadgeClass === 'function' ? severityBadgeClass(severity) : 'severity-low';
        const severityLabel = typeof severityBadgeLabel === 'function' ? severityBadgeLabel(severity) : 'Low Severity';

        const modalBody = document.getElementById('predictionModalBody');
        modalBody.innerHTML = `
            <div class=\"row gy-4\">
                <div class=\"col-md-6\">
                    <div class=\"preview-card\">
                        <img src=\"${pred.image_path}\" class=\"img-fluid rounded\" alt=\"Leaf Image\">
                    </div>
                </div>
                <div class=\"col-md-6\">
                    <h4 class=\"section-title mb-3\">${escapeHtml(pred.disease)}</h4>
                    <p class=\"text-muted mb-3\">Crop: <strong>${capitalize(pred.crop)}</strong></p>
                    <p class=\"text-muted mb-3\">Confidence: <strong>${pred.confidence_percent}</strong></p>
                    <p class=\"text-muted mb-3\">Severity: <span class=\"severity-badge ${severityClass}\">${severityLabel}</span></p>
                    <p class=\"text-muted mb-3\">Date: <strong>${formatDate(pred.created_at)}</strong></p>
                    ${pred.ai_advice ? `
                        <div class=\"ai-advice-card mt-4\">
                            <div class=\"card-header\">AI Advice</div>
                            <div class=\"card-body\"><p>${pred.ai_advice.replace(/\\n/g, '<br>')}</p></div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('predictionModal'));
        modal.show();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Unable to load prediction details.', 'danger');
    }
}

async function initializeCharts() {
    try {
        const response = await fetch('/api/history?limit=1000');
        if (!response.ok) {
            throw new Error('Failed to load chart data');
        }
        const data = await response.json();
        const predictions = data.predictions || [];

        const cropCounts = {};
        const diseaseCounts = {};
        predictions.forEach(pred => {
            cropCounts[pred.crop] = (cropCounts[pred.crop] || 0) + 1;
            diseaseCounts[pred.disease] = (diseaseCounts[pred.disease] || 0) + 1;
        });

        createPieChart('cropsChart', Object.keys(cropCounts), Object.values(cropCounts), 'Crop Distribution');

        const topDiseases = Object.entries(diseaseCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);

        createBarChart('diseasesChart', topDiseases.map(item => item[0]), topDiseases.map(item => item[1]), 'Top Detected Diseases', 'Detections');
    } catch (error) {
        console.error('Error initializing charts:', error);
        showAlert('Charts could not be loaded.', 'warning');
    }
}
""",
    'static/js/upload.js': """/* Upload page handling */
let currentPredictionId = null;

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
            showAlert('Please select a leaf image to analyze.', 'warning');
            return;
        }

        const crop = document.getElementById('crop').value;
        const includeAdvice = document.getElementById('includeAdvice').checked;

        if (!crop) {
            showAlert('Select a crop before submitting.', 'warning');
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
            displayPredictionResults(data);
        } catch (error) {
            console.error(error);
            showAlert(error.message, 'danger');
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
            showAlert('Only image files are supported.', 'danger');
            return;
        }
        if (file.size > 50 * 1024 * 1024) {
            showAlert('Image must be smaller than 50MB.', 'danger');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            previewImage.src = event.target.result;
            previewContainer.classList.remove('d-none');
            previewContainer.classList.add('preview-card');
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
    }
});

function displayPredictionResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const loadingContainer = document.getElementById('loadingContainer');
    const predictionForm = document.getElementById('predictionForm');

    predictionForm?.classList.add('d-none');
    loadingContainer?.classList.add('d-none');
    resultsSection?.classList.remove('d-none');

    const confidenceValue = parseFloat(data.confidence || 0) * 100;
    const severity = data.severity || 'low';
    const severityClass = typeof severityBadgeClass === 'function' ? severityBadgeClass(severity) : 'severity-low';
    const severityLabel = typeof severityBadgeLabel === 'function' ? severityBadgeLabel(severity) : 'Low Severity';

    resultsSection.innerHTML = `
        <div class=\"glass-card\">
            <div class=\"row gy-4\">
                <div class=\"col-lg-6\">
                    <div class=\"preview-card mb-4\">
                        <img src=\"${data.image_path}\" alt=\"Uploaded Leaf\" class=\"img-fluid rounded\">
                    </div>
                </div>
                <div class=\"col-lg-6 d-flex flex-column justify-content-between\">
                    <div>
                        <h4 class=\"section-title mb-3\">Prediction Summary</h4>
                        <div class=\"prediction-tile mb-3\">
                            <h4>${escapeHtml(data.disease)}</h4>
                            <p>Crop: <strong>${capitalize(data.crop)}</strong></p>
                        </div>
                        <div class=\"prediction-tile mb-3\">
                            <h4>Confidence</h4>
                            <div class=\"confidence-bar-wrapper mb-2\">
                                <div class=\"confidence-bar-fill\" style=\"width: ${confidenceValue}%\"></div>
                                <div class=\"confidence-bar-label\">${data.confidence_percent}</div>
                            </div>
                            <span class=\"severity-badge ${severityClass}\">${severityLabel}</span>
                        </div>
                    </div>
                    <div class=\"d-grid gap-2 mt-2\">
                        <button class=\"btn btn-outline-primary\" type=\"button\" onclick=\"window.downloadPredictionReport(${data.prediction_id})\">
                            <i class=\"fas fa-download me-2\"></i> Download Report
                        </button>
                        <button class=\"btn btn-outline-secondary\" type=\"button\" onclick=\"resetPredictionForm()\">
                            <i class=\"fas fa-redo me-2\"></i> Analyze Another Leaf
                        </button>
                    </div>
                </div>
            </div>
            <div class=\"row mt-4\">
                <div class=\"col-lg-12\">
                    <div class=\"ai-advice-card\">
                        <div class=\"card-header\">AI Agricultural Insight</div>
                        <div class=\"card-body\">
                            <p>${data.ai_advice ? data.ai_advice.replace(/\\n/g, '<br>') : 'AI advice is not available for this prediction.'}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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
""",
    'templates/index.html': """{% extends \"base.html\" %}

{% block title %}Home - AgriDetect{% endblock %}

{% block content %}
<section class=\"hero-section py-5\">
    <div class=\"container\">
        <div class=\"row align-items-center gy-5\">
            <div class=\"col-lg-6\">
                <div class=\"hero-panel\">
                    <p class=\"section-title mb-3\">FUTURISTIC FARMING CONTROL PANEL</p>
                    <h1 class=\"hero-title mb-4\">AI-Powered Crop Disease Detection</h1>
                    <p class=\"hero-copy mb-4\">Turn every leaf image into a smart diagnosis with neon-glow analytics, intelligent recommendations, and complete prediction history—all from an advanced AI farming dashboard.</p>
                    <div class=\"d-flex flex-wrap gap-3\">
                        {% if current_user %}
                            <a href=\"/upload\" class=\"btn btn-glow btn-lg\">Start Scanning</a>
                            <a href=\"/dashboard\" class=\"btn btn-outline-primary btn-lg\">Go to Dashboard</a>
                        {% else %}
                            <a href=\"/register\" class=\"btn btn-glow btn-lg\">Join Now</a>
                            <a href=\"/login\" class=\"btn btn-outline-primary btn-lg\">Sign In</a>
                        {% endif %}
                    </div>
                </div>
            </div>
            <div class=\"col-lg-6\">
                <div class=\"glass-card p-4\">
                    <div class=\"row g-3\">
                        <div class=\"col-6\">
                            <div class=\"stat-panel\">
                                <div class=\"stat-label\">Predictions</div>
                                <div class=\"stat-value\">50K+</div>
                                <div class=\"stat-note\">Fast AI disease scans</div>
                            </div>
                        </div>
                        <div class=\"col-6\">
                            <div class=\"stat-panel\">
                                <div class=\"stat-label\">Accuracy</div>
                                <div class=\"stat-value\">98%</div>
                                <div class=\"stat-note\">Research-backed models</div>
                            </div>
                        </div>
                        <div class=\"col-6\">
                            <div class=\"stat-panel\">
                                <div class=\"stat-label\">Crops Covered</div>
                                <div class=\"stat-value\">3</div>
                                <div class=\"stat-note\">Banana, Corn, Sugarcane</div>
                            </div>
                        </div>
                        <div class=\"col-6\">
                            <div class=\"stat-panel\">
                                <div class=\"stat-label\">AI Advisor</div>
                                <div class=\"stat-value\">24/7</div>
                                <div class=\"stat-note\">Smart farming guidance</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class=\"glass-card p-4 mt-4\">
                    <h3 class=\"section-title mb-3\">Smart Farming Highlights</h3>
                    <ul class=\"list-unstyled text-muted\">
                        <li class=\"mb-3\"><i class=\"fas fa-check-circle text-cyan me-2\"></i>Instant leaf disease detection</li>
                        <li class=\"mb-3\"><i class=\"fas fa-check-circle text-cyan me-2\"></i>Adaptive AI recommendations</li>
                        <li><i class=\"fas fa-check-circle text-cyan me-2\"></i>Secure user dashboard and history logs</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</section>

<section class=\"container py-5\">
    <div class=\"section-title-wrapper\">
        <div>
            <p class=\"section-label text-muted mb-2\">Why AgriDetect</p>
            <h2 class=\"section-title mb-1\">Next-Gen Crop Intelligence</h2>
        </div>
    </div>
    <div class=\"row g-4\">
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>Neon Analytics</h5>
                <p class=\"text-muted\">Track crop health through glowing AI visualizations and real-time prediction insights.</p>
            </div>
        </div>
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>AI Diagnostics</h5>
                <p class=\"text-muted\">Identify disease patterns with deep learning and make smarter treatment decisions faster.</p>
            </div>
        </div>
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>Field Recommendations</h5>
                <p class=\"text-muted\">Receive fertilizer guidance, severity alerts, and recovery plans for healthier yields.</p>
            </div>
        </div>
    </div>
</section>

<section class=\"container py-5\">
    <div class=\"section-title-wrapper\">
        <div>
            <p class=\"section-label text-muted mb-2\">Supported Crops</p>
            <h2 class=\"section-title mb-1\">Crops Monitored by Our AI</h2>
        </div>
    </div>
    <div class=\"row g-4\">
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>Banana</h5>
                <p class=\"text-muted\">Cordana, Pestalotiopsis, Sigatoka and healthy leaf detection.</p>
            </div>
        </div>
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>Corn</h5>
                <p class=\"text-muted\">Blight, Common Rust, Gray Leaf Spot and healthy crop analysis.</p>
            </div>
        </div>
        <div class=\"col-md-4\">
            <div class=\"glass-card p-4\">
                <h5>Sugarcane</h5>
                <p class=\"text-muted\">Red Rot, Rust, Yellow, Mosaic, Bacterial Blights and healthy conditions.</p>
            </div>
        </div>
    </div>
</section>
{% endblock %}
""",
    'templates/dashboard.html': """{% extends \"base.html\" %}

{% block title %}Dashboard - AgriDetect{% endblock %}

{% block content %}
<section class=\"hero-section py-5\">
    <div class=\"container\">
        <div class=\"hero-panel row align-items-center gy-4\">
            <div class=\"col-lg-8\">
                <p class=\"section-title mb-2\">FARMING INTELLIGENCE</p>
                <h1 class=\"hero-title mb-3\">Welcome back, {{ current_user.username }}.</h1>
                <p class=\"hero-copy\">Review AI crop diagnostics, explore disease analytics, and track your prediction timeline from one glowing command center.</p>
            </div>
            <div class=\"col-lg-4 text-lg-end\">
                <a href=\"/upload\" class=\"btn btn-glow btn-lg\">New Scan</a>
            </div>
        </div>
    </div>
</section>

<div class=\"container py-5\">
    <div class=\"row g-4 mb-4\">
        <div class=\"col-md-3\">
            <div class=\"stat-panel\">
                <div class=\"stat-label\">Total Predictions</div>
                <div class=\"stat-value\" id=\"totalPreds\">0</div>
            </div>
        </div>
        <div class=\"col-md-3\">
            <div class=\"stat-panel\">
                <div class=\"stat-label\">Healthy Crops</div>
                <div class=\"stat-value\" id=\"healthyCount\">0</div>
            </div>
        </div>
        <div class=\"col-md-3\">
            <div class=\"stat-panel\">
                <div class=\"stat-label\">Diseases Detected</div>
                <div class=\"stat-value\" id=\"diseaseCount\">0</div>
            </div>
        </div>
        <div class=\"col-md-3\">
            <div class=\"stat-panel\">
                <div class=\"stat-label\">AI Confidence</div>
                <div class=\"stat-value\" id=\"avgConfidence\">0%</div>
            </div>
        </div>
    </div>

    <div class=\"row g-4\">
        <div class=\"col-xl-8\">
            <div class=\"glow-card\">
                <div class=\"section-title-wrapper mb-3\">
                    <div>
                        <p class=\"section-label text-muted mb-2\">Prediction History</p>
                        <h3 class=\"section-title mb-0\">Recent Results</h3>
                    </div>
                </div>
                <div class=\"table-responsive\">
                    <table class=\"table table-hover mb-0\">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Crop</th>
                                <th>Disease</th>
                                <th>Confidence</th>
                                <th>Fertilizer</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id=\"predictionsBody\">
                            <tr>
                                <td colspan=\"6\" class=\"text-center text-muted py-5\">
                                    <div class=\"spinner-border text-cyan\" role=\"status\"></div>
                                    <div class=\"mt-3\">Loading prediction history...</div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class=\"col-xl-4\">
            <div class=\"glow-card mb-4\">
                <div class=\"section-title-wrapper mb-3\">
                    <div>
                        <p class=\"section-label text-muted mb-2\">Crop Insights</p>
                        <h3 class=\"section-title mb-0\">Distribution</h3>
                    </div>
                </div>
                <div style=\"height: 320px;\">
                    <canvas id=\"cropsChart\"></canvas>
                </div>
            </div>
            <div class=\"glow-card\">
                <div class=\"section-title-wrapper mb-3\">
                    <div>
                        <p class=\"section-label text-muted mb-2\">Next Action</p>
                        <h3 class=\"section-title mb-0\">Quick Tools</h3>
                    </div>
                </div>
                <div class=\"d-grid gap-3\">
                    <a href=\"/upload\" class=\"btn btn-outline-primary\"> <i class=\"fas fa-cloud-upload-alt me-2\"></i>New Prediction</a>
                    <a href=\"/advisor\" class=\"btn btn-outline-primary\"> <i class=\"fas fa-robot me-2\"></i>Ask AI Advisor</a>
                    <a href=\"/history\" class=\"btn btn-outline-primary\"> <i class=\"fas fa-history me-2\"></i>Full History</a>
                </div>
            </div>
        </div>
    </div>

    <div class=\"glow-card mt-4\">
        <div class=\"section-title-wrapper mb-3\">
            <div>
                <p class=\"section-label text-muted mb-2\">Health Patterns</p>
                <h3 class=\"section-title mb-0\">Top Detected Diseases</h3>
            </div>
        </div>
        <div style=\"height: 360px;\">
            <canvas id=\"diseasesChart\"></canvas>
        </div>
    </div>
</div>

<div class=\"modal fade\" id=\"predictionModal\" tabindex=\"-1\">
    <div class=\"modal-dialog modal-xl modal-dialog-centered\">
        <div class=\"modal-content glow-card\">
            <div class=\"modal-header border-0\">
                <h5 class=\"modal-title\">Prediction Details</h5>
                <button type=\"button\" class=\"btn-close btn-close-white\" data-bs-dismiss=\"modal\" aria-label=\"Close\"></button>
            </div>
            <div class=\"modal-body\" id=\"predictionModalBody\"></div>
            <div class=\"modal-footer border-0\">
                <button type=\"button\" class=\"btn btn-outline-secondary\" data-bs-dismiss=\"modal\">Close</button>
                <button type=\"button\" class=\"btn btn-glow\" onclick=\"window.downloadPredictionReport()\">Download Report</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src=\"{{ url_for('static', filename='js/dashboard.js') }}\"></script>
{% endblock %}
""",
    'templates/upload.html': """{% extends \"base.html\" %}

{% block title %}Predict Disease - AgriDetect{% endblock %}

{% block content %}
<section class=\"hero-section py-5\">
    <div class=\"container\">
        <div class=\"row align-items-center gy-4\">
            <div class=\"col-lg-7\">
                <div class=\"hero-panel\">
                    <p class=\"section-title mb-3\">AI LEAF ANALYZER</p>
                    <h1 class=\"hero-title mb-3\">Upload a crop image for instant diagnosis.</h1>
                    <p class=\"hero-copy\">Use the futuristic scan interface to capture leaf health data, get disease confidence, and receive fertilizer recommendations powered by intelligent AI.</p>
                </div>
            </div>
            <div class=\"col-lg-5 text-lg-end\">
                <a href=\"/dashboard\" class=\"btn btn-outline-primary btn-lg\">View Dashboard</a>
            </div>
        </div>
    </div>
</section>

<div class=\"container py-5\">
    <div class=\"row g-4\">
        <div class=\"col-xl-7\">
            <div class=\"glass-card p-4\">
                <div class=\"section-title-wrapper mb-4\">
                    <div>
                        <p class=\"section-label text-muted mb-2\">Smart Upload</p>
                        <h3 class=\"section-title mb-0\">AI Scan Zone</h3>
                    </div>
                </div>
                <form id=\"predictionForm\" class=\"row g-4\" novalidate>
                    <div class=\"col-12\">
                        <label class=\"form-label\" for=\"crop\">Select Crop</label>
                        <select class=\"form-select\" id=\"crop\" required>
                            <option value=\"\">-- Choose a crop --</option>
                            <option value=\"banana\">Banana</option>
                            <option value=\"corn\">Corn</option>
                            <option value=\"sugarcane\">Sugarcane</option>
                        </select>
                    </div>
                    <div class=\"col-12\">
                        <div class=\"upload-area\" id=\"uploadArea\">
                            <i class=\"fas fa-cloud-upload-alt\"></i>
                            <div>
                                <p class=\"mb-1\"><strong>Drag & drop your leaf image</strong></p>
                                <p class=\"text-muted\">or click to browse supported formats</p>
                            </div>
                            <small class=\"text-muted\">JPG, PNG, GIF, BMP — Max 50MB</small>
                            <input type=\"file\" class=\"d-none\" id=\"imageUpload\" accept=\".jpg,.jpeg,.png,.gif,.bmp\">
                        </div>
                    </div>
                    <div class=\"col-12 d-none\" id=\"previewContainer\">
                        <div class=\"preview-card p-3\">
                            <div class=\"d-flex justify-content-between align-items-center mb-3\">
                                <span class=\"text-muted\">Image Preview</span>
                                <button type=\"button\" class=\"btn btn-outline-secondary btn-sm\" id=\"changeImageBtn\">Change Image</button>
                            </div>
                            <img id=\"previewImage\" src=\"\" alt=\"Preview\" class=\"img-fluid rounded\" />
                        </div>
                    </div>
                    <div class=\"col-12\">
                        <div class=\"form-check form-switch\">
                            <input class=\"form-check-input\" type=\"checkbox\" id=\"includeAdvice\" checked>
                            <label class=\"form-check-label text-muted\" for=\"includeAdvice\">Include AI recommendation insights</label>
                        </div>
                    </div>
                    <div class=\"col-12\">
                        <button type=\"submit\" class=\"btn btn-glow btn-lg w-100\">Analyze Image</button>
                    </div>
                </form>
                <div id=\"loadingContainer\" class=\"text-center d-none mt-4\">
                    <div class=\"spinner-border text-cyan\" role=\"status\"></div>
                    <p class=\"mt-3 text-muted\">AI scanning leaf data...</p>
                </div>
            </div>
            <div id=\"resultsSection\" class=\"glass-card p-4 mt-4 d-none\"></div>
        </div>
        <div class=\"col-xl-5\">
            <div class=\"glass-card p-4\">
                <h4 class=\"section-title mb-3\">Capture Best Photos</h4>
                <ul class=\"text-muted\">
                    <li class=\"mb-3\"><i class=\"fas fa-check-circle text-cyan me-2\"></i>Use good lighting and clear focus.</li>
                    <li class=\"mb-3\"><i class=\"fas fa-check-circle text-cyan me-2\"></i>Frame the leaf close enough to see symptoms.</li>
                    <li class=\"mb-3\"><i class=\"fas fa-check-circle text-cyan me-2\"></i>Avoid shadows and reflections.</li>
                    <li><i class=\"fas fa-check-circle text-cyan me-2\"></i>Use a dark background for better AI performance.</li>
                </ul>
            </div>
            <div class=\"glass-card p-4\">
                <h4 class=\"section-title mb-3\">How it works</h4>
                <div class=\"text-muted\">
                    <p><strong>1.</strong> Select your crop and upload a leaf image.</p>
                    <p><strong>2.</strong> The AI model analyzes disease patterns.</p>
                    <p><strong>3.</strong> Receive confidence metrics and treatment advice.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src=\"{{ url_for('static', filename='js/upload.js') }}\"></script>
{% endblock %}
""",
}

for path, content in files.items():
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
print('Wrote', len(files), 'files.')
