from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from ..models.user_mongo import User, slugify
from ..database import get_db
from .admin import admin_required

admin_trainer = Blueprint('admin_trainer', __name__, url_prefix='/admin/trainers')

def trainer_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.is_admin or current_user.is_trainer):
            flash('Access denied.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_trainer.route('/')
@login_required
@trainer_or_admin_required
def list_trainers():
    """List trainers for management"""
    db = get_db()
    
    # If not admin, redirect to their own view page
    if not current_user.is_admin:
        return redirect(url_for('trainer.view_profile', slug=current_user.slug))
        
    trainers = User.find_all_trainers(db, published_only=False)
    return render_template('admin/trainers/list.html', trainers=trainers)

@admin_trainer.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
@trainer_or_admin_required
def edit_trainer(slug):
    """Edit trainer profile"""
    db = get_db()
    trainer_user = User.find_by_slug(db, slug)
    
    if not trainer_user:
        flash('Trainer not found', 'error')
        return redirect(url_for('admin_trainer.list_trainers'))
        
    # Security check: Trainers can only edit themselves, Admins can edit anyone
    if not current_user.is_admin and str(current_user.id) != str(trainer_user.id):
        flash('Permission denied.', 'error')
        return redirect(url_for('admin_trainer.list_trainers'))
        
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        bio = request.form.get('bio', '').strip()
        tagline = request.form.get('tagline', '').strip()
        years_of_experience = request.form.get('years_of_experience', '').strip()
        hourly_rate = request.form.get('hourly_rate', '').strip()

        # Update full name if provided
        if full_name:
            trainer_user.full_name = full_name
            # We are NOT updating the slug automatically to prevent breaking existing links
            # If slug update is needed, we would do it here:
            # trainer_user.slug = slugify(full_name)
            
        # Get certifications (dynamic list)
        certifications = []
        cert_index = 0
        while True:
            cert = request.form.get(f'certification_{cert_index}', '').strip()
            if cert:
                certifications.append(cert)
                cert_index += 1
            else:
                break
        
        # Get specializations (checkboxes)
        specializations = request.form.getlist('specializations')
        
        # Get social links
        social_links = {
            'instagram': request.form.get('instagram', '').strip(),
            'facebook': request.form.get('facebook', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip()
        }
        
        # Get publish status
        is_published = request.form.get('is_published') == 'on'
        
        # Build trainer profile data
        trainer_profile = {
            'bio': bio if bio else None,
            'tagline': tagline if tagline else None,
            'certifications': certifications if certifications else [],
            'specializations': specializations if specializations else [],
            'social_links': social_links,
            'is_published': is_published
        }
        
        # Add optional fields
        if years_of_experience:
            try:
                trainer_profile['years_of_experience'] = int(years_of_experience)
            except ValueError:
                pass
        
        if hourly_rate:
            try:
                trainer_profile['hourly_rate'] = float(hourly_rate)
            except ValueError:
                pass
        
        # Update trainer profile
        trainer_user.save(db) # Save full_name update
        if trainer_user.update_trainer_profile(db, trainer_profile):
            flash('Trainer profile updated successfully!', 'success')
            if current_user.is_admin:
                return redirect(url_for('admin_trainer.list_trainers'))
            return redirect(url_for('admin_trainer.edit_trainer', slug=trainer_user.slug))
        else:
            flash('Error updating trainer profile', 'error')
    
    return render_template('admin/trainers/edit.html', trainer=trainer_user)
