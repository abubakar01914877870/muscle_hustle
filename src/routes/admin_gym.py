from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models.gym_mongo import Gym
from ..database import get_db
from .admin import admin_required

admin_gym = Blueprint('admin_gym', __name__, url_prefix='/admin/gyms')

@admin_gym.route('/')
@login_required
@admin_required
def list_gyms():
    db = get_db()
    gyms = Gym.find_all(db)
    return render_template('admin/gyms/list.html', gyms=gyms)

@admin_gym.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_gym():
    if request.method == 'POST':
        db = get_db()
        
        name = request.form.get('name')
        description = request.form.get('description')
        phone = request.form.get('phone')
        google_map_link = request.form.get('google_map_link')
        address = request.form.get('address')
        admin_note = request.form.get('admin_note')
        
        if not name or not phone or not google_map_link:
            flash('Name, Phone, and Google Map Link are required', 'error')
            return render_template('admin/gyms/form.html')
            
        # Handle image URLs
        images_text = request.form.get('images', '')
        # Split by newline or comma and strip whitespace
        images = [url.strip() for url in images_text.replace(',', '\n').split('\n') if url.strip()]
        
        gym = Gym(
            name=name,
            description=description,
            phone=phone,
            google_map_link=google_map_link,
            address=address,
            admin_note=admin_note,
            images=images
        )
        
        Gym.save(db, gym)
        flash('Gym added successfully', 'success')
        return redirect(url_for('admin_gym.list_gyms'))
        
    return render_template('admin/gyms/form.html')

@admin_gym.route('/<gym_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_gym(gym_id):
    db = get_db()
    gym = Gym.find_by_id(db, gym_id)
    
    if not gym:
        flash('Gym not found', 'error')
        return redirect(url_for('admin_gym.list_gyms'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        phone = request.form.get('phone')
        google_map_link = request.form.get('google_map_link')
        address = request.form.get('address')
        admin_note = request.form.get('admin_note')
        
        if not name or not phone or not google_map_link:
            flash('Name, Phone, and Google Map Link are required', 'error')
            return render_template('admin/gyms/form.html', gym=gym)
            
        # Handle image URLs
        images_text = request.form.get('images', '')
        images = [url.strip() for url in images_text.replace(',', '\n').split('\n') if url.strip()]
        
        gym.name = name
        gym.description = description
        gym.phone = phone
        gym.google_map_link = google_map_link
        gym.address = address
        gym.admin_note = admin_note
        gym.images = images
        
        Gym.save(db, gym)
        flash('Gym updated successfully', 'success')
        return redirect(url_for('admin_gym.list_gyms'))
        
    return render_template('admin/gyms/form.html', gym=gym)

@admin_gym.route('/<gym_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_gym(gym_id):
    db = get_db()
    Gym.delete(db, gym_id)
    flash('Gym deleted successfully', 'success')
    return redirect(url_for('admin_gym.list_gyms'))

@admin_gym.route('/migrate-slugs')
@login_required
@admin_required
def migrate_slugs():
    """Temporary route to migrate existing gyms to have slugs"""
    db = get_db()
    gyms = Gym.find_all(db)
    count = 0
    for gym in gyms:
        Gym.save(db, gym)  # save() now auto-generates slug if missing
        count += 1
    return f"Migrated {count} gyms successfully!"
