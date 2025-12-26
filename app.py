from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Flask to serve Angular static files and templates
app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')

# Handle DATABASE_URL - Render sometimes provides postgres:// instead of postgresql://
# Also handle malformed URLs
database_url = os.getenv('DATABASE_URL', 'sqlite:///athar.db')
if database_url.startswith('postgres://'):
    # SQLAlchemy requires postgresql:// not postgres://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For dev, set to timedelta in production

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'message': 'Token has expired',
        'errors': ['Your session has expired. Please login again.']
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Invalid token',
        'errors': ['Invalid authentication token. Please login again.']
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'message': 'Authorization required',
        'errors': ['Authorization token is missing. Please login.']
    }), 401

# CORS configuration - allow requests from frontend domains
cors_origins = [
    'http://localhost:4200',  # Local development
    'https://athar-cosmetics-front.onrender.com',  # Production frontend
    'https://athar-cosmetics.onrender.com'  # Production backend (if needed)
]
CORS(app, origins=cors_origins, supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

# Import routes after db is initialized
from routes.auth import auth_bp
from routes.catalog import catalog_bp
from routes.orders import orders_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(catalog_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api/orders')

@app.route('/api/health')
def health():
    return {'success': True, 'message': 'API is running'}

# Error handlers
@app.errorhandler(422)
def handle_422(e):
    """Handle 422 Unprocessable Entity errors"""
    import traceback
    print("=== 422 ERROR ===")
    print(f"Error: {e}")
    print(f"Error description: {getattr(e, 'description', 'No description')}")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request data: {request.data}")
    traceback.print_exc()
    
    error_msg = 'The request was well-formed but contains semantic errors.'
    if hasattr(e, 'description'):
        error_msg = str(e.description)
    
    return jsonify({
        'success': False,
        'message': 'Unprocessable Entity',
        'errors': [error_msg]
    }), 422

@app.errorhandler(400)
def handle_400(e):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'success': False,
        'message': 'Bad Request',
        'errors': [str(e.description) if hasattr(e, 'description') else 'Invalid request']
    }), 400

# ---------- SPA FRONTEND ROUTES ----------
# Serve Angular app for all non-API routes
# This must be after all API routes are registered
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def spa(path):
    # Serve Angular index.html for all non-API routes
    # Angular Router will handle client-side routing
    # API routes are already handled above, so this only catches frontend routes
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

