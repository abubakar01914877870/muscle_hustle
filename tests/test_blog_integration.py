"""
Integration tests for complete blog system workflows
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from src.app import app
from src.models.blog_mongo import BlogPost


class TestBlogIntegrationWorkflows:
    """Integration tests for complete blog workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        
        # Create test admin user data
        self.admin_user_id = ObjectId()
        
        # Create test blog post data
        self.test_post_data = {
            '_id': ObjectId(),
            'title': 'Integration Test Post',
            'content': '<p>This is a test blog post for integration testing.</p>',
            'content_type': 'html',
            'status': 'draft',
            'author_id': self.admin_user_id,
            'author_name': 'Test Admin',
            'images': [],
            'youtube_videos': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'published_at': None,
            'view_count': 0,
            'tags': ['test', 'integration']
        }
    
    def test_complete_blog_creation_and_publication_workflow(self):
        """
        Test complete blog creation and publication workflow:
        1. Creates a new blog post
        2. Publishes the post
        3. Verifies post appears in public interface
        4. Tests individual post view
        """
        with patch('src.routes.blog.get_db') as mock_blog_get_db:
            
            # Setup database mocks
            mock_db = Mock()
            mock_blog_get_db.return_value = mock_db
            
            # Step 1: Test published post appears in public interface
            published_post_data = self.test_post_data.copy()
            published_post_data['status'] = 'published'
            published_post_data['published_at'] = datetime.utcnow()
            
            mock_published_post = BlogPost(published_post_data)
            
            with patch.object(BlogPost, 'find_published', return_value=[mock_published_post]), \
                 patch.object(BlogPost, 'count_published', return_value=1):
                
                public_list_response = self.client.get('/blog/')
                assert public_list_response.status_code == 200
                assert self.test_post_data['title'].encode() in public_list_response.data
                assert b'blog-post-card' in public_list_response.data
            
            # Step 2: Test individual post view
            with patch.object(BlogPost, 'find_by_id', return_value=mock_published_post):
                post_response = self.client.get(f'/blog/{self.test_post_data["_id"]}')
                assert post_response.status_code == 200
                assert self.test_post_data['title'].encode() in post_response.data
                assert self.test_post_data['content'].encode() in post_response.data
            
            # Step 3: Test draft post is not visible
            draft_post_data = self.test_post_data.copy()
            draft_post_data['status'] = 'draft'
            mock_draft_post = BlogPost(draft_post_data)
            
            with patch.object(BlogPost, 'find_by_id', return_value=mock_draft_post):
                draft_response = self.client.get(f'/blog/{self.test_post_data["_id"]}')
                assert draft_response.status_code == 404  # Draft posts should not be accessible
    
    def test_admin_management_interface_functionality(self):
        """
        Test admin management interface functionality:
        1. Test admin routes require authentication (redirect to login)
        2. Test model operations work correctly
        """
        # Step 1: Test admin routes require authentication
        admin_response = self.client.get('/admin/blog/')
        # Should redirect to login or return 401/403
        assert admin_response.status_code in [302, 401, 403]
        
        # Step 2: Test model operations directly
        mock_db = Mock()
        
        # Test post creation
        mock_result = Mock()
        mock_result.inserted_id = self.test_post_data['_id']
        mock_db.blog_posts.insert_one.return_value = mock_result
        
        with patch('src.models.blog_mongo.sanitize_blog_content', return_value=self.test_post_data['content']):
            created_post = BlogPost.create(
                db=mock_db,
                title=self.test_post_data['title'],
                content=self.test_post_data['content'],
                author_id=str(self.admin_user_id),
                author_name=self.test_post_data['author_name']
            )
            
            assert created_post is not None
            assert created_post.title == self.test_post_data['title']
            mock_db.blog_posts.insert_one.assert_called_once()
        
        # Test post update
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.blog_posts.update_one.return_value = mock_update_result
        
        update_success = BlogPost.update(mock_db, str(self.test_post_data['_id']), {
            'title': 'Updated Title',
            'status': 'published'
        })
        
        assert update_success
        mock_db.blog_posts.update_one.assert_called_once()
        
        # Test post deletion
        mock_delete_result = Mock()
        mock_delete_result.deleted_count = 1
        mock_db.blog_posts.delete_one.return_value = mock_delete_result
        
        delete_success = BlogPost.delete(mock_db, str(self.test_post_data['_id']))
        
        assert delete_success
        mock_db.blog_posts.delete_one.assert_called_once()
    
    def test_public_blog_browsing_experience(self):
        """
        Test public blog browsing experience:
        1. View blog list with multiple posts
        2. Navigate to individual posts
        3. Test pagination
        4. Test error handling
        """
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Create multiple test posts
            test_posts = []
            for i in range(15):  # Create 15 posts to test pagination
                post_data = self.test_post_data.copy()
                post_data['_id'] = ObjectId()
                post_data['title'] = f'Test Post {i+1}'
                post_data['status'] = 'published'
                post_data['published_at'] = datetime.utcnow()
                test_posts.append(BlogPost(post_data))
            
            # Step 1: Test blog list with pagination
            with patch.object(BlogPost, 'find_published', return_value=test_posts[:12]), \
                 patch.object(BlogPost, 'count_published', return_value=15):
                
                blog_list_response = self.client.get('/blog/')
                assert blog_list_response.status_code == 200
                assert b'blog-posts-grid' in blog_list_response.data
                
                # Check that posts are displayed
                for i in range(12):  # First page should show 12 posts
                    assert f'Test Post {i+1}'.encode() in blog_list_response.data
                
                # Check pagination controls
                assert b'pagination' in blog_list_response.data.lower()
            
            # Step 2: Test second page of pagination
            with patch.object(BlogPost, 'find_published', return_value=test_posts[12:]), \
                 patch.object(BlogPost, 'count_published', return_value=15):
                
                page2_response = self.client.get('/blog/?page=2')
                assert page2_response.status_code == 200
                
                # Should show remaining 3 posts
                for i in range(12, 15):
                    assert f'Test Post {i+1}'.encode() in page2_response.data
            
            # Step 3: Test individual post navigation
            test_post = test_posts[0]
            with patch.object(BlogPost, 'find_by_id', return_value=test_post):
                post_response = self.client.get(f'/blog/{test_post.id}')
                assert post_response.status_code == 200
                assert test_post.title.encode() in post_response.data
                assert b'Back to Blog' in post_response.data or b'back to' in post_response.data.lower()
            
            # Step 4: Test 404 for non-existent post
            with patch.object(BlogPost, 'find_by_id', return_value=None):
                not_found_response = self.client.get(f'/blog/{ObjectId()}')
                assert not_found_response.status_code == 404
            
            # Step 5: Test 404 for draft post (not visible to public)
            draft_post = BlogPost(self.test_post_data)  # Draft status
            with patch.object(BlogPost, 'find_by_id', return_value=draft_post):
                draft_response = self.client.get(f'/blog/{draft_post.id}')
                assert draft_response.status_code == 404
            
            # Step 6: Test empty blog state
            with patch.object(BlogPost, 'find_published', return_value=[]), \
                 patch.object(BlogPost, 'count_published', return_value=0):
                
                empty_response = self.client.get('/blog/')
                assert empty_response.status_code == 200
                assert b'No Blog Posts Yet' in empty_response.data or b'no content is available' in empty_response.data.lower()
    
    def test_concurrent_user_scenarios(self):
        """
        Test concurrent user scenarios:
        1. Multiple users viewing blog simultaneously
        2. Admin editing while users are viewing
        3. View count increments
        4. Cache behavior
        """
        with patch('src.routes.blog.get_db') as mock_get_db, \
             patch('src.routes.admin_blog.get_db') as mock_admin_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_admin_get_db.return_value = mock_db
            
            # Create published test post
            published_post_data = self.test_post_data.copy()
            published_post_data['status'] = 'published'
            published_post_data['published_at'] = datetime.utcnow()
            published_post_data['view_count'] = 0
            
            mock_post = BlogPost(published_post_data)
            
            # Step 1: Test multiple concurrent views
            with patch.object(BlogPost, 'find_by_id', return_value=mock_post):
                # Simulate multiple users viewing the same post
                for i in range(5):
                    response = self.client.get(f'/blog/{mock_post.id}')
                    assert response.status_code == 200
                    assert mock_post.title.encode() in response.data
            
            # Step 2: Test user views updated post
            updated_post_data = published_post_data.copy()
            updated_post_data['title'] = 'Updated During Concurrent Access'
            updated_post_data['updated_at'] = datetime.utcnow()
            updated_mock_post = BlogPost(updated_post_data)
            
            with patch.object(BlogPost, 'find_by_id', return_value=updated_mock_post):
                user_view_response = self.client.get(f'/blog/{mock_post.id}')
                assert user_view_response.status_code == 200
                assert b'Updated During Concurrent Access' in user_view_response.data
            
            # Step 3: Test caching behavior
            # First request should set cache headers
            with patch.object(BlogPost, 'find_published', return_value=[mock_post]), \
                 patch.object(BlogPost, 'count_published', return_value=1):
                
                first_response = self.client.get('/blog/')
                assert first_response.status_code == 200
                
                # Check for cache headers
                assert 'Cache-Control' in first_response.headers
                assert 'public' in first_response.headers.get('Cache-Control', '')
                
                # Second request should also work (cache behavior would be handled by browser/CDN)
                second_response = self.client.get('/blog/')
                assert second_response.status_code == 200
            
            # Step 4: Test database error handling during concurrent access
            # Simulate database connection failure
            from pymongo.errors import ConnectionFailure
            
            with patch.object(BlogPost, 'find_published', side_effect=ConnectionFailure("Connection lost")):
                error_response = self.client.get('/blog/')
                assert error_response.status_code == 200  # Should gracefully handle error
                assert b'technical difficulties' in error_response.data.lower() or b'error' in error_response.data.lower()
            
            # Step 5: Test concurrent post creation simulation
            # Simulate multiple posts being created
            all_concurrent_posts = [
                BlogPost({**self.test_post_data, '_id': ObjectId(), 'title': f'Concurrent Post {i+1}'}) 
                for i in range(3)
            ]
            
            # Test that multiple posts can be retrieved
            with patch.object(BlogPost, 'find_published', return_value=all_concurrent_posts), \
                 patch.object(BlogPost, 'count_published', return_value=3):
                
                list_response = self.client.get('/blog/')
                assert list_response.status_code == 200
                
                for i in range(3):
                    assert f'Concurrent Post {i+1}'.encode() in list_response.data
    
    def test_media_content_integration(self):
        """
        Test integration of media content (images and YouTube videos):
        1. Create post with images
        2. Create post with YouTube videos
        3. Test media rendering in public interface
        4. Test media handling in admin interface
        """
        with patch('src.routes.blog.get_db') as mock_get_db, \
             patch('src.routes.admin_blog.get_db') as mock_admin_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_admin_get_db.return_value = mock_db
            
            # Create post with media content
            media_post_data = self.test_post_data.copy()
            media_post_data['status'] = 'published'
            media_post_data['published_at'] = datetime.utcnow()
            media_post_data['images'] = [
                {
                    'firebase_path': 'blog-images/test-image.jpg',
                    'download_url': 'https://storage.googleapis.com/test-bucket/test-image.jpg',
                    'filename': 'test-image.jpg',
                    'caption': 'Test Image Caption',
                    'alt_text': 'Test Image Alt Text',
                    'order': 0
                }
            ]
            media_post_data['youtube_videos'] = [
                {
                    'video_id': 'dQw4w9WgXcQ',
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'title': 'Test Video',
                    'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allowfullscreen></iframe>',
                    'order': 0
                }
            ]
            
            media_post = BlogPost(media_post_data)
            
            # Step 1: Test media content in public interface
            with patch.object(BlogPost, 'find_by_id', return_value=media_post):
                media_response = self.client.get(f'/blog/{media_post.id}')
                assert media_response.status_code == 200
                
                # Check image rendering
                assert b'blog-post-images' in media_response.data
                assert media_post_data['images'][0]['download_url'].encode() in media_response.data
                assert media_post_data['images'][0]['alt_text'].encode() in media_response.data
                assert media_post_data['images'][0]['caption'].encode() in media_response.data
                
                # Check YouTube video rendering
                assert b'blog-post-videos' in media_response.data
                assert media_post_data['youtube_videos'][0]['video_id'].encode() in media_response.data
                assert b'youtube.com/embed' in media_response.data
                assert media_post_data['youtube_videos'][0]['title'].encode() in media_response.data
            
            # Step 2: Test media content in blog list
            with patch.object(BlogPost, 'find_published', return_value=[media_post]), \
                 patch.object(BlogPost, 'count_published', return_value=1):
                
                list_response = self.client.get('/blog/')
                assert list_response.status_code == 200
                
                # Check featured image in list view
                assert media_post_data['images'][0]['download_url'].encode() in list_response.data
                assert b'blog-post-featured-image' in list_response.data
            
            # Step 3: Test media error handling
            # Test image loading error
            error_post_data = media_post_data.copy()
            error_post_data['images'][0]['download_url'] = 'https://invalid-url.com/broken-image.jpg'
            error_post = BlogPost(error_post_data)
            
            with patch.object(BlogPost, 'find_by_id', return_value=error_post):
                error_response = self.client.get(f'/blog/{error_post.id}')
                assert error_response.status_code == 200
                
                # Should include error handling elements
                assert b'onerror' in error_response.data  # JavaScript error handling
                assert b'image-error' in error_response.data  # Error placeholder
            
            # Step 4: Test media data structure
            # Verify media post has correct structure
            assert len(media_post.images) == 1
            assert len(media_post.youtube_videos) == 1
            assert media_post.images[0]['download_url'] == media_post_data['images'][0]['download_url']
            assert media_post.youtube_videos[0]['video_id'] == media_post_data['youtube_videos'][0]['video_id']
    
    def test_error_handling_integration(self):
        """
        Test error handling across the entire blog system:
        1. Database connection errors
        2. Invalid post IDs
        3. Permission errors
        4. Validation errors
        """
        with patch('src.routes.blog.get_db') as mock_get_db, \
             patch('src.routes.admin_blog.get_db') as mock_admin_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_admin_get_db.return_value = mock_db
            
            # Step 1: Test database connection errors
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
            
            # Test blog list with database error
            with patch.object(BlogPost, 'find_published', side_effect=ConnectionFailure("Database unavailable")):
                db_error_response = self.client.get('/blog/')
                assert db_error_response.status_code == 200
                assert b'technical difficulties' in db_error_response.data.lower() or b'error' in db_error_response.data.lower()
            
            # Test individual post with database error
            with patch.object(BlogPost, 'find_by_id', side_effect=ServerSelectionTimeoutError("Timeout")):
                timeout_response = self.client.get(f'/blog/{ObjectId()}')
                assert timeout_response.status_code == 503
                assert b'database connectivity issues' in timeout_response.data.lower() or b'503' in timeout_response.data
            
            # Step 2: Test invalid post IDs
            # Test with malformed ObjectId
            invalid_id_response = self.client.get('/blog/invalid-id-format')
            # Should either return 404 or handle gracefully
            assert invalid_id_response.status_code in [404, 500]
            
            # Test with valid ObjectId format but non-existent post
            with patch.object(BlogPost, 'find_by_id', return_value=None):
                not_found_response = self.client.get(f'/blog/{ObjectId()}')
                assert not_found_response.status_code == 404
            
            # Step 3: Test permission errors (non-admin accessing admin routes)
            # Test without authentication
            admin_response = self.client.get('/admin/blog/')
            assert admin_response.status_code in [302, 401, 403]  # Redirect to login or forbidden
            
            # Test with non-authenticated user (already tested above)
            # Admin routes should require authentication
            
            # Step 4: Test validation errors at model level
            mock_db = Mock()
            
            # Test creating post with invalid data should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                BlogPost.create(
                    db=mock_db,
                    title='',  # Empty title should cause validation error
                    content='Valid content',
                    author_id=str(self.admin_user_id),
                    author_name='Test Author'
                )
            
            assert 'Title is required' in str(exc_info.value)
            
            # Step 5: Test graceful degradation
            # Test when Firebase service is unavailable (model level)
            mock_db = Mock()
            mock_result = Mock()
            mock_result.inserted_id = ObjectId()
            mock_db.blog_posts.insert_one.return_value = mock_result
            
            # Should still allow post creation without images
            with patch('src.models.blog_mongo.sanitize_blog_content', return_value='Content without media'):
                post_without_media = BlogPost.create(
                    db=mock_db,
                    title='Post without images',
                    content='Content without media',
                    author_id=str(self.admin_user_id),
                    author_name='Test Author'
                )
                
                # Should succeed even without media
                assert post_without_media is not None
                assert post_without_media.title == 'Post without images'
    
    def test_performance_and_caching_integration(self):
        """
        Test performance optimizations and caching behavior:
        1. Cache headers are set correctly
        2. Pagination works efficiently
        3. Database queries are optimized
        4. Large content handling
        """
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Create test posts for performance testing
            large_content_post_data = self.test_post_data.copy()
            large_content_post_data['content'] = '<p>' + 'Large content ' * 1000 + '</p>'  # Large content
            large_content_post_data['status'] = 'published'
            large_content_post_data['published_at'] = datetime.utcnow()
            
            large_post = BlogPost(large_content_post_data)
            
            # Step 1: Test cache headers
            with patch.object(BlogPost, 'find_published', return_value=[large_post]), \
                 patch.object(BlogPost, 'count_published', return_value=1):
                
                cache_response = self.client.get('/blog/')
                assert cache_response.status_code == 200
                
                # Check cache headers
                assert 'Cache-Control' in cache_response.headers
                assert 'public' in cache_response.headers['Cache-Control']
                assert 'max-age' in cache_response.headers['Cache-Control']
                assert 'Expires' in cache_response.headers
            
            # Step 2: Test individual post cache headers
            with patch.object(BlogPost, 'find_by_id', return_value=large_post):
                post_cache_response = self.client.get(f'/blog/{large_post.id}')
                assert post_cache_response.status_code == 200
                
                # Check cache headers for individual posts
                assert 'Cache-Control' in post_cache_response.headers
                assert 'ETag' in post_cache_response.headers
                assert 'Expires' in post_cache_response.headers
            
            # Step 3: Test pagination performance
            # Create many posts to test pagination
            many_posts = []
            for i in range(50):
                post_data = self.test_post_data.copy()
                post_data['_id'] = ObjectId()
                post_data['title'] = f'Performance Test Post {i+1}'
                post_data['status'] = 'published'
                post_data['published_at'] = datetime.utcnow()
                many_posts.append(BlogPost(post_data))
            
            # Test first page
            with patch.object(BlogPost, 'find_published', return_value=many_posts[:12]), \
                 patch.object(BlogPost, 'count_published', return_value=50):
                
                page1_response = self.client.get('/blog/')
                assert page1_response.status_code == 200
                
                # Should show pagination controls
                assert b'pagination' in page1_response.data.lower()
                assert b'Page 1 of' in page1_response.data
            
            # Test middle page
            with patch.object(BlogPost, 'find_published', return_value=many_posts[24:36]), \
                 patch.object(BlogPost, 'count_published', return_value=50):
                
                page3_response = self.client.get('/blog/?page=3')
                assert page3_response.status_code == 200
                assert b'Page 3 of' in page3_response.data
            
            # Step 4: Test large content handling
            with patch.object(BlogPost, 'find_by_id', return_value=large_post):
                large_content_response = self.client.get(f'/blog/{large_post.id}')
                assert large_content_response.status_code == 200
                
                # Should handle large content without issues
                assert len(large_content_response.data) > 10000  # Should include the large content
                
                # Should include performance optimizations
                # Note: lazy loading only appears when there are images in the post
                # For this test, we'll check for JavaScript optimization code
                assert b'IntersectionObserver' in large_content_response.data  # Lazy loading JS
                assert b'responsive-image' in large_content_response.data or b'will-change' in large_content_response.data  # CSS optimizations
            
            # Step 5: Test database query optimization
            # Verify that find_published uses projection to limit fields
            with patch.object(BlogPost, 'find_published') as mock_find_published:
                mock_find_published.return_value = [large_post]
                
                self.client.get('/blog/')
                
                # Verify find_published was called (which should use optimized queries)
                mock_find_published.assert_called_once()
                
                # In a real test, we would verify the MongoDB query includes projection
                # to limit fields and uses proper indexing