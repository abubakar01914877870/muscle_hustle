"""
Authentication API Endpoints for Mobile App
"""
from flask import Blueprint, request, jsonify
from ...database import get_db
from ...models.user_mongo import User
from ...utils.jwt_utils import (
    generate_access_token,
    generate_refresh_token,
    verify_token,
    jwt_required
)

bp = Blueprint('api_auth', __name__, url_prefix='/api/v1/auth')


def user_to_dict(user):
    """Convert user object to dictionary for API response"""
    return {
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_admin': user.is_admin,
        'is_trainer': user.is_trainer,
        'profile_picture': user.get_profile_picture_url(),
        'height': user.height,
        'weight': user.weight,
        'target_weight': user.target_weight,
        'fitness_level': user.fitness_level,
        'fitness_goal': user.fitness_goal,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }


@bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validate password length
        if len(password) < 6:
            return jsonify({
                'error': 'Password must be at least 6 characters',
                'code': 'INVALID_PASSWORD'
            }), 400
        
        # Check if user already exists
        db = get_db()
        existing_user = User.find_by_email(db, email)
        
        if existing_user:
            return jsonify({
                'error': 'Email already registered',
                'code': 'EMAIL_EXISTS'
            }), 400
        
        # Create new user
        user = User.create(db, email, password, is_admin=False)
        
        # Update full name if provided
        if data.get('full_name'):
            User.update(db, user.id, {'full_name': data['full_name']})
            user.full_name = data['full_name']
        
        # Generate tokens
        access_token = generate_access_token(user.id, user.email)
        refresh_token = generate_refresh_token(user.id, user.email)
        
        return jsonify({
            'user': user_to_dict(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Registration failed',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        db = get_db()
        user = User.find_by_email(db, email)
        
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Invalid email or password',
                'code': 'INVALID_CREDENTIALS'
            }), 401
        
        # Generate tokens
        access_token = generate_access_token(user.id, user.email)
        refresh_token = generate_refresh_token(user.id, user.email)
        
        return jsonify({
            'user': user_to_dict(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('refresh_token'):
            return jsonify({
                'error': 'Refresh token is required',
                'code': 'MISSING_TOKEN'
            }), 400
        
        # Verify refresh token
        payload = verify_token(data['refresh_token'], token_type='refresh')
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired refresh token',
                'code': 'INVALID_TOKEN'
            }), 401
        
        # Generate new access token
        access_token = generate_access_token(payload['user_id'], payload['email'])
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Token refresh failed',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/me', methods=['GET'])
@jwt_required
def get_profile(current_user):
    """Get current user profile"""
    try:
        return jsonify({
            'user': user_to_dict(current_user)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch profile',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/me', methods=['PUT'])
@jwt_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'code': 'MISSING_DATA'
            }), 400
        
        # Allowed fields to update
        allowed_fields = [
            'full_name', 'date_of_birth', 'gender', 'phone',
            'height', 'weight', 'target_weight', 'fitness_level',
            'fitness_goal', 'activity_level', 'medical_conditions',
            'dietary_restrictions', 'preferred_workout_time', 'workout_frequency'
        ]
        
        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({
                'error': 'No valid fields to update',
                'code': 'INVALID_DATA'
            }), 400
        
        # Update user
        db = get_db()
        User.update(db, current_user.id, update_data)
        
        # Fetch updated user
        updated_user = User.find_by_id(db, current_user.id)
        
        return jsonify({
            'user': user_to_dict(updated_user)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Profile update failed',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500
