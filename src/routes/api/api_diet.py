"""
Diet Plan API Endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from ...database import get_db
from ...models.diet_mongo import MealPlan
from ...models.planner import DietAssignment
from ...utils.jwt_utils import jwt_required

bp = Blueprint('api_diet', __name__, url_prefix='/api/v1/diet-plans')


def diet_plan_to_dict(plan):
    """Convert diet plan to API response"""
    total_calories = sum(meal.get('calories', 0) for meal in plan.meals)
    
    return {
        'id': plan.id,
        'name': plan.name,
        'meals': plan.meals,
        'total_calories': total_calories,
        'created_at': plan.created_at.isoformat() if plan.created_at else None
    }


@bp.route('/weekly', methods=['GET'])
@jwt_required
def get_weekly_plan(current_user):
    """Get 7-day diet plan for current user"""
    try:
        db = get_db()
        
        # Get user's meal plans
        plans = MealPlan.find_by_user(db, current_user.id)
        
        # Return up to 7 plans (one per day)
        weekly_plans = []
        for i, plan in enumerate(plans[:7]):
            weekly_plans.append({
                'day': i + 1,
                'plan': diet_plan_to_dict(plan)
            })
        
        return jsonify({
            'plans': weekly_plans
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch weekly diet plan',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('', methods=['GET'])
@jwt_required
def list_diet_plans(current_user):
    """List all diet plans"""
    try:
        db = get_db()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Get all plans for user
        all_plans = MealPlan.find_by_user(db, current_user.id)
        
        # Pagination
        total = len(all_plans)
        start = (page - 1) * limit
        end = start + limit
        paginated = all_plans[start:end]
        
        plans = [diet_plan_to_dict(p) for p in paginated]
        
        return jsonify({
            'plans': plans,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch diet plans',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/<plan_id>', methods=['GET'])
@jwt_required
def get_diet_plan(current_user, plan_id):
    """Get diet plan details"""
    try:
        db = get_db()
        plan = MealPlan.find_by_id(db, plan_id)
        
        if not plan or str(plan.user_id) != current_user.id:
            return jsonify({
                'error': 'Diet plan not found',
                'code': 'NOT_FOUND'
            }), 404
        
        return jsonify({
            'plan': diet_plan_to_dict(plan)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch diet plan',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500


@bp.route('/sync', methods=['GET'])
@jwt_required
def sync_diet_plans(current_user):
    """Get diet plans changed since timestamp"""
    try:
        db = get_db()
        
        # Get since parameter
        since_str = request.args.get('since')
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            # Return all plans
            since = datetime(2020, 1, 1)
        
        # Get plans created after since
        query = {
            'user_id': ObjectId(current_user.id),
            'created_at': {'$gte': since}
        }
        
        plans = []
        for doc in db.meal_plans.find(query):
            plan = MealPlan(doc)
            plans.append(diet_plan_to_dict(plan))
        
        return jsonify({
            'plans': plans,
            'deleted_ids': [],
            'last_sync': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to sync diet plans',
            'code': 'SERVER_ERROR',
            'details': str(e)
        }), 500
