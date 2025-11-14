from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from ..models.user_mongo import User
from ..database import get_db

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
    db = get_db()
    users = User.find_all(db)
    return render_template('admin/users.html', users=users)

@admin.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    db = get_db()
    user = User.find_by_id(db, user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.user_list'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if not email:
            flash('Email is required', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Check if email is already taken by another user
        existing_user = User.find_by_email(db, email)
        if existing_user and str(existing_user.id) != str(user_id):
            flash('Email already in use by another user', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update user
        update_data = {
            'email': email,
            'is_admin': is_admin
        }
        
        # Only update password if provided
        if password:
            user.set_password(password)
            update_data['password_hash'] = user.password_hash
        
        User.update(db, user_id, update_data)
        flash(f'User {user.email} updated successfully', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/edit_user.html', user=user)

@admin.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    db = get_db()
    user = User.find_by_id(db, user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.user_list'))
    
    # Prevent deleting yourself
    if str(user.id) == str(current_user.id):
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.user_list'))
    
    email = user.email
    User.delete(db, user_id)
    flash(f'User {email} deleted successfully', 'success')
    return redirect(url_for('admin.user_list'))
