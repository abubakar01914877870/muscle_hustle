from flask import Blueprint, jsonify, request, current_app
from ...database import get_db
from ...models.planner import CalendarAssignment, DietAssignment
from ...utils.jwt_utils import jwt_required

api_planner = Blueprint('api_planner', __name__)

@api_planner.route('/assignments', methods=['GET'])
@jwt_required
def get_assignments(current_user):
    """Get workout and diet assignments for a date range"""
    try:
        db = get_db()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': 'start_date and end_date are required'}), 400
            
        workout_assignments = CalendarAssignment.find_by_user_and_date_range(
            db, current_user.id, start_date, end_date
        )
        
        diet_assignments = DietAssignment.find_by_user_and_date_range(
            db, current_user.id, start_date, end_date
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'workouts': [a.date_str for a in workout_assignments], # Simplified for now
                'details': {
                    'workouts': [
                        {
                            'id': str(a._id),
                            'date': a.date_str,
                            'group_id': str(a.exercise_group_id) if a.exercise_group_id else None,
                            'name': a.group_name,
                            'type': a.assignment_type
                        } for a in workout_assignments
                    ],
                    'diet': [
                        {
                            'id': str(a._id),
                            'date': a.date_str,
                            'plan_id': str(a.meal_plan_id),
                            'name': a.plan_name
                        } for a in diet_assignments
                    ]
                }
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_planner.get_assignments: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
