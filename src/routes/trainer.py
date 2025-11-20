from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from ..models.user_mongo import User
from ..database import get_db

trainer = Blueprint('trainer', __name__, url_prefix='/trainer')

def trainer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_trainer:
            flash('You need trainer privileges to access this page', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@trainer.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_profile():
    """Edit trainer profile"""
    db = get_db()
    
    if request.method == 'POST':
        # Get form data
        bio = request.form.get('bio', '').strip()
        tagline = request.form.get('tagline', '').strip()
        years_of_experience = request.form.get('years_of_experience', '').strip()
        hourly_rate = request.form.get('hourly_rate', '').strip()
        
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
        if current_user.update_trainer_profile(db, trainer_profile):
            flash('Trainer profile updated successfully!', 'success')
            return redirect(url_for('trainer.edit_profile'))
        else:
            flash('Error updating trainer profile', 'error')
    
    return render_template('trainer/edit.html', user=current_user)

@trainer.route('/<trainer_id>')
def view_profile(trainer_id):
    """View public trainer profile"""
    db = get_db()
    trainer_user = User.find_by_id(db, trainer_id)
    
    if not trainer_user or not trainer_user.is_trainer:
        flash('Trainer not found', 'error')
        return redirect(url_for('trainer.list_trainers'))
    
    # Check if profile is published (unless viewing own profile)
    if current_user.is_authenticated and str(current_user.id) == str(trainer_id):
        # Allow trainers to view their own unpublished profile
        pass
    elif not trainer_user.is_trainer_profile_published():
        flash('This trainer profile is not available', 'error')
        return redirect(url_for('trainer.list_trainers'))
    
    return render_template('trainer/view.html', trainer=trainer_user)

@trainer.route('/trainers')
def list_trainers():
    """List all published trainers"""
    db = get_db()
    trainers = User.find_all_trainers(db, published_only=True)
    return render_template('trainer/list.html', trainers=trainers)
