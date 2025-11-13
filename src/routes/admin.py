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
