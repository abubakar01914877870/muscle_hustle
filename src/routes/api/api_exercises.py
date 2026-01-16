"""
Exercise Library API Endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from ...database import get_db
from ...models.exercise_mongo import Exercise
from ...utils.jwt_utils import jwt_required

bp = Blueprint('api_exercises', __name__, url_prefix='/api/v1/exercises')


def exercise_to_dict(exercise):
    """Convert exercise to API response"""
    return {
        'id': exercise.id,
        'name': exercise.name,
        'description': exercise.description,
        'category': exercise.category,
        'muscle_group': exercise.muscle_group,
        'equipment': exercise.equipment,
        'instructions': exercise.instructions,
        'image_url': exercise.image_url,
        'video_url': exercise.video_url,
        'is_custom': exercise.is_custom,
        'created_at': exercise.created_at.isoformat() if exercise.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required
def list_exercises(current_user):
    """List exercises with filters and pagination"""
    try:
        db = get_db()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category')
        muscle_group = request.args.get('muscle_group')
        search = request.args.get('search')
        
        # Build query
        query = {}
        
        if category:
            query['category'] = category
        
        if muscle_group:
            query['muscle_group'] = muscle_group
        
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        
        # Get total count
        total = db.exercises.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * limit
        cursor = db.exercises.find(query).skip(skip).limit(limit)
        
        exercises = []
        for doc in cursor:
            ex = Exercise(doc)
            exercises.append(exercise_to_dict(ex))
        
        return jsonify({
            'exercises': exercises,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch exercises',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<exercise_id>', methods=['GET'])
@jwt_required
def get_exercise(current_user, exercise_id):
    """Get exercise details"""
    try:
        db = get_db()
        exercise = Exercise.find_by_id(db, exercise_id)
        
        if not exercise:
            return jsonify({
                'error': 'Exercise not found',
                'code': 'NOT_FOUND'
            }), 404
        
        return jsonify({
            'exercise': exercise_to_dict(exercise)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch exercise',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/sync', methods=['GET'])
@jwt_required
def sync_exercises(current_user):
    """Get exercises changed since timestamp"""
    try:
        db = get_db()
        
        # Get since parameter
        since_str = request.args.get('since')
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            # Return all exercises
            since = datetime(2020, 1, 1)
        
        # Get exercises created/updated after since
        query = {
            'created_at': {'$gte': since}
        }
        
        exercises = []
        for doc in db.exercises.find(query):
            ex = Exercise(doc)
            exercises.append(exercise_to_dict(ex))
        
        return jsonify({
            'exercises': exercises,
            'deleted_ids': [],
            'last_sync': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to sync exercises',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500
