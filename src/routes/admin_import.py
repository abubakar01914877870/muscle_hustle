"""
Admin Import Routes
Allows admins to browse Wger exercises and import them into MongoDB
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from src.database import get_db
from src.models.exercise_mongo import Exercise
from src.services.wger_service import WgerService

admin_import_bp = Blueprint('admin_import', __name__, url_prefix='/admin')

@admin_import_bp.route('/import-exercises')
@login_required
def browse():
    """Browse Wger exercises for import (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('exercises.index'))
    
    db = get_db()
    
    # Get pagination and filter parameters
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    muscle_filter = request.args.get('muscle', '')
    
    limit = 20
    offset = (page - 1) * limit
    
    # Fetch exercises from Wger API
    if search_query:
        # Search is handled differently - API returns IDs
        results_list = WgerService.search_exercises(search_query)
        total_count = len(results_list)
        # Apply pagination to search results manually since API might return all matches
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        results_page = results_list[start_idx:end_idx]
        wger_results = results_page
    else:
        # Standard browse
        wger_data = WgerService.get_exercises(limit=limit, offset=offset)
        wger_results = wger_data.get('results', [])
        total_count = wger_data.get('count', 788)
    
    exercises = []
    for ex_data in wger_results:
        # Get detailed info
        exercise_info = WgerService.get_exercise_info(ex_data['id'])
        if exercise_info:
            # Extract name from translations
            translations = exercise_info.get('translations', [])
            if translations:
                name = translations[0].get('name', f"Exercise {ex_data['id']}")
            else:
                name = f"Exercise {ex_data['id']}"
            
            # Skip manual search filter as we now use API search
            # if search_query and search_query.lower() not in name.lower():
            #    continue
            
            # Get category
            category_data = exercise_info.get('category', {})
            muscle = category_data.get('name', 'Other') if isinstance(category_data, dict) else 'Other'
            
            # Get equipment
            equipment_data = exercise_info.get('equipment', [])
            equipment = equipment_data[0].get('name', 'Bodyweight') if equipment_data else 'Bodyweight'
            
            # Check if already imported (by name, case-insensitive)
            from src.models.exercise_mongo import Exercise
            is_imported = Exercise.find_by_name(db, name) is not None
            
            exercises.append({
                'id': ex_data['id'],
                'name': name,
                'muscle': muscle,
                'equipment': equipment,
                'is_imported': is_imported
            })
    
    # Calculate pagination
    # total_count set above depending on search/browse mode
    total_pages = (total_count + limit - 1) // limit
    
    return render_template('admin/import_exercises.html',
                         exercises=exercises,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         search_query=search_query)


@admin_import_bp.route('/prepare-import/<int:exercise_id>')
@login_required
def prepare_import(exercise_id):
    """Prepare exercise data for import (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('exercises.index'))
    
    # Fetch exercise data from Wger
    exercise_info = WgerService.get_exercise_info(exercise_id)
    
    if not exercise_info:
        flash('Exercise not found in Wger API', 'error')
        return redirect(url_for('admin_import.browse'))
    
    # Extract name from translations
    translations = exercise_info.get('translations', [])
    if translations:
        name = translations[0].get('name', f"Exercise {exercise_id}")
        description = translations[0].get('description', '')
    else:
        name = f"Exercise {exercise_id}"
        description = ''
    
    # Get category
    category_data = exercise_info.get('category', {})
    muscle = category_data.get('name', 'Other') if isinstance(category_data, dict) else 'Other'
    
    # Get equipment
    equipment_data = exercise_info.get('equipment', [])
    equipment = equipment_data[0].get('name', 'Bodyweight') if equipment_data else 'Bodyweight'
    
    # Get secondary muscles
    muscles_secondary = exercise_info.get('muscles_secondary', [])
    secondary_muscles_list = [m.get('name') for m in muscles_secondary] if muscles_secondary else []
    
    # Redirect to add exercise form with pre-filled data as query parameters
    from urllib.parse import urlencode
    params = {
        'from_import': 'true',
        'wger_id': exercise_id,
        'name': name,
        'muscle': muscle,
        'equipment': equipment,
        'secondary_muscles': secondary_muscles_list,
        'description': description,
        'instructions': description,
        'difficulty': 'Intermediate',
        'type': 'Strength',
        'reps_sets': '3 sets x 8-12 reps'
    }
    
    return redirect(url_for('exercises.add') + '?' + urlencode(params))


@admin_import_bp.route('/import-preview/<int:exercise_id>')
@login_required
def preview_exercise(exercise_id):
    """Preview exercise details (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get detailed info from Wger
    exercise_info = WgerService.get_exercise_info(exercise_id)
    
    if not exercise_info:
        return jsonify({'error': 'Exercise not found'}), 404
    
    # Extract name from translations
    translations = exercise_info.get('translations', [])
    if translations:
        name = translations[0].get('name', f"Exercise {exercise_id}")
        description = translations[0].get('description', '')
    else:
        name = f"Exercise {exercise_id}"
        description = ''
    
    # Get category
    category_data = exercise_info.get('category', {})
    muscle = category_data.get('name', 'Other') if isinstance(category_data, dict) else 'Other'
    
    # Get equipment
    equipment_data = exercise_info.get('equipment', [])
    equipment = [e.get('name') for e in equipment_data] if equipment_data else ['Bodyweight']
    
    return jsonify({
        'id': exercise_id,
        'name': name,
        'muscle': muscle,
        'equipment': equipment,
        'description': description
    })
