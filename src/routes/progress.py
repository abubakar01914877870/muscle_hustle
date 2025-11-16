from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..models.progress_mongo import ProgressEntry
from ..database import get_db
from ..utils.image_handler import resize_image

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

@progress_bp.route('/')
@login_required
def index():
    return render_template('progress/index.html')

@progress_bp.route('/add', methods=['POST'])
@login_required
def add_entry():
    try:
        weight = float(request.form.get('weight'))
        body_fat = request.form.get('body_fat')
        water_intake = request.form.get('water_intake')
        chest = request.form.get('chest')
        waist = request.form.get('waist')
        hips = request.form.get('hips')
        arms = request.form.get('arms')
        thighs = request.form.get('thighs')
        notes = request.form.get('notes', '').strip()
        
        # Handle photo upload
        photo_data = None
        photo_type = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                image_result = resize_image(file, max_width=800, max_height=800)
                if image_result:
                    photo_data = image_result['image_data']
                    photo_type = image_result['content_type']
        
        # Create entry
        db = get_db()
        ProgressEntry.create(
            db=db,
            user_id=str(current_user.id),
            weight=weight,
            body_fat=float(body_fat) if body_fat else None,
            water_intake=float(water_intake) if water_intake else None,
            chest=float(chest) if chest else None,
            waist=float(waist) if waist else None,
            hips=float(hips) if hips else None,
            arms=float(arms) if arms else None,
            thighs=float(thighs) if thighs else None,
            notes=notes if notes else None,
            photo_data=photo_data,
            photo_type=photo_type
        )
        
        flash('Progress entry added successfully!', 'success')
        return redirect(url_for('progress.index'))
    
    except Exception as e:
        flash(f'Error adding entry: {str(e)}', 'error')
        return redirect(url_for('progress.index'))

@progress_bp.route('/api/entries')
@login_required
def get_entries():
    db = get_db()
    entries = ProgressEntry.find_by_user(db, str(current_user.id))
    
    return jsonify([entry.to_dict() for entry in entries])

@progress_bp.route('/api/chart-data')
@login_required
def get_chart_data():
    # Get entries from last 30 days
    db = get_db()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    entries = ProgressEntry.find_by_user_since(db, str(current_user.id), thirty_days_ago)
    
    data = {
        'labels': [entry.created_at.strftime('%b %d') for entry in entries],
        'weights': [entry.weight for entry in entries],
        'body_fats': [entry.body_fat for entry in entries if entry.body_fat]
    }
    
    return jsonify(data)

@progress_bp.route('/delete/<entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    db = get_db()
    entry = ProgressEntry.find_by_id(db, entry_id)
    
    if not entry:
        flash('Entry not found', 'error')
        return redirect(url_for('progress.index'))
    
    # Check ownership
    if str(entry.user_id) != str(current_user.id):
        flash('Unauthorized access', 'error')
        return redirect(url_for('progress.index'))
    
    # Photos are stored in DB, no file deletion needed
    ProgressEntry.delete(db, entry_id)
    
    flash('Entry deleted successfully', 'success')
    return redirect(url_for('progress.index'))
