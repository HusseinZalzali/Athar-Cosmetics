from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///athar.db')
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

CORS(app, origins=['http://localhost:4200'], supports_credentials=True)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

