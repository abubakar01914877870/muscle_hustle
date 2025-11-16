from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..models.exercise_mongo import Exercise
from ..database import get_db
from ..utils.image_handler import resize_image
import re

exercises_bp = Blueprint('exercises', __name__, url_prefix='/exercises')

@exercises_bp.route('/')
def index():
    """Display all exercises with filters"""
    db = get_db()
    
    # Get filter parameters
    muscle_filters = request.args.getlist('muscle')
    equipment_filters = request.args.getlist('equipment')
    search_query = request.args.get('search', '')
    
    filters = {}
    if muscle_filters:
        filters['muscle'] = muscle_filters
    if equipment_filters:
        filters['equipment'] = equipment_filters
    
    exercises = Exercise.find_all(db, filters=filters, search=search_query)
    
    return render_template('exercises/index.html', 
                         exercises=exercises,
                         active_filters={'muscle': muscle_filters, 'equipment': equipment_filters},
                         search_query=search_query)


@exercises_bp.route('/<exercise_id>')
def detail(exercise_id):
    """Display exercise details"""
    db = get_db()
    exercise = Exercise.find_by_id(db, exercise_id)
    
    if not exercise:
        flash('Exercise not found', 'error')
        return redirect(url_for('exercises.index'))
    
    return render_template('exercises/detail.html', exercise=exercise)

@exercises_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new exercise (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('exercises.index'))
    
    if request.method == 'POST':
        try:
            # Collect secondary muscles
            secondary_muscles = request.form.getlist('secondary_muscles')
            
            # Get media type selection
            media_type = request.form.get('media_type', 'image')
            
            # Handle image upload
            image_data = None
            image_type = None
            if media_type == 'image' and 'exercise_image' in request.files:
                file = request.files['exercise_image']
                if file and file.filename:
                    image_result = resize_image(file, max_width=800, max_height=800)
                    if image_result:
                        image_data = image_result['image_data']
                        image_type = image_result['content_type']
            
            # Handle YouTube URL
            youtube_url = None
            if media_type == 'video':
                video_url = request.form.get('video_url', '').strip()
                print(f"DEBUG: Video URL from form: '{video_url}'")
                if video_url:
                    # Extract YouTube video ID
                    youtube_id = extract_youtube_id(video_url)
                    print(f"DEBUG: Extracted YouTube ID: '{youtube_id}'")
                    if youtube_id:
                        youtube_url = f"https://www.youtube.com/embed/{youtube_id}"
                        print(f"DEBUG: Final embed URL: '{youtube_url}'")
                    else:
                        flash('Invalid YouTube URL. Please use a valid YouTube link.', 'error')
                        return render_template('exercises/add.html')
                else:
                    flash('Please provide a YouTube URL when selecting video option.', 'error')
                    return render_template('exercises/add.html')
            
            # Create exercise
            db = get_db()
            print(f"DEBUG: Creating exercise with media_type='{media_type}', has_image='{image_data is not None}', video_url='{youtube_url}'")
            
            Exercise.create(
                db=db,
                name=request.form.get('name'),
                muscle=request.form.get('muscle'),
                secondary_muscles=secondary_muscles,
                equipment=request.form.get('equipment'),
                difficulty=request.form.get('difficulty'),
                type=request.form.get('type'),
                description=request.form.get('description'),
                instructions=request.form.get('instructions'),
                reps_sets=request.form.get('reps_sets'),
                tips=request.form.get('tips'),
                common_mistakes=request.form.get('common_mistakes'),
                media_type=media_type,
                image_data=image_data,
                image_type=image_type,
                video_url=youtube_url,
                created_by=str(current_user.id)
            )
            
            flash('Exercise added successfully!', 'success')
            return redirect(url_for('exercises.index'))
        
        except Exception as e:
            flash(f'Error adding exercise: {str(e)}', 'error')
    
    return render_template('exercises/add.html')

def extract_youtube_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


@exercises_bp.route('/<exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(exercise_id):
    """Edit exercise (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('exercises.index'))
    
    db = get_db()
    exercise = Exercise.find_by_id(db, exercise_id)
    
    if not exercise:
        flash('Exercise not found', 'error')
        return redirect(url_for('exercises.index'))
    
    if request.method == 'POST':
        try:
            # Get media type selection
            media_type = request.form.get('media_type', 'image')
            
            update_data = {
                'name': request.form.get('name'),
                'muscle': request.form.get('muscle'),
                'secondary_muscles': request.form.getlist('secondary_muscles'),
                'equipment': request.form.get('equipment'),
                'difficulty': request.form.get('difficulty'),
                'type': request.form.get('type'),
                'description': request.form.get('description'),
                'instructions': request.form.get('instructions'),
                'reps_sets': request.form.get('reps_sets'),
                'tips': request.form.get('tips'),
                'common_mistakes': request.form.get('common_mistakes'),
                'media_type': media_type
            }
            
            # Handle image upload
            if media_type == 'image' and 'exercise_image' in request.files:
                file = request.files['exercise_image']
                if file and file.filename:
                    image_result = resize_image(file, max_width=800, max_height=800)
                    if image_result:
                        update_data['image_data'] = image_result['image_data']
                        update_data['image_type'] = image_result['content_type']
                        update_data['video_url'] = None
            
            # Handle YouTube URL
            elif media_type == 'video':
                video_url = request.form.get('video_url', '').strip()
                print(f"DEBUG EDIT: Video URL from form: '{video_url}'")
                if video_url:
                    youtube_id = extract_youtube_id(video_url)
                    print(f"DEBUG EDIT: Extracted YouTube ID: '{youtube_id}'")
                    if youtube_id:
                        update_data['video_url'] = f"https://www.youtube.com/embed/{youtube_id}"
                        update_data['image_data'] = None
                        update_data['image_type'] = None
                        print(f"DEBUG EDIT: Final embed URL: '{update_data['video_url']}'")
                    else:
                        flash('Invalid YouTube URL. Please use a valid YouTube link.', 'error')
                        return render_template('exercises/edit.html', exercise=exercise)
                else:
                    # Keep existing video URL if no new one provided
                    if exercise.video_url:
                        update_data['video_url'] = exercise.video_url
                        update_data['image_filename'] = None
            
            Exercise.update(db, exercise_id, update_data)
            flash('Exercise updated successfully!', 'success')
            return redirect(url_for('exercises.detail', exercise_id=exercise_id))
        
        except Exception as e:
            flash(f'Error updating exercise: {str(e)}', 'error')
    
    return render_template('exercises/edit.html', exercise=exercise)

@exercises_bp.route('/<exercise_id>/delete', methods=['POST'])
@login_required
def delete(exercise_id):
    """Delete exercise (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('exercises.index'))
    
    db = get_db()
    exercise = Exercise.find_by_id(db, exercise_id)
    
    if not exercise:
        flash('Exercise not found', 'error')
        return redirect(url_for('exercises.index'))
    
    # Images are stored in DB, no file deletion needed
    Exercise.delete(db, exercise_id)
    flash('Exercise deleted successfully!', 'success')
    return redirect(url_for('exercises.index'))
