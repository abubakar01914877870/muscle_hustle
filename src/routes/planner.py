from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from src.database import get_db
from src.models.planner import ExerciseGroup, CalendarAssignment, WorkoutLog
from src.models.exercise_mongo import Exercise
from datetime import datetime, timedelta

planner_bp = Blueprint('planner', __name__, url_prefix='/planner')

@planner_bp.route('/')
@login_required
def dashboard():
    """Main Planner Dashboard"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('planner/dashboard.html', today_date=today_date)

@planner_bp.route('/groups')
@login_required
def groups_list():
    """List Exercise Groups"""
    db = get_db()
    groups = ExerciseGroup.find_by_user(db, current_user.id)
    return render_template('planner/groups.html', groups=groups)

@planner_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """Create a new Exercise Group"""
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        exercise_ids = request.form.getlist('exercise_ids')
        
        try:
            ExerciseGroup.create(db, current_user.id, name, exercise_ids)
            flash('Exercise Group created successfully!', 'success')
            return redirect(url_for('planner.groups_list'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while creating the group', 'error')
            print(f"Error creating group: {str(e)}")
            
    # GET: Show form with all exercises from MongoDB
    all_exercises = Exercise.find_all(db)
    return render_template('planner/group_form.html', exercises=all_exercises)

@planner_bp.route('/groups/<group_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    """Edit an existing Exercise Group"""
    db = get_db()
    group = ExerciseGroup.find_by_id(db, group_id)
    
    if not group or str(group.user_id) != current_user.id:
        flash('Group not found or unauthorized', 'error')
        return redirect(url_for('planner.groups_list'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        # Dependent on how the multi-select is implemented. 
        # For now assuming checkboxes with name 'exercise_ids'
        exercise_ids = request.form.getlist('exercise_ids')
        
        try:
            group.update(db, name=name, exercise_ids=exercise_ids)
            flash('Group updated successfully!', 'success')
            return redirect(url_for('planner.groups_list'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while updating the group', 'error')
            print(f"Error updating group: {str(e)}")

    # GET: Show form with all exercises from MongoDB
    all_exercises = Exercise.find_all(db)
    return render_template('planner/group_form.html', group=group, exercises=all_exercises)

@planner_bp.route('/groups/<group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    db = get_db()
    group = ExerciseGroup.find_by_id(db, group_id)
    if group and str(group.user_id) == current_user.id:
        group.delete(db)
        flash('Group deleted', 'success')
    else:
        flash('Error deleting group', 'error')
    return redirect(url_for('planner.groups_list'))

# --- Calendar Routes ---

@planner_bp.route('/calendar')
@login_required
def calendar_view():
    """Weekly Calendar View"""
    db = get_db()
    groups = ExerciseGroup.find_by_user(db, current_user.id)
    return render_template('planner/calendar.html', groups=groups)

@planner_bp.route('/api/assignments', methods=['GET', 'POST'])
@login_required
def api_assignments():
    """API to get or create assignments"""
    db = get_db()
    
    if request.method == 'POST':
        data = request.json
        date_str = data.get('date')
        group_id = data.get('group_id')
        repeat_option = data.get('repeat', 'none') # none, weekly_4, weekly_12, weekly_52
        
        if not date_str or not group_id:
            return jsonify({'error': 'Missing data'}), 400
            
        try:
            start_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Logic for repeats
        dates_to_assign = [start_date]
        if repeat_option == 'weekly_4':
            for i in range(1, 4):
                dates_to_assign.append(start_date + timedelta(weeks=i))
        elif repeat_option == 'weekly_12':
            for i in range(1, 12):
                dates_to_assign.append(start_date + timedelta(weeks=i))
        elif repeat_option == 'weekly_52': # "Unlimited" / 1 Year
             for i in range(1, 52):
                dates_to_assign.append(start_date + timedelta(weeks=i))
        
        created_count = 0
        for d in dates_to_assign:
            CalendarAssignment.create(db, current_user.id, d, group_id)
            created_count += 1
            
        return jsonify({'message': f'Created {created_count} assignments', 'dates': [d.strftime('%Y-%m-%d') for d in dates_to_assign]})

    # GET
    start = request.args.get('start')
    end = request.args.get('end')
    assignments = CalendarAssignment.find_by_user_and_date_range(db, current_user.id, start, end)
    
    return jsonify([{
        'id': a.id,
        'title': a.group_name,
        'start': a.date_str,
        'group_id': str(a.exercise_group_id)
    } for a in assignments])

# --- Tracker Routes ---

@planner_bp.route('/tracker')
@login_required
def tracker_view():
    """Daily Tracker View"""
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    db = get_db()
    
    # 1. Get assignments for this day
    assignments = CalendarAssignment.find_by_user_and_date(db, current_user.id, date_str)
    
    # 2. For each assignment, get the group details (exercises)
    # We might have multiple groups assigned to one day.
    
    daily_plan = []
    
    # Also get completion status
    completed_ids = WorkoutLog.get_completed_exercise_ids(db, current_user.id, date_str)
    completed_ids_str = [str(i) for i in completed_ids]

    for asm in assignments:
        group = ExerciseGroup.find_by_id(db, asm.exercise_group_id)
        if group:
            # Fetch full exercise details for the group
            exercises = []
            if group.exercise_ids:
                # Fetch exercises from MongoDB
                for eid in group.exercise_ids:
                    ex = Exercise.find_by_id(db, str(eid))
                    if ex:
                        exercises.append({
                            'id': str(ex._id),
                            'name': ex.name,
                            'reps_sets': ex.reps_sets if hasattr(ex, 'reps_sets') else '3 sets x 8-12 reps',
                            'instructions': ex.instructions if hasattr(ex, 'instructions') else '',
                            'tips': ex.tips if hasattr(ex, 'tips') else '',
                            'is_completed': str(ex._id) in completed_ids_str
                        })
            
            daily_plan.append({
                'group_name': group.name,
                'exercises': exercises
            })
            
    return render_template('planner/tracker.html', date=date_str, daily_plan=daily_plan)

@planner_bp.route('/api/log', methods=['POST'])
@login_required
def toggle_log():
    """Toggle completion status"""
    data = request.json
    date_str = data.get('date')
    exercise_id = data.get('exercise_id')
    completed = data.get('completed') # boolean
    
    db = get_db()
    if completed:
        WorkoutLog.mark_completed(db, current_user.id, date_str, exercise_id)
    else:
        WorkoutLog.mark_incomplete(db, current_user.id, date_str, exercise_id)
        
    return jsonify({'success': True})
