"""
Flask Backend Application
Main application entry point with API routes and logic.
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import sys
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import json

from flask import (
    Flask, render_template, request, jsonify, 
    session, redirect, url_for, send_file
)

# Import existing ML modules
from config import get_config, Config
from database import Database
from feature_extractor import FeatureExtractor
from predict_disease import load_model, MODEL_CONFIG
from preprocess import preprocess_image
from ollama_crop_advisor import generate_ai_advice, get_disease_prediction
from reports import ReportGenerator

import numpy as np
from PIL import Image


# =====================================================
# FLASK APP INITIALIZATION
# =====================================================

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app_config = get_config(config_name)
    app.config.from_object(app_config)
    os.makedirs(app.config.get('REPORTS_FOLDER', os.path.join(os.getcwd(), 'reports')), exist_ok=True)
    
    # Initialize database
    db = Database(app.config['DATABASE_PATH'])
    app.db = db
    
    # Initialize feature extractor
    try:
        app.feature_extractor = FeatureExtractor(batch_size=app.config['BATCH_SIZE'])
        print("[INFO] Feature Extractor initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Feature Extractor: {e}")
        app.feature_extractor = None
    
    # Load pre-trained models
    app.models = {}
    app.label_encoders = {}
    for crop in app.config['MODEL_CONFIG'].keys():
        try:
            model, encoder = load_model(crop)
            if model is not None:
                app.models[crop] = model
                app.label_encoders[crop] = encoder
                print(f"[INFO] Loaded {crop} model successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load {crop} model: {e}")
    
    return app, db


app, db = create_app('development')


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Login required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' not in session:
        return None
    return db.get_user_by_id(session['user_id'])


def _severity_from_confidence(confidence: float) -> str:
    if confidence >= 0.85:
        return 'High'
    if confidence >= 0.6:
        return 'Moderate'
    return 'Low'


def _empty_recommendation_payload(crop: str, disease: str, confidence: float) -> dict:
    severity = _severity_from_confidence(confidence)
    return {
        'severity': severity,
        'disease_summary': '',
        'causes': '',
        'treatment': '',
        'fertilizer_name': '',
        'npk_values': '',
        'fertilizer_recommendation': '',
        'dosage': '',
        'application_timing': '',
        'application_schedule': '',
        'spraying_interval': '',
        'fertilizer_notes': '',
        'organic_alternative': '',
        'prevention_tips': '',
        'recovery_plan': '',
        'full_text': '',
        'raw_response': '',
    }


def _coerce_text(value, fallback=''):
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _coerce_recommendation_payload(recommendation, crop: str, disease: str, confidence: float) -> dict:
    payload = _empty_recommendation_payload(crop, disease, confidence)

    if isinstance(recommendation, dict):
        for key in payload.keys():
            value = recommendation.get(key)
            if value is None:
                continue
            payload[key] = value

        payload['severity'] = payload.get('severity') or _severity_from_confidence(confidence)
        payload['application_schedule'] = payload.get('application_schedule') or payload.get('application_timing') or ''
        payload['application_timing'] = payload.get('application_timing') or payload.get('application_schedule') or ''

        if not payload['full_text']:
            sections = [
                ('Disease Summary', payload.get('disease_summary')),
                ('Causes', payload.get('causes')),
                ('Treatment', payload.get('treatment')),
                ('Fertilizer Name', payload.get('fertilizer_name')),
                ('NPK Values', payload.get('npk_values')),
                ('Fertilizer Recommendation', payload.get('fertilizer_recommendation')),
                ('Dosage', payload.get('dosage')),
                ('Application Timing', payload.get('application_timing')),
                ('Spraying Interval', payload.get('spraying_interval')),
                ('Organic Alternatives', payload.get('organic_alternative')),
                ('Prevention Tips', payload.get('prevention_tips')),
                ('7-Day Recovery Plan', payload.get('recovery_plan')),
            ]
            payload['full_text'] = '\n\n'.join(
                f"{title}\n{body}" for title, body in sections if body
            )
        return payload

    if recommendation:
        payload['full_text'] = str(recommendation)
        payload['raw_response'] = str(recommendation)

    payload['severity'] = payload.get('severity') or _severity_from_confidence(confidence)
    return payload


def _prediction_to_api_payload(prediction: dict) -> dict:
    if prediction is None:
        return {}

    confidence = float(prediction.get('confidence', 0) or 0)
    payload = {
        'id': prediction.get('id'),
        'crop': prediction.get('crop', ''),
        'disease': prediction.get('disease', ''),
        'confidence': confidence,
        'confidence_percent': f"{confidence * 100:.2f}%",
        'image_path': f"/uploads/{prediction.get('image_filename', '')}",
        'created_at': prediction.get('created_at'),
        'ai_advice': prediction.get('ai_advice') or '',
        'disease_summary': prediction.get('disease_summary') or '',
        'causes': prediction.get('causes') or '',
        'treatment': prediction.get('treatment') or '',
        'fertilizer_name': prediction.get('fertilizer_name') or '',
        'npk_values': prediction.get('npk_values') or '',
        'fertilizer_recommendation': prediction.get('fertilizer_recommendation') or '',
        'dosage': prediction.get('dosage') or '',
        'application_timing': prediction.get('application_timing') or '',
        'application_schedule': prediction.get('application_timing') or '',
        'spraying_interval': prediction.get('spraying_interval') or '',
        'fertilizer_notes': prediction.get('fertilizer_notes') or '',
        'organic_alternative': prediction.get('organic_alternative') or '',
        'severity': prediction.get('severity') or _severity_from_confidence(confidence),
        'prevention_tips': prediction.get('prevention_tips') or '',
        'recovery_plan': prediction.get('recovery_plan') or '',
        'full_text': prediction.get('ai_advice') or '',
        'all_probabilities': prediction.get('all_probabilities') or {}
    }
    return payload


def _prediction_detail_payload(prediction: dict) -> dict:
    payload = _prediction_to_api_payload(prediction)
    payload['image_filename'] = prediction.get('image_filename', '')
    payload['user_id'] = prediction.get('user_id')
    payload['all_probabilities'] = prediction.get('all_probabilities') or {}
    payload['report_path'] = prediction.get('report_path')
    payload['report_generated_at'] = prediction.get('report_generated_at')
    payload['report_url'] = url_for('download_report', prediction_id=prediction.get('id')) if prediction.get('id') else None
    return payload


def _prediction_has_owner(prediction: dict) -> bool:
    return bool(prediction and prediction.get('user_id') == session.get('user_id'))


def _report_download_url(prediction_id: int) -> str:
    return url_for('download_report', prediction_id=prediction_id)


def _ensure_report_folder() -> str:
    reports_folder = app.config.get('REPORTS_FOLDER', os.path.join(os.getcwd(), 'reports'))
    os.makedirs(reports_folder, exist_ok=True)
    return reports_folder


def _save_prediction_report(prediction: dict, user_name: str) -> str:
    reports_folder = _ensure_report_folder()
    safe_name = secure_filename(
        f"prediction_report_{prediction.get('id')}_{prediction.get('crop', 'crop')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    report_path = os.path.join(reports_folder, safe_name)
    pdf_buffer = ReportGenerator.generate_prediction_report_pdf(
        prediction,
        user_name=user_name
    )
    with open(report_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    db.update_prediction_report(
        prediction.get('id'),
        report_path,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    )
    return report_path


def _generate_voice_assistant_response(crop: str, disease: str, question: str) -> dict:
    """Generate an assistant answer for a voice query and preserve AI context."""
    try:
        recommendation = generate_ai_advice(crop, disease, 0.75)
        if isinstance(recommendation, dict):
            answer_text = recommendation.get('full_text') or recommendation.get('raw_response') or ''
        else:
            answer_text = str(recommendation or '')

        if question:
            answer_text = f"Question: {question}\n\n{answer_text}".strip()

        return {
            'answer': answer_text,
            'source': 'ai_advice'
        }
    except Exception as e:
        print(f"[ERROR] Voice assistant failed to generate response: {e}")
        fallback = (
            f"Question: {question}\n\n"
            f"I recommend reviewing the crop condition for {crop} and the issue '{disease}'. "
            "Use targeted treatments, maintain proper crop hygiene, and monitor field conditions closely."
        )
        return {'answer': fallback, 'source': 'fallback'}


# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            if not username or not email or not password:
                return jsonify({'error': 'All fields required'}), 400
            
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Add user to database
            user_id = db.add_user(username, email, password_hash)
            
            if user_id is None:
                return jsonify({'error': 'Username or email already exists'}), 400
            
            if request.is_json:
                return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201
            
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"[ERROR] Registration failed: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            # Get user from database
            user = db.get_user(username)
            
            if user is None or not check_password_hash(user['password_hash'], password):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            # Set session
            session['user_id'] = user['id']
            session.permanent = True
            app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
            
            if request.is_json:
                return jsonify({'message': 'Login successful', 'user_id': user['id']}), 200
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            return jsonify({'error': 'Login failed'}), 500
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))


# =====================================================
# MAIN ROUTES
# =====================================================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = get_current_user()
    stats = db.get_dashboard_stats()
    predictions = db.get_user_predictions(session['user_id'], limit=10)
    
    return render_template('dashboard.html', 
                         user=user, 
                         predictions=predictions,
                         stats=stats)


@app.route('/upload')
@login_required
def upload_page():
    """Upload and predict page"""
    crops = list(app.config['MODEL_CONFIG'].keys())
    return render_template('upload.html', crops=crops)


@app.route('/advisor')
@login_required
def advisor_page():
    """AI Advisor page"""
    crops = list(app.config['MODEL_CONFIG'].keys())
    return render_template('advisor.html', crops=crops)


@app.route('/results')
@login_required
def results_page():
    """Prediction result detail page"""
    return render_template('results.html')


@app.route('/history')
@login_required
def history_page():
    """Prediction history page"""
    return render_template('history.html')


@app.route('/profile')
@login_required
def profile_page():
    """User profile page"""
    return render_template('profile.html')


# =====================================================
# API ROUTES - PREDICTION
# =====================================================

@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """
    API endpoint for disease prediction
    
    Expected form data:
    - file: image file
    - crop: crop name (banana/corn/sugarcane)
    - include_advice: boolean (default: true)
    """
    try:
        # Check for required fields
        if 'file' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        crop = request.form.get('crop', '').lower().strip()
        include_advice = request.form.get('include_advice', 'true').lower() == 'true'
        
        if not crop or crop not in app.config['MODEL_CONFIG']:
            crops = list(app.config['MODEL_CONFIG'].keys())
            return jsonify({'error': f'Invalid crop. Supported: {crops}'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png, gif, bmp'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Preprocess image
        img = preprocess_image(file_path)
        if img is None:
            os.remove(file_path)
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Check if models are loaded
        if crop not in app.models:
            os.remove(file_path)
            return jsonify({'error': f'Model for {crop} not available'}), 503
        
        if app.feature_extractor is None:
            os.remove(file_path)
            return jsonify({'error': 'Feature extractor not available'}), 503
        
        # Feature extraction
        img_batch = np.expand_dims(img, axis=0)
        features = app.feature_extractor.extract_from_array(img_batch)
        
        # Prediction
        model = app.models[crop]
        label_encoder = app.label_encoders[crop]
        
        probabilities = model.predict_proba(features)[0]
        pred_idx = np.argmax(probabilities)
        confidence = float(probabilities[pred_idx])
        disease_name = label_encoder.inverse_transform([pred_idx])[0]

        # Get all class probabilities
        all_probabilities = {
            label_encoder.inverse_transform([i])[0]: float(probabilities[i])
            for i in range(len(probabilities))
        }
        
        # Generate AI advice if requested
        recommendation_data = _empty_recommendation_payload(crop, disease_name, confidence)
        if include_advice:
            try:
                recommendation_data = _coerce_recommendation_payload(
                    generate_ai_advice(crop, disease_name, confidence),
                    crop,
                    disease_name,
                    confidence
                )
            except Exception as e:
                print(f"[WARNING] Failed to generate AI advice: {e}")
        
        ai_advice = recommendation_data['full_text']
        prediction_data = {
            'id': None,
            'user_id': session['user_id'],
            'crop': crop,
            'disease': disease_name,
            'confidence': confidence,
            'confidence_percent': f"{confidence * 100:.2f}%",
            'image_filename': unique_filename,
            'image_path': f"/uploads/{unique_filename}",
            'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'ai_advice': ai_advice,
            'disease_summary': _coerce_text(recommendation_data.get('disease_summary'), 'No disease summary generated.'),
            'causes': _coerce_text(recommendation_data.get('causes'), 'No causes summary generated.'),
            'treatment': _coerce_text(recommendation_data.get('treatment'), 'No treatment recommendation generated.'),
            'fertilizer_name': _coerce_text(recommendation_data.get('fertilizer_name'), 'Not Available'),
            'npk_values': _coerce_text(recommendation_data.get('npk_values'), 'Not Available'),
            'fertilizer_recommendation': _coerce_text(recommendation_data.get('fertilizer_recommendation'), 'No recommendation generated.'),
            'dosage': _coerce_text(recommendation_data.get('dosage'), 'Not Available'),
            'application_timing': _coerce_text(recommendation_data.get('application_timing'), 'Not Available'),
            'application_schedule': _coerce_text(recommendation_data.get('application_schedule'), 'Not Available'),
            'spraying_interval': _coerce_text(recommendation_data.get('spraying_interval'), 'Not Available'),
            'fertilizer_notes': _coerce_text(recommendation_data.get('fertilizer_notes'), 'Not Available'),
            'organic_alternative': _coerce_text(recommendation_data.get('organic_alternative'), 'Not Available'),
            'severity': recommendation_data.get('severity') or _severity_from_confidence(confidence),
            'prevention_tips': _coerce_text(recommendation_data.get('prevention_tips'), 'No prevention tips generated.'),
            'recovery_plan': _coerce_text(recommendation_data.get('recovery_plan'), 'No recovery plan generated.'),
            'full_text': ai_advice,
            'all_probabilities': all_probabilities
        }

        # Store prediction in database
        prediction_id = db.add_prediction(
            user_id=session['user_id'],
            crop=crop,
            disease=disease_name,
            confidence=confidence,
            image_filename=unique_filename,
            image_path=f"/uploads/{unique_filename}",
            ai_advice=ai_advice,
            disease_summary=recommendation_data.get('disease_summary'),
            causes=recommendation_data.get('causes'),
            treatment=recommendation_data.get('treatment'),
            fertilizer_name=recommendation_data.get('fertilizer_name'),
            npk_values=recommendation_data.get('npk_values'),
            fertilizer_recommendation=recommendation_data.get('fertilizer_recommendation'),
            severity=recommendation_data.get('severity'),
            prevention_tips=recommendation_data.get('prevention_tips'),
            recovery_plan=recommendation_data.get('recovery_plan'),
            dosage=recommendation_data.get('dosage'),
            application_timing=recommendation_data.get('application_timing'),
            spraying_interval=recommendation_data.get('spraying_interval'),
            fertilizer_notes=recommendation_data.get('fertilizer_notes'),
            organic_alternative=recommendation_data.get('organic_alternative'),
            probability_data=json.dumps(all_probabilities)
        )
        
        if prediction_id is None:
            os.remove(file_path)
            return jsonify({'error': 'Failed to save prediction'}), 500

        prediction_data['id'] = prediction_id

        if recommendation_data.get('fertilizer_name') or recommendation_data.get('fertilizer_recommendation'):
            db.add_fertilizer_recommendation(
                crop=crop,
                disease=disease_name,
                fertilizer=recommendation_data.get('fertilizer_name') or recommendation_data.get('fertilizer_recommendation'),
                dosage=recommendation_data.get('dosage'),
                timing=recommendation_data.get('application_timing') or recommendation_data.get('application_schedule'),
                notes=' '.join(filter(None, [
                    recommendation_data.get('fertilizer_recommendation'),
                    recommendation_data.get('organic_alternative'),
                    recommendation_data.get('prevention_tips')
                ]))
            )
        
        return jsonify({
            'success': True,
                'prediction': prediction_data,
            'prediction_id': prediction_id,
            'crop': crop,
            'disease': disease_name,
            'confidence': confidence,
            'confidence_percent': f"{confidence * 100:.2f}%",
            'all_probabilities': all_probabilities,
            'ai_advice': ai_advice,
            'fertilizer_name': recommendation_data.get('fertilizer_name'),
            'npk_values': recommendation_data.get('npk_values'),
            'full_text': recommendation_data['full_text'],
            'severity': recommendation_data['severity'],
            'disease_summary': recommendation_data['disease_summary'],
            'causes': recommendation_data['causes'],
            'treatment': recommendation_data['treatment'],
            'fertilizer_recommendation': recommendation_data['fertilizer_recommendation'],
            'dosage': recommendation_data['dosage'],
            'application_timing': recommendation_data['application_timing'],
            'application_schedule': recommendation_data['application_schedule'],
            'spraying_interval': recommendation_data.get('spraying_interval'),
            'fertilizer_notes': recommendation_data.get('fertilizer_notes'),
            'organic_alternative': recommendation_data['organic_alternative'],
            'prevention_tips': recommendation_data['prevention_tips'],
            'recovery_plan': recommendation_data['recovery_plan'],
            'image_path': f"/uploads/{unique_filename}"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Get user prediction history"""
    try:
        limit = request.args.get('limit', 1000, type=int)
        search = request.args.get('search', type=str)
        crop = request.args.get('crop', type=str)
        status = request.args.get('status', type=str)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        sort_order = request.args.get('sort_order', 'DESC', type=str)

        predictions = db.get_user_predictions(
            session['user_id'],
            limit=limit,
            search=search,
            crop=crop,
            status=status,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            'success': True,
            'total': len(predictions),
            'predictions': [
                _prediction_to_api_payload(p)
                for p in predictions
            ]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch history: {e}")
        return jsonify({'error': 'Failed to fetch history'}), 500


@app.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    """Get dashboard summary for user and system metrics"""
    try:
        stats = db.get_dashboard_stats()
        recent_predictions = db.get_user_predictions(
            session['user_id'],
            limit=10,
            sort_by='created_at',
            sort_order='DESC'
        )
        return jsonify({
            'success': True,
            'stats': stats,
            'recent_predictions': [
                _prediction_to_api_payload(p)
                for p in recent_predictions
            ]
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to fetch dashboard data: {e}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500


@app.route('/api/predictions', methods=['GET'])
@login_required
def api_predictions():
    return api_history()


@app.route('/api/prediction/<int:prediction_id>', methods=['GET'])
@login_required
def api_get_prediction(prediction_id):
    """Get specific prediction details"""
    try:
        prediction = db.get_prediction(prediction_id)
        
        if prediction is None:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Verify user owns this prediction
        if prediction['user_id'] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        feedback = db.get_prediction_feedback(prediction_id)
        
        return jsonify({
            'success': True,
            'prediction': _prediction_detail_payload(prediction),
            'feedback': dict(feedback) if feedback else None,
            'fertilizer_history': db.get_fertilizer_recommendations(prediction['crop'], prediction['disease'])
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to get prediction: {e}")
        return jsonify({'error': 'Failed to get prediction'}), 500


@app.route('/api/voice-query', methods=['POST'])
@login_required
def api_voice_query():
    """Create a voice assistant query and return AI response."""
    try:
        data = request.get_json() or {}
        crop = (data.get('crop') or '').strip().lower()
        disease = (data.get('disease') or '').strip()
        question = (data.get('question') or '').strip()
        transcript = (data.get('transcript') or '').strip()

        if not crop or not disease or not question:
            return jsonify({'error': 'Crop, disease, and question are required'}), 400

        if crop not in app.config['MODEL_CONFIG']:
            return jsonify({'error': 'Invalid crop'}), 400

        response_payload = _generate_voice_assistant_response(crop, disease, question)
        query_id = db.add_voice_query(
            session['user_id'],
            crop,
            disease,
            question,
            transcript,
            response_payload['answer']
        )

        return jsonify({
            'success': True,
            'query_id': query_id,
            'answer': response_payload['answer'],
            'source': response_payload.get('source', 'ai_advice')
        }), 200
    except Exception as e:
        print(f"[ERROR] Voice query failed: {e}")
        return jsonify({'error': 'Voice query failed'}), 500


@app.route('/api/voice-history', methods=['GET'])
@login_required
def api_voice_history():
    """Fetch recent voice assistant queries."""
    try:
        queries = db.get_voice_queries(session['user_id'], limit=20)
        return jsonify({
            'success': True,
            'queries': [
                {
                    'id': q['id'],
                    'crop': q['crop'],
                    'disease': q['disease'],
                    'question': q['question'],
                    'transcript': q['transcript'],
                    'answer': q['ai_response'],
                    'created_at': q['created_at']
                }
                for q in queries
            ]
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to load voice history: {e}")
        return jsonify({'error': 'Failed to load voice history'}), 500


# =====================================================
# API ROUTES - FEEDBACK
# =====================================================

@app.route('/api/feedback', methods=['POST'])
@login_required
def api_add_feedback():
    """Add feedback for a prediction"""
    try:
        data = request.get_json()
        prediction_id = data.get('prediction_id')
        user_feedback = data.get('feedback')
        rating = data.get('rating')
        
        if not prediction_id:
            return jsonify({'error': 'prediction_id required'}), 400
        
        # Verify user owns this prediction
        prediction = db.get_prediction(prediction_id)
        if prediction is None or prediction['user_id'] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        feedback_id = db.add_feedback(prediction_id, user_feedback, rating)
        
        if feedback_id is None:
            return jsonify({'error': 'Failed to save feedback'}), 500
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback saved successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to add feedback: {e}")
        return jsonify({'error': 'Failed to add feedback'}), 500


# =====================================================
# API ROUTES - STATISTICS
# =====================================================

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get global statistics"""
    try:
        stats = db.get_dashboard_stats()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500


@app.route('/api/crop-stats/<crop>', methods=['GET'])
def api_crop_stats(crop):
    """Get statistics for specific crop"""
    try:
        crop = crop.lower()
        if crop not in app.config['MODEL_CONFIG']:
            return jsonify({'error': 'Invalid crop'}), 400
        
        stats = db.get_crop_stats(crop)
        return jsonify({
            'success': True,
            'crop': crop,
            'stats': [{'disease': s['disease'], 'count': s['count']} for s in stats]
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to get crop stats: {e}")
        return jsonify({'error': 'Failed to get crop stats'}), 500


# =====================================================
# API ROUTES - REPORTS
# =====================================================

def _ensure_prediction_report(prediction: dict) -> str:
    user = get_current_user()
    report_path = prediction.get('report_path')
    if report_path and os.path.exists(report_path):
        return report_path
    return _save_prediction_report(prediction, user_name=user['username'] if user else 'Unknown')


@app.route('/generate-report/<int:prediction_id>', methods=['GET'])
@login_required
def generate_report(prediction_id):
    """Generate and save a PDF report for a prediction"""
    try:
        prediction = db.get_prediction(prediction_id)

        if prediction is None:
            return jsonify({'error': 'Prediction not found'}), 404

        if not _prediction_has_owner(prediction):
            return jsonify({'error': 'Unauthorized'}), 403

        report_path = _ensure_prediction_report(prediction)
        report_url = url_for('download_report', prediction_id=prediction_id)

        return jsonify({
            'success': True,
            'report_path': report_path,
            'report_url': report_url
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to generate report: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500


@app.route('/download-report/<int:prediction_id>', methods=['GET'])
@login_required
def download_report(prediction_id):
    """Download an existing or newly generated PDF report"""
    try:
        prediction = db.get_prediction(prediction_id)

        if prediction is None:
            return jsonify({'error': 'Prediction not found'}), 404

        if not _prediction_has_owner(prediction):
            return jsonify({'error': 'Unauthorized'}), 403

        report_path = prediction.get('report_path')
        if not report_path or not os.path.exists(report_path):
            report_path = _ensure_prediction_report(prediction)

        return send_file(
            report_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"prediction_report_{prediction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        print(f"[ERROR] Failed to download report: {e}")
        return jsonify({'error': 'Failed to download report'}), 500


@app.route('/api/report/<int:prediction_id>', methods=['GET'])
@app.route('/api/reports/prediction/<int:prediction_id>', methods=['GET'])
@login_required
def api_prediction_report(prediction_id):
    """Backward-compatible alias for prediction report downloads"""
    return download_report(prediction_id)


@app.route('/api/reports/history', methods=['GET'])
@login_required
def api_history_report():
    """Download history report as PDF or CSV"""
    try:
        report_format = request.args.get('format', 'pdf').lower()
        predictions = db.get_user_predictions(session['user_id'], limit=1000)
        user = get_current_user()

        if report_format == 'pdf':
            pdf_buffer = ReportGenerator.generate_history_report_pdf(
                predictions,
                user_name=user['username'] if user else 'Unknown'
            )
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

        if report_format == 'csv':
            csv_content = ReportGenerator.generate_history_report_csv(predictions)
            response = app.response_class(csv_content, mimetype='text/csv')
            response.headers['Content-Disposition'] = (
                f"attachment; filename=history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            return response

        return jsonify({'error': 'Invalid format. Supported: pdf, csv'}), 400
    except Exception as e:
        print(f"[ERROR] Failed to generate history report: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500


# =====================================================
# FILE SERVING
# =====================================================

@app.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded image files"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/jpeg')
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"[ERROR] Failed to serve file: {e}")
        return jsonify({'error': 'Failed to serve file'}), 500


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.is_json:
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.is_json:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# =====================================================
# CONTEXT PROCESSORS
# =====================================================

@app.context_processor
def inject_user():
    """Inject user into template context"""
    user = None
    if 'user_id' in session:
        user = get_current_user()
    return {'current_user': user}


@app.context_processor
def inject_config():
    """Inject config into template context"""
    return {
        'crops': list(app.config['MODEL_CONFIG'].keys()),
        'model_config': app.config['MODEL_CONFIG']
    }


# =====================================================
# APPLICATION START
# =====================================================

if __name__ == '__main__':
    # Create necessary folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("\n" + "="*50)
    print(" DISEASE DETECTION WEB APP")
    print("="*50)
    print(f"[INFO] Starting Flask server...")
    print(f"[INFO] Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"[INFO] Database: {app.config['DATABASE_PATH']}")
    print(f"[INFO] Loaded crops: {list(app.models.keys())}")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
