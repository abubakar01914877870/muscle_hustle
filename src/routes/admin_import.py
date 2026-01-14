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
    
    # Extract name and description from translations (English = language 2)
    translations = exercise_info.get('translations', [])
    english_translation = None
    for t in translations:
        if t.get('language') == 2:  # English
            english_translation = t
            break
    if not english_translation and translations:
        english_translation = translations[0]
    
    if english_translation:
        name = english_translation.get('name', f"Exercise {exercise_id}")
        description = english_translation.get('description', '')
    else:
        name = f"Exercise {exercise_id}"
        description = ''
    
    # Get category (primary muscle group)
    category_data = exercise_info.get('category', {})
    muscle = category_data.get('name', 'Other') if isinstance(category_data, dict) else 'Other'
    
    # Get primary muscles from API 'muscles' array
    muscles_data = exercise_info.get('muscles', [])
    muscles_primary = []
    for m in muscles_data:
        # Prefer name_en (English name) if available, else use name
        muscle_name = m.get('name_en') or m.get('name', '')
        if muscle_name:
            muscles_primary.append(muscle_name)
    
    # Get secondary muscles
    muscles_secondary_data = exercise_info.get('muscles_secondary', [])
    secondary_muscles_list = []
    for m in muscles_secondary_data:
        muscle_name = m.get('name_en') or m.get('name', '')
        if muscle_name:
            secondary_muscles_list.append(muscle_name)
    
    # Get ALL equipment (not just first one)
    equipment_data = exercise_info.get('equipment', [])
    equipment_list = [e.get('name', 'Bodyweight') for e in equipment_data if e.get('name')]
    equipment = equipment_list[0] if equipment_list else 'Bodyweight'
    
    # Get images from Wger
    images_data = exercise_info.get('images', [])
    wger_images = []
    for img in images_data:
        img_url = img.get('image')
        if img_url:
            wger_images.append(img_url)
    
    # Get videos from Wger
    videos_data = exercise_info.get('videos', [])
    wger_videos = []
    for vid in videos_data:
        vid_url = vid.get('video')
        if vid_url:
            wger_videos.append(vid_url)
    
    # Get license and attribution info
    license_author = exercise_info.get('license_author', '')
    wger_uuid = exercise_info.get('uuid', '')
    
    # Redirect to add exercise form with pre-filled data as query parameters
    import json
    from urllib.parse import urlencode
    params = {
        'from_import': 'true',
        'wger_id': exercise_id,
        'wger_uuid': wger_uuid,
        'name': name,
        'muscle': muscle,
        'equipment': equipment,
        'muscles_primary': json.dumps(muscles_primary),
        'secondary_muscles': json.dumps(secondary_muscles_list),
        'equipment_list': json.dumps(equipment_list),
        'wger_images': json.dumps(wger_images),
        'wger_videos': json.dumps(wger_videos),
        'license_author': license_author,
        'description': description,
        'instructions': description,
        'difficulty': 'Intermediate',
        'type': 'Strength',
        'reps_sets': '3 sets x 8-12 reps',
        'wger_raw_response': json.dumps(exercise_info)  # Store full Wger API response
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
