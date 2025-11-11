from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from ..models.user import User, db

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>/profile')
@login_required
@admin_required
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/view_profile.html', user=user)

@admin.route('/users/<int:user_id>/profile/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Personal Information
        user.full_name = request.form.get('full_name')
        
        dob = request.form.get('date_of_birth')
        if dob:
            try:
                user.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        user.gender = request.form.get('gender')
        user.phone = request.form.get('phone')
        
        # Physical Measurements
        height = request.form.get('height')
        if height:
            try:
                user.height = float(height)
            except ValueError:
                pass
        
        weight = request.form.get('weight')
        if weight:
            try:
                user.weight = float(weight)
            except ValueError:
                pass
        
        target_weight = request.form.get('target_weight')
        if target_weight:
            try:
                user.target_weight = float(target_weight)
            except ValueError:
                pass
        
        # Fitness Information
        user.fitness_level = request.form.get('fitness_level')
        user.fitness_goal = request.form.get('fitness_goal')
        user.activity_level = request.form.get('activity_level')
        
        # Health Information
        user.medical_conditions = request.form.get('medical_conditions')
        user.dietary_restrictions = request.form.get('dietary_restrictions')
        
        # Preferences
        user.preferred_workout_time = request.form.get('preferred_workout_time')
        
        workout_freq = request.form.get('workout_frequency')
        if workout_freq:
            try:
                user.workout_frequency = int(workout_freq)
            except ValueError:
                pass
        
        db.session.commit()
        flash(f'Profile for {user.email} updated successfully!', 'success')
        return redirect(url_for('admin.view_user_profile', user_id=user_id))
    
    return render_template('admin/edit_profile.html', user=user)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if not email:
            flash('Email is required', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Email already in use by another user', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        user.email = email
        user.is_admin = is_admin
        
        # Only update password if provided
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash(f'User {user.email} updated successfully', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/edit_user.html', user=user)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.user_list'))
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'User {email} deleted successfully', 'success')
    return redirect(url_for('admin.user_list'))
