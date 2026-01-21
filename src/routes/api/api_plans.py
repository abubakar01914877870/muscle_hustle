"""
Workout Plans API Endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from ...database import get_db
from ...models.planner import ExerciseGroup
from ...models.exercise_mongo import Exercise
from ...utils.jwt_utils import jwt_required

bp = Blueprint('api_plans', __name__, url_prefix='/api/v1/plans')

@bp.route('', methods=['GET'])
@jwt_required
def list_plans(current_user):
    """List user's workout plans"""
    try:
        db = get_db()
        groups = ExerciseGroup.find_by_user(db, current_user.id)
        return jsonify({
            'plans': [g.to_dict() for g in groups]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<plan_id>', methods=['GET'])
@jwt_required
def get_plan(current_user, plan_id):
    """Get workout plan details with exercises"""
    try:
        db = get_db()
        group = ExerciseGroup.find_by_id(db, plan_id)
        
        if not group or str(group.user_id) != current_user.id:
            return jsonify({'error': 'Plan not found'}), 404
            
        # Hydrate exercises
        result = group.to_dict()
        exercises = []
        for eid in group.exercise_ids:
            ex = Exercise.find_by_id(db, str(eid))
            if ex:
                exercises.append({
                    'id': ex.id,
                    'name': ex.name,
                    'description': ex.description or ex.instructions,
                    'category': ex.type,
                    'muscle_group': ex.muscle,
                    'equipment': ex.equipment,
                    'instructions': ex.instructions,
                    'image_url': ex.get_image_url(),
                    'video_url': ex.video_url,
                    'is_custom': ex.created_by != 'wger_import',
                    'created_at': ex.created_at.isoformat() if ex.created_at else None
                })
        result['exercises'] = exercises
        
        return jsonify({'plan': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
@jwt_required
def create_plan(current_user):
    """Create new workout plan"""
    try:
        data = request.get_json()
        db = get_db()
        
        group = ExerciseGroup.create(
            db,
            current_user.id,
            name=data['name'],
            exercise_ids=data['exercise_ids'],
            description=data.get('description'),
            duration=data.get('duration', 0),
            difficulty=data.get('difficulty', 'Intermediate')
        )
        
        return jsonify({'plan': group.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<plan_id>', methods=['PUT'])
@jwt_required
def update_plan(current_user, plan_id):
    """Update workout plan"""
    try:
        data = request.get_json()
        db = get_db()
        group = ExerciseGroup.find_by_id(db, plan_id)
        
        if not group or str(group.user_id) != current_user.id:
            return jsonify({'error': 'Plan not found'}), 404
            
        group.update(
            db,
            name=data.get('name'),
            exercise_ids=data.get('exercise_ids'),
            description=data.get('description'),
            duration=data.get('duration'),
            difficulty=data.get('difficulty')
        )
        
        return jsonify({'plan': group.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<plan_id>', methods=['DELETE'])
@jwt_required
def delete_plan(current_user, plan_id):
    """Delete workout plan"""
    try:
        db = get_db()
        group = ExerciseGroup.find_by_id(db, plan_id)
        
        if not group or str(group.user_id) != current_user.id:
            return jsonify({'error': 'Plan not found'}), 404
            
        group.delete(db)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
