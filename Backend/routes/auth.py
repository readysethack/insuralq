from flask import Blueprint, request, jsonify
from ..services.auth_service import auth_service, user_store
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def token_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            token = auth_service.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        current_user = user_store.get_user_by_id(payload['user_id'])
        if not current_user:
            return jsonify({'message': 'User not found'}), 401
        
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Basic validation
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        # Hash password
        password_hash = auth_service.hash_password(password)
        
        # Create user
        user = user_store.create_user(
            email=email,
            password_hash=password_hash,
            name=data.get('name', '')
        )
        
        # Generate token
        token = auth_service.generate_token(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user,
            'token': token
        }), 201
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 409
    except Exception as e:
        return jsonify({'message': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user
        user = user_store.get_user_by_email(email)
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Verify password
        if not auth_service.verify_password(password, user['password_hash']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate token
        user_response = user.copy()
        del user_response['password_hash']
        token = auth_service.generate_token(user_response)
        
        return jsonify({
            'message': 'Login successful',
            'user': user_response,
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    user = request.current_user.copy()
    if 'password_hash' in user:
        del user['password_hash']
    return jsonify({'user': user}), 200

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify token validity"""
    try:
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            token = auth_service.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'valid': False, 'message': 'Token missing'}), 400
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'valid': False, 'message': 'Invalid token'}), 401
        
        return jsonify({'valid': True, 'payload': payload}), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Token verification failed'}), 500
