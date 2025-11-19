"""
Admin blog management routes with security features
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, ValidationError
from functools import wraps
from datetime import datetime
from ..database import get_db
from ..models.blog_mongo import BlogPost
from ..services.firebase_service import FirebaseService
from ..utils.security import validate_file_upload

admin_blog = Blueprint('admin_blog', __name__, url_prefix='/admin/blog')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_blog.route('/')
@login_required
@admin_required
def blog_dashboard():
    """Blog management dashboard showing all posts with status"""
    db = get_db()
    
    # Get all blog posts ordered by creation date (newest first)
    all_posts = BlogPost.find_all(db)
    
    return render_template('admin/blog/dashboard.html', posts=all_posts)

@admin_blog.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_blog_post():
    """Create new blog post form and handler with CSRF protection"""
    if request.method == 'POST':
        try:
            # CSRF validation
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Security token validation failed. Please try again.', 'error')
            return render_template('admin/blog/create.html')
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        content_type = request.form.get('content_type', 'html')
        status = request.form.get('status', 'draft')
        
        # Validation
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/blog/create.html')
        
        if not content:
            flash('Content is required', 'error')
            return render_template('admin/blog/create.html')    
    
        try:
            # Create the blog post (content will be sanitized in the model)
            db = get_db()
            blog_post = BlogPost.create(
                db=db,
                title=title,
                content=content,
                author_id=current_user.id,
                author_name=current_user.email,
                content_type=content_type,
                status=status
            )
            
            flash(f'Blog post "{title}" created successfully', 'success')
            return redirect(url_for('admin_blog.blog_dashboard'))
            
        except ValueError as e:
            flash(f'Error creating blog post: {str(e)}', 'error')
            return render_template('admin/blog/create.html')
        except Exception as e:
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('admin/blog/create.html')
    
    return render_template('admin/blog/create.html')

@admin_blog.route('/<post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_blog_post(post_id):
    """Edit blog post form and handler with CSRF protection"""
    db = get_db()
    post = BlogPost.find_by_id(db, post_id)
    
    if not post:
        flash('Blog post not found', 'error')
        return redirect(url_for('admin_blog.blog_dashboard'))
    
    if request.method == 'POST':
        try:
            # CSRF validation
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Security token validation failed. Please try again.', 'error')
            return render_template('admin/blog/edit.html', post=post)
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        content_type = request.form.get('content_type', 'html')
        status = request.form.get('status', 'draft')
        
        # Validation
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/blog/edit.html', post=post)
        
        if not content:
            flash('Content is required', 'error')
            return render_template('admin/blog/edit.html', post=post)
        
        try:
            # Update post fields (content will be sanitized in save method)
            post.title = title
            post.content = content
            post.content_type = content_type
            
            # Handle status change using model methods
            if status == 'published' and post.status != 'published':
                post.publish()
            elif status == 'draft' and post.status != 'draft':
                post.unpublish()
            else:
                post.status = status
            
            # Save the blog post
            success = post.save(db)
            
            if success:
                flash(f'Blog post "{title}" updated successfully', 'success')
                return redirect(url_for('admin_blog.blog_dashboard'))
            else:
                flash('Failed to update blog post. Please try again.', 'error')
                return render_template('admin/blog/edit.html', post=post)
                
        except Exception as e:
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('admin/blog/edit.html', post=post)
    
    return render_template('admin/blog/edit.html', post=post)

@admin_blog.route('/<post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_blog_post(post_id):
    """Delete blog post with image cleanup and CSRF protection"""
    try:
        # CSRF validation
        validate_csrf(request.form.get('csrf_token'))
    except ValidationError:
        flash('Security token validation failed. Please try again.', 'error')
        return redirect(url_for('admin_blog.blog_dashboard'))
    
    db = get_db()
    post = BlogPost.find_by_id(db, post_id)
    
    if not post:
        flash('Blog post not found', 'error')
        return redirect(url_for('admin_blog.blog_dashboard'))
    
    title = post.title
    
    try:
        # Clean up associated images from Firebase Storage
        firebase_service = FirebaseService()
        cleanup_errors = []
        
        for image in post.images:
            if 'firebase_path' in image:
                success, error = firebase_service.delete_image(image['firebase_path'])
                if not success and error:
                    cleanup_errors.append(f"Failed to delete image {image.get('filename', 'unknown')}: {error}")
        
        # Delete the blog post from database
        delete_success = BlogPost.delete(db, post_id)
        
        if delete_success:
            flash(f'Blog post "{title}" deleted successfully', 'success')
            
            # Show warnings for image cleanup failures (non-critical)
            if cleanup_errors:
                for error in cleanup_errors:
                    flash(f'Warning: {error}', 'warning')
        else:
            flash('Failed to delete blog post. Please try again.', 'error')
            
    except Exception as e:
        flash('An unexpected error occurred during deletion. Please try again.', 'error')
    
    return redirect(url_for('admin_blog.blog_dashboard'))

@admin_blog.route('/<post_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_post_status(post_id):
    """Toggle blog post status between draft and published with CSRF protection"""
    try:
        # CSRF validation
        validate_csrf(request.form.get('csrf_token'))
    except ValidationError:
        flash('Security token validation failed. Please try again.', 'error')
        return redirect(url_for('admin_blog.blog_dashboard'))
    
    db = get_db()
    post = BlogPost.find_by_id(db, post_id)
    
    if not post:
        flash('Blog post not found', 'error')
        return redirect(url_for('admin_blog.blog_dashboard'))
    
    try:
        # Toggle status using the model methods for consistency
        if post.status == 'draft':
            post.publish()
        else:
            post.unpublish()
        
        # Save the changes
        success = post.save(get_db())
        
        if success:
            flash(f'Blog post status changed to {post.status}', 'success')
        else:
            flash('Failed to update blog post status. Please try again.', 'error')
            
    except Exception as e:
        flash('An unexpected error occurred. Please try again.', 'error')
    
    return redirect(url_for('admin_blog.blog_dashboard'))

@admin_blog.route('/upload-image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    """Handle image upload via AJAX with enhanced security validation and error handling"""
    try:
        # CSRF validation for AJAX requests
        validate_csrf(request.headers.get('X-CSRFToken'))
    except ValidationError:
        return jsonify({
            'error': 'Security token validation failed. Please refresh the page and try again.',
            'error_type': 'csrf'
        }), 403
    
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image file was selected. Please choose an image to upload.',
            'error_type': 'no_file'
        }), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({
            'error': 'Please select a valid image file.',
            'error_type': 'empty_file'
        }), 400
    
    try:
        # Use base64 storage in MongoDB (consistent with rest of application)
        from ..utils.image_handler import resize_image, get_image_data_url
        
        # Validate file type
        from ..utils.security import validate_file_upload
        is_valid, validation_error = validate_file_upload(file)
        if not is_valid:
            return jsonify({
                'error': f'File validation failed: {validation_error}',
                'error_type': 'validation_failed'
            }), 400
        
        # Resize and encode image to base64
        file.seek(0)  # Reset file pointer
        result = resize_image(file, max_width=1200, max_height=1200)
        
        if not result:
            return jsonify({
                'error': 'Failed to process image. Please try a different file.',
                'error_type': 'processing_failed'
            }), 400
        
        # Create data URL for immediate display
        download_url = get_image_data_url(result['image_data'], result['content_type'])
        
        if not download_url:
            return jsonify({
                'error': 'Failed to generate image URL.',
                'error_type': 'url_generation_failed'
            }), 400
        
        # Return success with base64 data URL
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': result['filename'],
            'width': result.get('width'),
            'height': result.get('height'),
            'message': 'Image uploaded successfully!',
            'storage_type': 'base64'  # Indicate storage method
        })
    
    except Exception as e:
        # Log the error for debugging but don't expose internal details
        current_app.logger.error(f"Image upload error: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred during upload. Please try again.',
            'error_type': 'unexpected_error'
        }), 500

@admin_blog.route('/validate-youtube', methods=['POST'])
@login_required
@admin_required
def validate_youtube():
    """Validate YouTube URL via AJAX"""
    try:
        # CSRF validation for AJAX requests
        validate_csrf(request.headers.get('X-CSRFToken'))
    except ValidationError:
        return jsonify({
            'error': 'Security token validation failed',
            'error_type': 'csrf'
        }), 403
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'error': 'No URL provided',
            'error_type': 'no_url'
        }), 400
    
    url = data['url'].strip()
    if not url:
        return jsonify({
            'error': 'Please provide a YouTube video URL',
            'error_type': 'empty_url'
        }), 400
    
    try:
        from ..services.youtube_service import YouTubeService
        
        # Process the YouTube URL
        success, video_data, error = YouTubeService.process_youtube_url(url)
        
        if success and video_data:
            # Check video accessibility
            is_accessible, access_error = YouTubeService.validate_video_accessibility(video_data['video_id'])
            
            return jsonify({
                'success': True,
                'video_id': video_data['video_id'],
                'embed_code': video_data['embed_code'],
                'metadata': video_data['metadata'],
                'accessible': is_accessible,
                'access_warning': access_error if not is_accessible else None,
                'message': 'YouTube video validated successfully!'
            })
        else:
            error_type = 'invalid_url'
            if error and 'not a valid youtube' in error.lower():
                error_type = 'invalid_youtube_url'
            elif error and 'network' in error.lower():
                error_type = 'network_error'
            
            return jsonify({
                'error': error or 'Invalid YouTube URL',
                'error_type': error_type
            }), 400
    
    except Exception as e:
        current_app.logger.error(f"YouTube validation error: {str(e)}")
        return jsonify({
            'error': 'An error occurred while validating the YouTube URL',
            'error_type': 'unexpected_error'
        }), 500