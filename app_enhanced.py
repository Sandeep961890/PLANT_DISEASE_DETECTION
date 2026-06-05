"""
Production-Ready Flask Backend - Enhanced Version
Agricultural Disease Detection API with advanced features
"""

import os
import uuid
import numpy as np
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request, jsonify, session, redirect, 
    url_for, send_file, send_from_directory, make_response
)

# Import custom modules
from database import Database
from config import Config
from feature_extractor import FeatureExtractor
from predict_disease import predict_disease, load_model
from preprocess import preprocess_image
from ollama_crop_advisor import generate_ai_advice
from utils import (
    Logger, Validator, Sanitizer, Pagination, APIResponse, 
    QUERY_CACHE, rate_limit, UPLOAD_LIMITER, API_LIMITER,
    get_time_range
)
from reports import ReportGenerator, ReportExporter
from models import User, Prediction, Feedback


# =====================================================
# INITIALIZATION
# =====================================================

app = Flask(__name__)
app.config.from_object(Config.development)

# Initialize components
logger = Logger('app')
db = Database(app.config['DATABASE_PATH'])
db.init_db()

# Load ML models
logger.info("[STARTUP] Loading feature extractor...")
app.feature_extractor = FeatureExtractor()

logger.info("[STARTUP] Loading trained models...")
app.models = {}
app.label_encoders = {}
for crop in app.config['MODEL_CONFIG'].keys():
    try:
        model_info = app.config['MODEL_CONFIG'][crop]
        model_path = model_info.get('model_path')
        encoder_path = model_info.get('label_encoder_path')
        
        if os.path.exists(model_path) and os.path.exists(encoder_path):
            app.models[crop], app.label_encoders[crop] = load_model(crop, model_path, encoder_path)
            logger.info(f"[STARTUP] Loaded {crop} model: {model_path}")
        else:
            logger.warning(f"[STARTUP] Model not found for {crop}")
    except Exception as e:
        logger.error(f"[STARTUP] Failed to load {crop} model: {e}")

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logger.info("[STARTUP] Flask app initialized successfully")


# =====================================================
# DECORATORS & HELPERS
# =====================================================

def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return APIResponse.error("Not authenticated", code=401)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require admin role (future feature)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return APIResponse.error("Not authenticated", code=401)
        # Add admin check when implemented
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' not in session:
        return None
    return db.get_user_by_id(session['user_id'])


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config['ALLOWED_EXTENSIONS']


def get_user_identifier():
    """Get unique identifier for current user"""
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    return request.remote_addr


# =====================================================
# HEALTH CHECK & API INFO
# =====================================================

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = db.get_user_by_id(1) is None
        
        # Check models
        models_loaded = len(app.models) > 0
        feature_extractor_loaded = app.feature_extractor is not None
        
        return APIResponse.success(
            data={
                'status': 'healthy',
                'database': 'connected' if db_status else 'error',
                'models_loaded': models_loaded,
                'feature_extractor': 'loaded' if feature_extractor_loaded else 'error',
                'available_crops': list(app.models.keys()),
                'timestamp': datetime.utcnow().isoformat()
            },
            message="System is operational"
        )[0], 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse.error(f"Health check failed: {e}", code=500)


@app.route('/api/v1/info', methods=['GET'])
def api_info():
    """Get API information and available crops"""
    try:
        crops_info = {}
        for crop in app.config['MODEL_CONFIG'].keys():
            if crop in app.models:
                diseases = app.config['MODEL_CONFIG'][crop].get('diseases', [])
                crops_info[crop] = {
                    'available': True,
                    'diseases': diseases,
                    'count': len(diseases)
                }
            else:
                crops_info[crop] = {'available': False}
        
        return APIResponse.success(
            data={
                'api_version': 'v1',
                'app_name': 'AI Agricultural Disease Detection',
                'crops': crops_info,
                'features': [
                    'disease_detection',
                    'ai_advice',
                    'prediction_history',
                    'analytics',
                    'report_generation'
                ]
            },
            message="API information retrieved"
        )[0], 200
    except Exception as e:
        logger.error(f"API info retrieval failed: {e}")
        return APIResponse.error(f"Failed to retrieve API info: {e}", code=500)


# =====================================================
# AUTHENTICATION ROUTES (v1)
# =====================================================

@app.route('/api/v1/auth/register', methods=['POST'])
@rate_limit(API_LIMITER, get_user_identifier)
def api_register():
    """API registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return APIResponse.error("Request body required", code=400)
        
        username = Sanitizer.sanitize_string(data.get('username', ''), max_length=50)
        email = Sanitizer.sanitize_string(data.get('email', ''), max_length=120)
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate
        valid, msg = Validator.validate_username(username)
        if not valid:
            return APIResponse.error(msg, code=400)
        
        valid, msg = Validator.validate_email(email)
        if not valid:
            return APIResponse.error(msg, code=400)
        
        valid, msg = Validator.validate_password(password)
        if not valid:
            return APIResponse.error(msg, code=400)
        
        if password != confirm_password:
            return APIResponse.error("Passwords do not match", code=400)
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Add user
        user_id = db.add_user(username, email, password_hash)
        
        if user_id is None:
            return APIResponse.error("Username or email already exists", code=409)
        
        logger.info(f"[AUTH] User registered: {username} (ID: {user_id})")
        
        return APIResponse.success(
            data={'user_id': user_id, 'username': username},
            message="Registration successful",
            code=201
        )
    except Exception as e:
        logger.error(f"[AUTH] Registration error: {e}")
        return APIResponse.error("Registration failed", code=500, details=str(e))


@app.route('/api/v1/auth/login', methods=['POST'])
@rate_limit(API_LIMITER, get_user_identifier)
def api_login():
    """API login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return APIResponse.error("Request body required", code=400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return APIResponse.error("Username and password required", code=400)
        
        # Get user
        user = db.get_user(username)
        
        if user is None or not check_password_hash(user['password_hash'], password):
            logger.warning(f"[AUTH] Failed login attempt for: {username}")
            return APIResponse.error("Invalid credentials", code=401)
        
        # Set session
        session['user_id'] = user['id']
        session.permanent = True
        app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
        
        logger.info(f"[AUTH] User logged in: {username} (ID: {user['id']})")
        
        return APIResponse.success(
            data={'user_id': user['id'], 'username': username},
            message="Login successful"
        )
    except Exception as e:
        logger.error(f"[AUTH] Login error: {e}")
        return APIResponse.error("Login failed", code=500)


@app.route('/api/v1/auth/logout', methods=['POST'])
def api_logout():
    """API logout endpoint"""
    session.clear()
    logger.info("[AUTH] User logged out")
    return APIResponse.success(message="Logout successful")


@app.route('/api/v1/auth/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        
        if not user:
            return APIResponse.error("User not found", code=404)
        
        return APIResponse.success(
            data=user,
            message="Profile retrieved"
        )
    except Exception as e:
        logger.error(f"[AUTH] Profile retrieval error: {e}")
        return APIResponse.error("Failed to retrieve profile", code=500)


# =====================================================
# PREDICTION ROUTES (v1)
# =====================================================

@app.route('/api/v1/predict', methods=['POST'])
@login_required
@rate_limit(UPLOAD_LIMITER, get_user_identifier)
def api_predict_v1():
    """
    Predict disease from uploaded image
    
    Form data:
    - file: Image file
    - crop: Crop name (banana/corn/sugarcane)
    - include_advice: Boolean, generate AI advice (optional)
    """
    file_path = None
    try:
        # Validate file
        if 'file' not in request.files:
            return APIResponse.error("No image file provided", code=400)
        
        crop = request.form.get('crop', '').lower().strip()
        include_advice = request.form.get('include_advice', 'true').lower() == 'true'
        
        # Validate crop
        valid, msg = Validator.validate_crop(crop, list(app.config['MODEL_CONFIG'].keys()))
        if not valid:
            return APIResponse.error(msg, code=400)
        
        file = request.files['file']
        
        if file.filename == '':
            return APIResponse.error("No image selected", code=400)
        
        valid, msg = Validator.validate_file_extension(
            file.filename, 
            app.config['ALLOWED_EXTENSIONS']
        )
        if not valid:
            return APIResponse.error(msg, code=400)
        
        # Check file size
        if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
            return APIResponse.error("File too large", code=413)
        file.seek(0)
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        logger.info(f"[PREDICT] File saved: {unique_filename}")
        
        # Preprocess image
        img = preprocess_image(file_path)
        if img is None:
            return APIResponse.error("Failed to process image", code=400)
        
        # Check models
        if crop not in app.models:
            return APIResponse.error(f"Model for {crop} not available", code=503)
        
        if app.feature_extractor is None:
            return APIResponse.error("Feature extractor not available", code=503)
        
        # Extract features
        img_batch = np.expand_dims(img, axis=0)
        features = app.feature_extractor.extract_from_array(img_batch)
        
        # Predict
        model = app.models[crop]
        label_encoder = app.label_encoders[crop]
        
        probabilities = model.predict_proba(features)[0]
        pred_idx = np.argmax(probabilities)
        confidence = float(probabilities[pred_idx])
        disease_name = label_encoder.inverse_transform([pred_idx])[0]
        
        # Generate AI advice
        ai_advice = None
        if include_advice:
            try:
                ai_advice = generate_ai_advice(crop, disease_name, confidence)
                logger.info(f"[PREDICT] AI advice generated for {crop}/{disease_name}")
            except Exception as e:
                logger.warning(f"[PREDICT] Failed to generate AI advice: {e}")
        
        # Store in database
        prediction_id = db.add_prediction(
            user_id=session['user_id'],
            crop=crop,
            disease=disease_name,
            confidence=confidence,
            image_filename=unique_filename,
            image_path=file_path,
            ai_advice=ai_advice
        )
        
        if prediction_id is None:
            return APIResponse.error("Failed to save prediction", code=500)
        
        # Prepare all probabilities
        all_probabilities = {
            label_encoder.inverse_transform([i])[0]: float(probabilities[i])
            for i in range(len(probabilities))
        }
        
        logger.info(f"[PREDICT] Prediction successful: {disease_name} ({confidence*100:.2f}%)")
        
        return APIResponse.success(
            data={
                'prediction_id': prediction_id,
                'crop': crop,
                'disease': disease_name,
                'confidence': confidence,
                'confidence_percent': f"{confidence * 100:.2f}%",
                'all_probabilities': all_probabilities,
                'ai_advice': ai_advice,
                'image_path': f"/uploads/{unique_filename}"
            },
            message="Prediction successful"
        )
    
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"[PREDICT] Error: {e}", exc_info=True)
        return APIResponse.error("Prediction failed", code=500, details=str(e))


@app.route('/api/v1/predictions', methods=['GET'])
@login_required
def api_get_predictions():
    """Get user prediction history"""
    try:
        page, per_page = Pagination.get_pagination_params(request.args)
        
        predictions = db.get_user_predictions(session['user_id'], limit=per_page * 10)
        
        pagination_data = Pagination.paginate_list(predictions, page, per_page)
        
        # Convert to dicts
        items = [
            {
                'id': p['id'],
                'crop': p['crop'],
                'disease': p['disease'],
                'confidence': p['confidence'],
                'confidence_percent': f"{p['confidence'] * 100:.2f}%",
                'image_path': f"/uploads/{p['image_filename']}",
                'created_at': p['created_at'],
                'ai_advice': p['ai_advice'][:200] + '...' if p['ai_advice'] and len(p['ai_advice']) > 200 else p['ai_advice']
            }
            for p in pagination_data['items']
        ]
        
        return APIResponse.paginated(
            items,
            pagination_data,
            message="Prediction history retrieved"
        )
    
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error: {e}")
        return APIResponse.error("Failed to fetch predictions", code=500)


@app.route('/api/v1/predictions/<int:prediction_id>', methods=['GET'])
@login_required
def api_get_prediction_detail(prediction_id):
    """Get specific prediction details"""
    try:
        prediction = db.get_prediction(prediction_id)
        
        if not prediction:
            return APIResponse.error("Prediction not found", code=404)
        
        # Verify ownership
        if prediction['user_id'] != session['user_id']:
            return APIResponse.error("Unauthorized", code=403)
        
        return APIResponse.success(
            data=prediction,
            message="Prediction retrieved"
        )
    
    except Exception as e:
        logger.error(f"[PREDICTION_DETAIL] Error: {e}")
        return APIResponse.error("Failed to retrieve prediction", code=500)


# =====================================================
# REPORT GENERATION ROUTES
# =====================================================

@app.route('/api/v1/reports/prediction/<int:prediction_id>', methods=['GET'])
@login_required
def api_download_prediction_report(prediction_id):
    """Download PDF report for a prediction"""
    try:
        prediction = db.get_prediction(prediction_id)
        
        if not prediction:
            return APIResponse.error("Prediction not found", code=404)
        
        # Verify ownership
        if prediction['user_id'] != session['user_id']:
            return APIResponse.error("Unauthorized", code=403)
        
        user = get_current_user()
        
        # Generate PDF
        pdf_buffer = ReportGenerator.generate_prediction_report_pdf(
            prediction, 
            user_name=user['username']
        )
        
        logger.info(f"[REPORT] Generated PDF report for prediction {prediction_id}")
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"prediction_{prediction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    
    except Exception as e:
        logger.error(f"[REPORT] Error generating report: {e}")
        return APIResponse.error("Failed to generate report", code=500)


@app.route('/api/v1/reports/history', methods=['GET'])
@login_required
def api_download_history_report():
    """Download prediction history report"""
    try:
        report_format = request.args.get('format', 'pdf').lower()
        
        predictions = db.get_user_predictions(session['user_id'], limit=1000)
        user = get_current_user()
        
        if report_format == 'pdf':
            pdf_buffer = ReportGenerator.generate_history_report_pdf(
                predictions,
                user_name=user['username']
            )
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        elif report_format == 'csv':
            csv_content = ReportGenerator.generate_history_report_csv(predictions)
            
            response = make_response(csv_content)
            response.headers['Content-Disposition'] = f"attachment; filename=history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response.headers['Content-Type'] = 'text/csv'
            
            return response
        
        else:
            return APIResponse.error("Invalid format. Supported: pdf, csv", code=400)
    
    except Exception as e:
        logger.error(f"[REPORT] Error generating history report: {e}")
        return APIResponse.error("Failed to generate report", code=500)


# =====================================================
# ANALYTICS ROUTES
# =====================================================

@app.route('/api/v1/analytics/dashboard', methods=['GET'])
@login_required
def api_analytics_dashboard():
    """Get dashboard analytics"""
    try:
        # Check cache first
        cache_key = f"analytics_{session['user_id']}"
        cached = QUERY_CACHE.get(cache_key)
        if cached:
            return APIResponse.success(data=cached, message="Analytics retrieved")
        
        stats = db.get_dashboard_stats()
        user_predictions = db.get_user_predictions(session['user_id'], limit=100)
        
        # Build analytics
        analytics = {
            'total_predictions': len(user_predictions),
            'total_users': stats.get('total_users', 0),
            'healthy_crops': sum(1 for p in user_predictions if 'healthy' in p['disease'].lower()),
            'diseases_detected': len(set(p['disease'] for p in user_predictions)),
            'average_confidence': np.mean([p['confidence'] for p in user_predictions]) if user_predictions else 0,
            'crop_distribution': stats.get('crop_distribution', {}),
            'top_diseases': stats.get('top_diseases', {}),
            'predictions_by_crop': {}
        }
        
        # Predictions by crop
        for crop in app.config['MODEL_CONFIG'].keys():
            crop_preds = [p for p in user_predictions if p['crop'] == crop]
            analytics['predictions_by_crop'][crop] = len(crop_preds)
        
        # Cache results
        QUERY_CACHE.set(cache_key, analytics)
        
        return APIResponse.success(data=analytics, message="Analytics retrieved")
    
    except Exception as e:
        logger.error(f"[ANALYTICS] Error: {e}")
        return APIResponse.error("Failed to retrieve analytics", code=500)


# =====================================================
# WEB ROUTES (legacy, for browser)
# =====================================================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            
            # Validate
            valid, msg = Validator.validate_username(username)
            if not valid:
                return render_template('register.html', error=msg), 400
            
            valid, msg = Validator.validate_email(email)
            if not valid:
                return render_template('register.html', error=msg), 400
            
            valid, msg = Validator.validate_password(password)
            if not valid:
                return render_template('register.html', error=msg), 400
            
            if password != confirm:
                return render_template('register.html', error="Passwords don't match"), 400
            
            password_hash = generate_password_hash(password)
            user_id = db.add_user(username, email, password_hash)
            
            if not user_id:
                return render_template('register.html', error="Username/email already exists"), 409
            
            session['user_id'] = user_id
            logger.info(f"[AUTH] User registered: {username}")
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            logger.error(f"[REGISTER] Error: {e}")
            return render_template('register.html', error="Registration failed"), 500
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                return render_template('login.html', error="Username and password required"), 400
            
            user = db.get_user(username)
            
            if not user or not check_password_hash(user['password_hash'], password):
                logger.warning(f"[AUTH] Failed login: {username}")
                return render_template('login.html', error="Invalid credentials"), 401
            
            session['user_id'] = user['id']
            session.permanent = True
            logger.info(f"[AUTH] User logged in: {username}")
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            logger.error(f"[LOGIN] Error: {e}")
            return render_template('login.html', error="Login failed"), 500
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    logger.info("[AUTH] User logged out")
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard"""
    user = get_current_user()
    stats = db.get_dashboard_stats()
    predictions = db.get_user_predictions(session['user_id'], limit=10)
    
    return render_template('dashboard.html', user=user, predictions=predictions, stats=stats)


@app.route('/upload')
@login_required
def upload_page():
    """Upload page"""
    crops = list(app.config['MODEL_CONFIG'].keys())
    return render_template('upload.html', crops=crops)


@app.route('/advisor')
@login_required
def advisor_page():
    """Advisor page"""
    crops = list(app.config['MODEL_CONFIG'].keys())
    return render_template('advisor.html', crops=crops)


# =====================================================
# FILE SERVING
# =====================================================

@app.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    except Exception as e:
        logger.error(f"[FILE_SERVE] Error: {e}")
        return APIResponse.error("File not found", code=404)


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if request.is_json or request.path.startswith('/api/'):
        return APIResponse.error("Not found", code=404)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"[ERROR] 500: {error}")
    if request.is_json or request.path.startswith('/api/'):
        return APIResponse.error("Internal server error", code=500)
    return render_template('500.html'), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """413 error handler"""
    return APIResponse.error("File too large", code=413)


# =====================================================
# CONTEXT PROCESSORS
# =====================================================

@app.context_processor
def inject_user():
    """Inject user into templates"""
    user = None
    if 'user_id' in session:
        user = get_current_user()
    return {'current_user': user}


@app.context_processor
def inject_config():
    """Inject config into templates"""
    return {
        'crops': list(app.config['MODEL_CONFIG'].keys()),
        'model_config': app.config['MODEL_CONFIG']
    }


# =====================================================
# APPLICATION START
# =====================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("\n" + "="*60)
    print(" PRODUCTION-READY AI DISEASE DETECTION API")
    print("="*60)
    print(f"[INFO] Starting Flask server (v1)...")
    print(f"[INFO] Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"[INFO] Database: {app.config['DATABASE_PATH']}")
    print(f"[INFO] Available crops: {list(app.models.keys())}")
    print(f"[INFO] API Version: /api/v1")
    print(f"[INFO] Health check: /api/v1/health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
