from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from ..models.user_mongo import User
from ..database import get_db

profile = Blueprint('profile', __name__, url_prefix='/profile')

UPLOAD_FOLDER = 'src/static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile.route('/')
@login_required
def view_profile():
    return render_template('profile/view.html', user=current_user)

@profile.route('/upload-picture', methods=['POST'])
@login_required
def upload_picture():
    if 'profile_picture' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('profile.view_profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('profile.view_profile'))
    
    if file and allowed_file(file.filename):
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            old_path = os.path.join(UPLOAD_FOLDER, current_user.profile_picture)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{timestamp}_{filename}"
        
        # Save file
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        
        # Update user profile
        db = get_db()
        User.update(db, current_user.id, {'profile_picture': unique_filename})
        current_user.profile_picture = unique_filename
        
        flash('Profile picture updated successfully!', 'success')
    else:
        flash('Invalid file type. Please upload an image file (PNG, JPG, JPEG, GIF, WEBP)', 'error')
    
    return redirect(url_for('profile.view_profile'))

@profile.route('/remove-picture', methods=['POST'])
@login_required
def remove_picture():
    if current_user.profile_picture:
        # Delete file
        file_path = os.path.join(UPLOAD_FOLDER, current_user.profile_picture)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Update database
        db = get_db()
        User.update(db, current_user.id, {'profile_picture': None})
        current_user.profile_picture = None
        
        flash('Profile picture removed successfully!', 'success')
    
    return redirect(url_for('profile.view_profile'))

@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Build update data dictionary
        update_data = {}
        
        # Personal Information
        full_name = request.form.get('full_name')
        if full_name:
            update_data['full_name'] = full_name
            current_user.full_name = full_name
        
        dob = request.form.get('date_of_birth')
        if dob:
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d')
                update_data['date_of_birth'] = dob_date
                current_user.date_of_birth = dob_date
            except ValueError:
                pass
        
        gender = request.form.get('gender')
        if gender:
            update_data['gender'] = gender
            current_user.gender = gender
        
        phone = request.form.get('phone')
        if phone:
            update_data['phone'] = phone
            current_user.phone = phone
        
        # Physical Measurements
        height = request.form.get('height')
        if height:
            try:
                height_val = float(height)
                update_data['height'] = height_val
                current_user.height = height_val
            except ValueError:
                pass
        
        weight = request.form.get('weight')
        if weight:
            try:
                weight_val = float(weight)
                update_data['weight'] = weight_val
                current_user.weight = weight_val
            except ValueError:
                pass
        
        target_weight = request.form.get('target_weight')
        if target_weight:
            try:
                target_val = float(target_weight)
                update_data['target_weight'] = target_val
                current_user.target_weight = target_val
            except ValueError:
                pass
        
        # Fitness Information
        fitness_level = request.form.get('fitness_level')
        if fitness_level:
            update_data['fitness_level'] = fitness_level
            current_user.fitness_level = fitness_level
        
        fitness_goal = request.form.get('fitness_goal')
        if fitness_goal:
            update_data['fitness_goal'] = fitness_goal
            current_user.fitness_goal = fitness_goal
        
        activity_level = request.form.get('activity_level')
        if activity_level:
            update_data['activity_level'] = activity_level
            current_user.activity_level = activity_level
        
        # Health Information
        medical_conditions = request.form.get('medical_conditions')
        if medical_conditions:
            update_data['medical_conditions'] = medical_conditions
            current_user.medical_conditions = medical_conditions
        
        dietary_restrictions = request.form.get('dietary_restrictions')
        if dietary_restrictions:
            update_data['dietary_restrictions'] = dietary_restrictions
            current_user.dietary_restrictions = dietary_restrictions
        
        # Preferences
        preferred_workout_time = request.form.get('preferred_workout_time')
        if preferred_workout_time:
            update_data['preferred_workout_time'] = preferred_workout_time
            current_user.preferred_workout_time = preferred_workout_time
        
        workout_freq = request.form.get('workout_frequency')
        if workout_freq:
            try:
                freq_val = int(workout_freq)
                update_data['workout_frequency'] = freq_val
                current_user.workout_frequency = freq_val
            except ValueError:
                pass
        
        # Update database
        db = get_db()
        User.update(db, current_user.id, update_data)
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/edit.html', user=current_user)

@profile.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('profile/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('profile/change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('profile/change_password.html')
        
        current_user.set_password(new_password)
        db = get_db()
        User.update(db, current_user.id, {'password_hash': current_user.password_hash})
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/change_password.html')
