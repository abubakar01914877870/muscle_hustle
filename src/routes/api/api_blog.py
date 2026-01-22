from flask import Blueprint, jsonify, request, current_app
from ...database import get_db
from ...models.blog_mongo import BlogPost

api_blog = Blueprint('api_blog', __name__)

@api_blog.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all published blog posts
    ---
    tags:
      - Blog
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Items per page
    responses:
      200:
        description: List of blog posts
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                posts:
                  type: array
                  items:
                    $ref: '#/definitions/BlogPost'
                total:
                  type: integer
                page:
                  type: integer
                per_page:
                  type: integer
                total_pages:
                  type: integer
      500:
        description: Internal Server Error
    """
    try:
        db = get_db()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        skip = (page - 1) * per_page
        
        posts = BlogPost.find_published(db, limit=per_page, skip=skip)
        total = BlogPost.count_published(db)
        
        return jsonify({
            'status': 'success',
            'data': {
                'posts': [post.to_dict() for post in posts],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_blog.get_posts: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_blog.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get a single blog post by ID
    ---
    tags:
      - Blog
    parameters:
      - name: post_id
        in: path
        type: string
        required: true
        description: ID of the blog post
    responses:
      200:
        description: Blog post details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              $ref: '#/definitions/BlogPost'
      404:
        description: Post not found
    """
    try:
        db = get_db()
        post = BlogPost.find_by_id(db, post_id)
        
        if not post or not post.is_published:
            return jsonify({'status': 'error', 'message': 'Post not found'}), 404
            
        # Increment view count
        post.increment_view_count(db)
        
        return jsonify({
            'status': 'success',
            'data': post.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_blog.get_post: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
