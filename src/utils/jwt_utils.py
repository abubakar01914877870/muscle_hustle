"""
JWT Utilities for Mobile API Authentication
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from ..database import get_db
from ..models.user_mongo import User

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRES = timedelta(days=7)
ALGORITHM = 'HS256'


def generate_access_token(user_id, email):
    """Generate JWT access token (15 minutes)"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def generate_refresh_token(user_id, email):
    """Generate JWT refresh token (7 days)"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + REFRESH_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token, token_type='access'):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get('type') != token_type:
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        # Format: "Bearer <token>"
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None


def get_current_user():
    """Get current user from JWT token"""
    token = get_token_from_header()
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    db = get_db()
    user = User.find_by_id(db, payload['user_id'])
    return user


def jwt_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Missing authorization token',
                'code': 'MISSING_TOKEN'
            }), 401
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'INVALID_TOKEN'
            }), 401
        
        # Get user and attach to request
        db = get_db()
        user = User.find_by_id(db, payload['user_id'])
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 401
        
        # Pass user to route function
        return f(user, *args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Missing authorization token',
                'code': 'MISSING_TOKEN'
            }), 401
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'INVALID_TOKEN'
            }), 401
        
        db = get_db()
        user = User.find_by_id(db, payload['user_id'])
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 401
        
        if not user.is_admin:
            return jsonify({
                'error': 'Admin privileges required',
                'code': 'FORBIDDEN'
            }), 403
        
        return f(user, *args, **kwargs)
    
    return decorated_function
