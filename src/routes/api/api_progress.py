"""
Progress Tracking API Endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import base64
from bson import ObjectId
from ...database import get_db
from ...models.progress_mongo import ProgressEntry
from ...utils.jwt_utils import jwt_required

bp = Blueprint('api_progress', __name__, url_prefix='/api/v1/progress')


def progress_to_dict(entry):
    """Convert progress entry to API response"""
    measurements = {}
    if entry.chest:
        measurements['chest'] = entry.chest
    if entry.waist:
        measurements['waist'] = entry.waist
    if entry.hips:
        measurements['hips'] = entry.hips
    if entry.arms:
        measurements['arms'] = entry.arms
    if entry.thighs:
        measurements['thighs'] = entry.thighs
    
    return {
        'id': entry.id,
        'weight': entry.weight,
        'body_fat': entry.body_fat,
        'measurements': measurements if measurements else None,
        'notes': entry.notes,
        'photo_url': entry.get_photo_url(),
        'recorded_date': entry.created_at.isoformat() if entry.created_at else None,
        'created_at': entry.created_at.isoformat() if entry.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required
def list_progress(current_user):
    """List progress entries with pagination"""
    try:
        db = get_db()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Get all entries for user
        all_entries = ProgressEntry.find_by_user(db, current_user.id)
        
        # Pagination
        total = len(all_entries)
        start = (page - 1) * limit
        end = start + limit
        paginated = all_entries[start:end]
        
        entries = [progress_to_dict(e) for e in paginated]
        
        return jsonify({
            'entries': entries,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch progress entries',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<entry_id>', methods=['GET'])
@jwt_required
def get_progress(current_user, entry_id):
    """Get progress entry details"""
    try:
        db = get_db()
        entry = ProgressEntry.find_by_id(db, entry_id)
        
        if not entry or entry.user_id != current_user.id:
            return jsonify({
                'error': 'Progress entry not found',
                'code': 'NOT_FOUND'
            }), 404
        
        return jsonify({
            'entry': progress_to_dict(entry)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch progress entry',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('', methods=['POST'])
@jwt_required
def create_progress(current_user):
    """Create progress entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'code': 'MISSING_DATA'
            }), 400
        
        db = get_db()
        
        # Extract measurements
        measurements = data.get('measurements', {})
        
        # Handle photo if provided (base64)
        photo_data = None
        photo_type = 'image/jpeg'
        if data.get('photo_base64'):
            photo_data = data['photo_base64']
            photo_type = data.get('photo_type', 'image/jpeg')
        
        entry = ProgressEntry.create(
            db,
            current_user.id,
            weight=data.get('weight'),
            body_fat=data.get('body_fat'),
            chest=measurements.get('chest'),
            waist=measurements.get('waist'),
            hips=measurements.get('hips'),
            arms=measurements.get('arms'),
            thighs=measurements.get('thighs'),
            notes=data.get('notes'),
            photo_data=photo_data,
            photo_type=photo_type
        )
        
        return jsonify({
            'entry': progress_to_dict(entry)
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create progress entry',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<entry_id>', methods=['DELETE'])
@jwt_required
def delete_progress(current_user, entry_id):
    """Delete progress entry"""
    try:
        db = get_db()
        
        # Verify ownership
        entry = ProgressEntry.find_by_id(db, entry_id)
        
        if not entry or entry.user_id != current_user.id:
            return jsonify({
                'error': 'Progress entry not found',
                'code': 'NOT_FOUND'
            }), 404
        
        ProgressEntry.delete(db, entry_id)
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete progress entry',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/sync', methods=['GET'])
@jwt_required
def sync_progress(current_user):
    """Get progress entries changed since timestamp"""
    try:
        db = get_db()
        
        # Get since parameter
        since_str = request.args.get('since')
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            # Return all entries
            since = datetime(2020, 1, 1)
        
        # Get entries created after since
        entries_list = ProgressEntry.find_by_user_since(db, current_user.id, since)
        
        entries = [progress_to_dict(e) for e in entries_list]
        
        return jsonify({
            'entries': entries,
            'deleted_ids': [],
            'last_sync': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to sync progress entries',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500
