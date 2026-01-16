"""
Workout Management API Endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from ...database import get_db
from ...models.planner import ExerciseGroup, CalendarAssignment, WorkoutLog
from ...models.exercise_mongo import Exercise
from ...utils.jwt_utils import jwt_required

bp = Blueprint('api_workouts', __name__, url_prefix='/api/v1/workouts')


def workout_to_dict(assignment, exercises=None):
    """Convert workout assignment to API response"""
    result = {
        'id': assignment.id,
        'date': assignment.date_str,
        'type': assignment.assignment_type,
        'is_rest_day': assignment.assignment_type == 'rest',
        'created_at': assignment.created_at.isoformat() if assignment.created_at else None
    }
    
    if assignment.exercise_group_id:
        result['workout_group_id'] = str(assignment.exercise_group_id)
        result['workout_name'] = getattr(assignment, 'group_name', None)
    
    if exercises:
        result['exercises'] = [exercise_to_dict(ex) for ex in exercises]
    
    return result


def exercise_to_dict(exercise):
    """Convert exercise to API response"""
    return {
        'id': exercise.id,
        'name': exercise.name,
        'description': exercise.description,
        'category': exercise.category,
        'muscle_group': exercise.muscle_group,
        'equipment': exercise.equipment,
        'instructions': exercise.instructions
    }


@bp.route('', methods=['GET'])
@jwt_required
def list_workouts(current_user):
    """List user's workouts with pagination"""
    try:
        db = get_db()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default date range if not provided (current month)
        if not date_from or not date_to:
            today = datetime.now()
            date_from = today.replace(day=1).strftime('%Y-%m-%d')
            # Last day of month
            if today.month == 12:
                date_to = today.replace(year=today.year+1, month=1, day=1).strftime('%Y-%m-%d')
            else:
                date_to = today.replace(month=today.month+1, day=1).strftime('%Y-%m-%d')
        
        # Get assignments
        assignments = CalendarAssignment.find_by_user_and_date_range(
            db, current_user.id, date_from, date_to
        )
        
        # Pagination
        total = len(assignments)
        start = (page - 1) * limit
        end = start + limit
        paginated = assignments[start:end]
        
        workouts = [workout_to_dict(a) for a in paginated]
        
        return jsonify({
            'workouts': workouts,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch workouts',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<workout_id>', methods=['GET'])
@jwt_required
def get_workout(current_user, workout_id):
    """Get workout details with exercises"""
    try:
        db = get_db()
        
        # Find assignment
        assignment = db.calendar_assignments.find_one({'_id': ObjectId(workout_id)})
        
        if not assignment or str(assignment['user_id']) != current_user.id:
            return jsonify({
                'error': 'Workout not found',
                'code': 'NOT_FOUND'
            }), 404
        
        assignment_obj = CalendarAssignment(assignment)
        
        # Get exercises if it's a workout (not rest day)
        exercises = []
        if assignment_obj.exercise_group_id:
            group = db.exercise_groups.find_one({'_id': assignment_obj.exercise_group_id})
            if group:
                assignment_obj.group_name = group['name']
                exercise_ids = group.get('exercise_ids', [])
                for ex_id in exercise_ids:
                    ex = Exercise.find_by_id(db, str(ex_id))
                    if ex:
                        exercises.append(ex)
        
        return jsonify({
            'workout': workout_to_dict(assignment_obj, exercises)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch workout',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('', methods=['POST'])
@jwt_required
def create_workout(current_user):
    """Create new workout assignment"""
    try:
        data = request.get_json()
        
        if not data or not data.get('date'):
            return jsonify({
                'error': 'Date is required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        db = get_db()
        date_str = data['date']
        is_rest_day = data.get('is_rest_day', False)
        
        if is_rest_day:
            # Create rest day assignment
            assignment = CalendarAssignment.create(
                db, current_user.id, date_str,
                assignment_type='rest'
            )
        else:
            # Create workout assignment
            group_id = data.get('workout_group_id')
            if not group_id:
                return jsonify({
                    'error': 'workout_group_id is required for workout assignments',
                    'code': 'MISSING_FIELDS'
                }), 400
            
            assignment = CalendarAssignment.create(
                db, current_user.id, date_str,
                group_id=group_id,
                assignment_type='workout'
            )
        
        return jsonify({
            'workout': workout_to_dict(assignment)
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create workout',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<workout_id>', methods=['DELETE'])
@jwt_required
def delete_workout(current_user, workout_id):
    """Delete workout assignment"""
    try:
        db = get_db()
        
        # Verify ownership
        assignment = db.calendar_assignments.find_one({'_id': ObjectId(workout_id)})
        
        if not assignment or str(assignment['user_id']) != current_user.id:
            return jsonify({
                'error': 'Workout not found',
                'code': 'NOT_FOUND'
            }), 404
        
        CalendarAssignment.delete(db, workout_id)
        
        return jsonify({
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete workout',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/sync', methods=['GET'])
@jwt_required
def sync_workouts(current_user):
    """Get workouts changed since timestamp"""
    try:
        db = get_db()
        
        # Get since parameter
        since_str = request.args.get('since')
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            # Return all workouts from last 30 days
            since = datetime.utcnow().replace(day=1)
        
        # Get all assignments created/updated after since
        query = {
            'user_id': ObjectId(current_user.id),
            'created_at': {'$gte': since}
        }
        
        assignments = []
        for doc in db.calendar_assignments.find(query):
            assignment = CalendarAssignment(doc)
            assignments.append(workout_to_dict(assignment))
        
        return jsonify({
            'workouts': assignments,
            'deleted_ids': [],  # Implement soft delete tracking if needed
            'last_sync': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to sync workouts',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500
