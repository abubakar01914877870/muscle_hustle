"""
Blog routes for public blog interface with comprehensive error handling and performance optimizations
"""
from flask import Blueprint, render_template, abort, request, flash, current_app, make_response
from flask_login import current_user
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, timedelta
from ..database import get_db
from ..models.blog_mongo import BlogPost

blog = Blueprint('blog', __name__, url_prefix='/blog')

@blog.route('/')
def blog_list():
    """Display list of published blog posts with pagination and caching"""
    try:
        db = get_db()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Show 12 posts per page for better grid layout
        skip = (page - 1) * per_page
        
        # Get published posts with pagination
        published_posts = BlogPost.find_published(db, limit=per_page, skip=skip)
        total_posts = BlogPost.count_published(db)
        
        # Calculate pagination info
        total_pages = (total_posts + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        response = make_response(render_template('blog/list.html', 
                                               posts=published_posts,
                                               page=page,
                                               total_pages=total_pages,
                                               has_prev=has_prev,
                                               has_next=has_next,
                                               total_posts=total_posts))
        
        # Add caching headers for public content (5 minutes)
        response.headers['Cache-Control'] = 'public, max-age=300'
        response.headers['Expires'] = (datetime.utcnow() + timedelta(minutes=5)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return response
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        current_app.logger.error(f"Database connection error in blog_list: {str(e)}")
        # Return template with error state
        return render_template('blog/list.html', 
                             posts=[], 
                             db_error=True,
                             error_message="We're experiencing technical difficulties. Please try again later.")
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in blog_list: {str(e)}")
        # Return template with generic error state
        return render_template('blog/list.html', 
                             posts=[], 
                             db_error=True,
                             error_message="Something went wrong while loading the blog posts. Please refresh the page.")

@blog.route('/<post_id>')
def blog_post(post_id):
    """Display individual blog post with caching and error handling"""
    try:
        db = get_db()
        
        # Find the blog post
        post = BlogPost.find_by_id(db, post_id)
        
        # Check if post exists and is published
        if not post or not post.is_published:
            abort(404)
        
        # Increment view count (with error handling)
        try:
            post.increment_view_count(db)
        except Exception as e:
            # Log the error but don't fail the request
            current_app.logger.warning(f"Failed to increment view count for post {post_id}: {str(e)}")
        
        response = make_response(render_template('blog/post.html', post=post))
        
        # Add caching headers for individual posts (10 minutes)
        response.headers['Cache-Control'] = 'public, max-age=600'
        response.headers['Expires'] = (datetime.utcnow() + timedelta(minutes=10)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add ETag for better caching
        etag = f'"{post.id}-{post.updated_at.timestamp() if post.updated_at else post.created_at.timestamp()}"'
        response.headers['ETag'] = etag
        
        return response
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        current_app.logger.error(f"Database connection error in blog_post: {str(e)}")
        # Return 503 Service Unavailable for database issues
        return render_template('errors/503.html', 
                             error_message="We're experiencing database connectivity issues. Please try again in a few moments."), 503
    
    except Exception as e:
        # Don't catch abort exceptions - let them propagate
        if hasattr(e, 'code') and e.code == 404:
            raise
        current_app.logger.error(f"Unexpected error in blog_post for post_id {post_id}: {str(e)}")
        # Return 500 Internal Server Error for other issues
        return render_template('errors/500.html', 
                             error_message="An unexpected error occurred while loading this blog post."), 500