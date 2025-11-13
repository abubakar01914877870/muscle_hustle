from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from ..models.user import db
from ..models.progress import ProgressEntry

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

UPLOAD_FOLDER = 'src/static/uploads/progress'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                photo_filename = f"{current_user.id}_{timestamp}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, photo_filename))
        
        # Create entry
        entry = ProgressEntry(
            user_id=current_user.id,
            weight=weight,
            body_fat=float(body_fat) if body_fat else None,
            water_intake=float(water_intake) if water_intake else None,
            chest=float(chest) if chest else None,
            waist=float(waist) if waist else None,
            hips=float(hips) if hips else None,
            arms=float(arms) if arms else None,
            thighs=float(thighs) if thighs else None,
            notes=notes if notes else None,
            photo_filename=photo_filename
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Progress entry added successfully!', 'success')
        return redirect(url_for('progress.index'))
    
    except Exception as e:
        flash(f'Error adding entry: {str(e)}', 'error')
        return redirect(url_for('progress.index'))

@progress_bp.route('/api/entries')
@login_required
def get_entries():
    entries = ProgressEntry.query.filter_by(user_id=current_user.id)\
        .order_by(ProgressEntry.created_at.desc())\
        .all()
    
    return jsonify([entry.to_dict() for entry in entries])

@progress_bp.route('/api/chart-data')
@login_required
def get_chart_data():
    # Get entries from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    entries = ProgressEntry.query.filter(
        ProgressEntry.user_id == current_user.id,
        ProgressEntry.created_at >= thirty_days_ago
    ).order_by(ProgressEntry.created_at.asc()).all()
    
    data = {
        'labels': [entry.created_at.strftime('%b %d') for entry in entries],
        'weights': [entry.weight for entry in entries],
        'body_fats': [entry.body_fat for entry in entries if entry.body_fat]
    }
    
    return jsonify(data)

@progress_bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    
    # Check ownership
    if entry.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('progress.index'))
    
    # Delete photo file if exists
    if entry.photo_filename:
        photo_path = os.path.join(UPLOAD_FOLDER, entry.photo_filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Entry deleted successfully', 'success')
    return redirect(url_for('progress.index'))
