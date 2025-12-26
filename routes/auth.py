from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User

auth_bp = Blueprint('auth', __name__)

def json_response(success=True, data=None, message=None, errors=None, status_code=200):
    response = {'success': success}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return json_response(False, message='Missing required fields', errors=['email, password, and name are required'], status_code=400)
        
        if User.query.filter_by(email=data['email']).first():
            return json_response(False, message='Email already registered', errors=['Email already exists'], status_code=400)
        
        user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'customer')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        
        return json_response(True, data={
            'user': user.to_dict(),
            'token': access_token
        }, message='Registration successful', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Registration failed', errors=[str(e)], status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return json_response(False, message='Missing email or password', errors=['Email and password are required'], status_code=400)
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return json_response(False, message='Invalid credentials', errors=['Invalid email or password'], status_code=401)
        
        access_token = create_access_token(identity=str(user.id))
        
        return json_response(True, data={
            'user': user.to_dict(),
            'token': access_token
        }, message='Login successful')
    
    except Exception as e:
        return json_response(False, message='Login failed', errors=[str(e)], status_code=500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return json_response(False, message='User not found', status_code=404)
        
        return json_response(True, data={'user': user.to_dict()})
    
    except Exception as e:
        return json_response(False, message='Failed to get user', errors=[str(e)], status_code=500)

