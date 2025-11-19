"""
Blog Post Model for MongoDB
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from flask import g
from ..utils.security import sanitize_blog_content


class BlogPost:
    """Blog Post model for MongoDB operations"""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize blog post from MongoDB document"""
        self._id = data.get('_id')
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.content_type = data.get('content_type', 'html')  # 'html' or 'plain'
        self.status = data.get('status', 'draft')  # 'draft' or 'published'
        self.author_id = data.get('author_id')
        self.author_name = data.get('author_name', '')
        self.images = data.get('images', [])  # Array of image objects
        self.youtube_videos = data.get('youtube_videos', [])  # Array of video objects
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.published_at = data.get('published_at')
        self.view_count = data.get('view_count', 0)
        self.tags = data.get('tags', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blog post to dictionary for MongoDB storage"""
        return {
            '_id': self._id,
            'title': self.title,
            'content': self.content,
            'content_type': self.content_type,
            'status': self.status,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'images': self.images,
            'youtube_videos': self.youtube_videos,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'published_at': self.published_at,
            'view_count': self.view_count,
            'tags': self.tags
        }
    
    @property
    def id(self) -> str:
        """Get string representation of ObjectId"""
        return str(self._id) if self._id else None
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate blog post data
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate required fields
        if not self.title or not self.title.strip():
            errors.append("Title is required and cannot be empty")
        
        if not self.content or not self.content.strip():
            errors.append("Content is required and cannot be empty")
        
        if not self.author_name or not self.author_name.strip():
            errors.append("Author name is required and cannot be empty")
        
        if not self.author_id:
            errors.append("Author ID is required")
        
        # Validate field lengths
        if len(self.title.strip()) > 200:
            errors.append("Title cannot exceed 200 characters")
        
        if len(self.content) > 100000:  # 100KB limit
            errors.append("Content cannot exceed 100,000 characters")
        
        if len(self.author_name.strip()) > 100:
            errors.append("Author name cannot exceed 100 characters")
        
        # Validate content type
        if self.content_type not in ['html', 'plain']:
            errors.append("Content type must be 'html' or 'plain'")
        
        # Validate status
        if self.status not in ['draft', 'published']:
            errors.append("Status must be 'draft' or 'published'")
        
        # Validate tags
        if len(self.tags) > 20:
            errors.append("Cannot have more than 20 tags")
        
        for tag in self.tags:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                errors.append("All tags must be non-empty strings")
                break
            if len(tag) > 50:
                errors.append("Tags cannot exceed 50 characters")
                break
        
        # Validate images
        for i, image in enumerate(self.images):
            if not isinstance(image, dict):
                errors.append(f"Image {i+1} must be a dictionary")
                continue
            
            required_image_fields = ['firebase_path', 'download_url', 'filename']
            for field in required_image_fields:
                if field not in image or not image[field]:
                    errors.append(f"Image {i+1} missing required field: {field}")
        
        # Validate YouTube videos
        for i, video in enumerate(self.youtube_videos):
            if not isinstance(video, dict):
                errors.append(f"Video {i+1} must be a dictionary")
                continue
            
            required_video_fields = ['video_id', 'url', 'embed_code']
            for field in required_video_fields:
                if field not in video or not video[field]:
                    errors.append(f"Video {i+1} missing required field: {field}")
        
        return len(errors) == 0, errors
    
    @property
    def is_published(self) -> bool:
        """Check if blog post is published"""
        return self.status == 'published'
    
    @property
    def is_draft(self) -> bool:
        """Check if blog post is draft"""
        return self.status == 'draft'
    
    def publish(self):
        """Mark blog post as published"""
        self.status = 'published'
        if not self.published_at:
            self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def unpublish(self):
        """Mark blog post as draft"""
        self.status = 'draft'
        self.updated_at = datetime.utcnow()
    
    def add_image(self, image_data: Dict[str, Any]):
        """Add image to blog post"""
        image_obj = {
            'firebase_path': image_data.get('firebase_path'),
            'download_url': image_data.get('download_url'),
            'filename': image_data.get('filename'),
            'caption': image_data.get('caption', ''),
            'alt_text': image_data.get('alt_text', ''),
            'order': len(self.images)
        }
        self.images.append(image_obj)
    
    def add_youtube_video(self, video_data: Dict[str, Any]):
        """Add YouTube video to blog post"""
        video_obj = {
            'video_id': video_data.get('video_id'),
            'url': video_data.get('url'),
            'title': video_data.get('title', ''),
            'embed_code': video_data.get('embed_code'),
            'order': len(self.youtube_videos)
        }
        self.youtube_videos.append(video_obj)
    
    @staticmethod
    def create(db, title: str, content: str, author_id: str, author_name: str, 
               content_type: str = 'html', status: str = 'draft') -> 'BlogPost':
        """Create new blog post with validation and content sanitization"""
        now = datetime.utcnow()
        
        # Sanitize content for security
        sanitized_content = sanitize_blog_content(content, content_type)
        
        # Create temporary blog post for validation
        temp_data = {
            'title': title,
            'content': sanitized_content,
            'content_type': content_type,
            'status': status,
            'author_id': ObjectId(author_id),
            'author_name': author_name,
            'images': [],
            'youtube_videos': [],
            'created_at': now,
            'updated_at': now,
            'published_at': now if status == 'published' else None,
            'view_count': 0,
            'tags': []
        }
        
        temp_post = BlogPost(temp_data)
        is_valid, errors = temp_post.validate()
        
        if not is_valid:
            raise ValueError(f"Blog post validation failed: {'; '.join(errors)}")
        
        result = db.blog_posts.insert_one(temp_data)
        temp_data['_id'] = result.inserted_id
        
        return BlogPost(temp_data)
    
    @staticmethod
    def find_by_id(db, post_id: str) -> Optional['BlogPost']:
        """Find blog post by ID"""
        try:
            post_data = db.blog_posts.find_one({'_id': ObjectId(post_id)})
            return BlogPost(post_data) if post_data else None
        except Exception:
            return None
    
    @staticmethod
    def find_all(db, status: Optional[str] = None, limit: Optional[int] = None, skip: int = 0) -> List['BlogPost']:
        """Find all blog posts, optionally filtered by status with pagination support"""
        query = {}
        if status:
            query['status'] = status
        
        cursor = db.blog_posts.find(query).sort('created_at', -1)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        return [BlogPost(post_data) for post_data in cursor]
    
    @staticmethod
    def find_published(db, limit: Optional[int] = None, skip: int = 0) -> List['BlogPost']:
        """Find published blog posts ordered by publication date with pagination support"""
        cursor = db.blog_posts.find(
            {'status': 'published'},
            # Project only necessary fields for list view to reduce memory usage
            {
                'title': 1,
                'content': 1,
                'content_type': 1,
                'author_name': 1,
                'published_at': 1,
                'created_at': 1,
                'view_count': 1,
                'tags': 1,
                'images': {'$slice': 1}  # Only get first image for list view
            }
        ).sort('published_at', -1)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        return [BlogPost(post_data) for post_data in cursor]
    
    @staticmethod
    def find_by_author(db, author_id: str) -> List['BlogPost']:
        """Find blog posts by author"""
        cursor = db.blog_posts.find({'author_id': ObjectId(author_id)}).sort('created_at', -1)
        return [BlogPost(post_data) for post_data in cursor]
    
    @staticmethod
    def count_published(db) -> int:
        """Count total number of published blog posts"""
        return db.blog_posts.count_documents({'status': 'published'})
    
    @staticmethod
    def count_all(db, status: Optional[str] = None) -> int:
        """Count total number of blog posts, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status
        return db.blog_posts.count_documents(query)
    
    @staticmethod
    def find_popular(db, limit: int = 5) -> List['BlogPost']:
        """Find most popular published blog posts by view count"""
        cursor = db.blog_posts.find(
            {'status': 'published', 'view_count': {'$gt': 0}},
            {
                'title': 1,
                'author_name': 1,
                'published_at': 1,
                'view_count': 1,
                'images': {'$slice': 1}
            }
        ).sort('view_count', -1).limit(limit)
        
        return [BlogPost(post_data) for post_data in cursor]
    
    @staticmethod
    def find_by_tag(db, tag: str, limit: Optional[int] = None) -> List['BlogPost']:
        """Find published blog posts by tag"""
        cursor = db.blog_posts.find(
            {'status': 'published', 'tags': tag},
            {
                'title': 1,
                'content': 1,
                'content_type': 1,
                'author_name': 1,
                'published_at': 1,
                'view_count': 1,
                'tags': 1,
                'images': {'$slice': 1}
            }
        ).sort('published_at', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return [BlogPost(post_data) for post_data in cursor]
    
    def save(self, db) -> bool:
        """Save blog post to database with validation and content sanitization"""
        try:
            # Sanitize content before saving
            self.content = sanitize_blog_content(self.content, self.content_type)
            
            # Validate before saving
            is_valid, errors = self.validate()
            if not is_valid:
                print(f"Blog post validation failed: {'; '.join(errors)}")
                return False
            
            self.updated_at = datetime.utcnow()
            
            if self._id:
                # Update existing post
                result = db.blog_posts.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # Create new post
                self.created_at = datetime.utcnow()
                result = db.blog_posts.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
                
        except Exception as e:
            print(f"Error saving blog post: {str(e)}")
            return False
    
    def delete(self, db) -> bool:
        """Delete blog post from database"""
        try:
            if self._id:
                result = db.blog_posts.delete_one({'_id': self._id})
                return result.deleted_count > 0
            return False
        except Exception as e:
            print(f"Error deleting blog post: {str(e)}")
            return False
    
    def increment_view_count(self, db):
        """Increment view count for blog post"""
        try:
            if self._id:
                db.blog_posts.update_one(
                    {'_id': self._id},
                    {'$inc': {'view_count': 1}}
                )
                self.view_count += 1
        except Exception as e:
            print(f"Error incrementing view count: {str(e)}")
    
    @staticmethod
    def update(db, post_id: str, update_data: dict) -> bool:
        """Update blog post with given data"""
        try:
            # Ensure updated_at is set
            update_data['updated_at'] = datetime.utcnow()
            
            result = db.blog_posts.update_one(
                {'_id': ObjectId(post_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating blog post: {str(e)}")
            return False
    
    @staticmethod
    def delete(db, post_id: str) -> bool:
        """Delete blog post by ID"""
        try:
            result = db.blog_posts.delete_one({'_id': ObjectId(post_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting blog post: {str(e)}")
            return False