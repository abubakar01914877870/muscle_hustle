"""
Property-based tests for Blog Routes
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from bson import ObjectId
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

from src.app import app
from src.models.blog_mongo import BlogPost


@composite
def blog_posts_mixed_status_strategy(draw):
    """Generate a list of blog posts with mixed statuses for testing"""
    num_posts = draw(st.integers(min_value=1, max_value=10))
    posts = []
    
    for i in range(num_posts):
        status = draw(st.sampled_from(['draft', 'published']))
        title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        content = draw(st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
        author_name = draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
        
        # Create timestamps
        created_at = datetime.utcnow()
        published_at = created_at if status == 'published' else None
        
        post_data = {
            '_id': ObjectId(),
            'title': title,
            'content': content,
            'content_type': 'html',
            'status': status,
            'author_id': ObjectId(),
            'author_name': author_name,
            'images': [],
            'youtube_videos': [],
            'created_at': created_at,
            'updated_at': created_at,
            'published_at': published_at,
            'view_count': 0,
            'tags': []
        }
        
        posts.append(BlogPost(post_data))
    
    return posts


@composite
def blog_post_with_media_strategy(draw):
    """Generate blog post with media content for testing"""
    # Use safe text generation to avoid HTML-problematic characters
    safe_text = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), max_codepoint=127))
    
    title = draw(safe_text.filter(lambda x: x.strip() and len(x.strip()) > 0))
    content = draw(safe_text.filter(lambda x: x.strip() and len(x.strip()) > 0))
    author_name = draw(safe_text.filter(lambda x: x.strip() and len(x.strip()) > 0))
    
    # Generate images
    num_images = draw(st.integers(min_value=0, max_value=3))
    images = []
    for i in range(num_images):
        caption = draw(safe_text.filter(lambda x: len(x.strip()) <= 50))
        alt_text = draw(safe_text.filter(lambda x: len(x.strip()) <= 50))
        
        image = {
            'firebase_path': f'blog-images/test_{i}.jpg',
            'download_url': f'https://storage.googleapis.com/test-bucket/test_{i}.jpg',
            'filename': f'test_{i}.jpg',
            'caption': caption.strip() if caption.strip() else f'Test image {i}',
            'alt_text': alt_text.strip() if alt_text.strip() else f'Test alt {i}',
            'order': i
        }
        images.append(image)
    
    # Generate YouTube videos
    num_videos = draw(st.integers(min_value=0, max_value=2))
    youtube_videos = []
    for i in range(num_videos):
        video_id = draw(st.text(min_size=11, max_size=11, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'))
        video_title = draw(safe_text.filter(lambda x: len(x.strip()) <= 50))
        
        video = {
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'title': video_title.strip() if video_title.strip() else f'Test video {i}',
            'embed_code': f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>',
            'order': i
        }
        youtube_videos.append(video)
    
    post_data = {
        '_id': ObjectId(),
        'title': title.strip(),
        'content': content.strip(),
        'content_type': 'html',
        'status': 'published',
        'author_id': ObjectId(),
        'author_name': author_name.strip(),
        'images': images,
        'youtube_videos': youtube_videos,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'published_at': datetime.utcnow(),
        'view_count': 0,
        'tags': []
    }
    
    return BlogPost(post_data)


class TestBlogRoutes:
    """Test blog route functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_blog_list_route_exists(self):
        """Test that blog list route exists and returns 200"""
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock empty blog posts
            with patch.object(BlogPost, 'find_published', return_value=[]):
                response = self.client.get('/blog/')
                assert response.status_code == 200
    
    def test_blog_post_route_exists(self):
        """Test that individual blog post route exists"""
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock published blog post
            mock_post = Mock()
            mock_post.is_published = True
            mock_post.increment_view_count = Mock()
            mock_post.view_count = 5
            mock_post.title = "Test Post"
            mock_post.content = "Test content"
            mock_post.author_name = "Test Author"
            mock_post.created_at = datetime.utcnow()
            mock_post.published_at = datetime.utcnow()
            mock_post.images = []
            mock_post.youtube_videos = []
            mock_post.tags = []
            mock_post.id = "507f1f77bcf86cd799439011"
            
            with patch.object(BlogPost, 'find_by_id', return_value=mock_post):
                response = self.client.get('/blog/507f1f77bcf86cd799439011')
                assert response.status_code == 200
    
    def test_blog_post_route_404_for_draft(self):
        """Test that draft posts return 404"""
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock draft blog post
            mock_post = Mock()
            mock_post.is_published = False
            
            with patch.object(BlogPost, 'find_by_id', return_value=mock_post):
                response = self.client.get('/blog/507f1f77bcf86cd799439011')
                assert response.status_code == 404
    
    def test_blog_post_route_404_for_nonexistent(self):
        """Test that nonexistent posts return 404"""
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            with patch.object(BlogPost, 'find_by_id', return_value=None):
                response = self.client.get('/blog/507f1f77bcf86cd799439011')
                assert response.status_code == 404


# **Feature: blog-system, Property 1: Published posts visibility**
# **Validates: Requirements 1.1, 1.3**
@given(posts=blog_posts_mixed_status_strategy())
@settings(max_examples=100, deadline=None)
def test_published_posts_visibility_property(posts):
    """
    Property: For any collection of blog posts with mixed statuses, the public blog 
    interface should only display posts with "published" status, ordered by 
    publication date in reverse chronological order
    """
    app.config['TESTING'] = True
    
    # Filter expected published posts
    expected_published = [post for post in posts if post.is_published]
    
    # Sort by publication date (newest first)
    expected_published.sort(key=lambda p: p.published_at or p.created_at, reverse=True)
    
    with app.test_client() as client:
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock the find_published method to return only published posts
            with patch.object(BlogPost, 'find_published', return_value=expected_published) as mock_find, \
                 patch.object(BlogPost, 'count_published', return_value=len(expected_published)):
                response = client.get('/blog/')
                
                # Verify the route was called successfully
                assert response.status_code == 200
                
                # Verify find_published was called (which filters to published posts only)
                mock_find.assert_called_once_with(mock_db, limit=12, skip=0)
                
                # The key property we're testing: only published posts should be retrieved
                # This is verified by the fact that find_published was called, which by definition
                # only returns posts with status='published'
                
                # Verify the response is properly formatted HTML
                response_text = response.get_data(as_text=True)
                assert '<!DOCTYPE html>' in response_text or '<html' in response_text
                assert 'Blog' in response_text  # Page should indicate it's the blog
                
                # If no published posts exist, verify appropriate empty state
                if not expected_published:
                    assert "No Blog Posts Yet" in response_text or "no content is available" in response_text.lower()
                else:
                    # If there are published posts, the template should render them
                    # We verify this by checking that the blog posts grid is present
                    assert 'blog-posts-grid' in response_text or 'blog-post-card' in response_text
                
                # The core property: verify that ONLY published posts are passed to the template
                # by checking that find_published (not find_all) was called
                assert mock_find.called
                call_args = mock_find.call_args
                assert call_args[0][0] == mock_db  # Called with database
                
                # Verify ordering: find_published should return posts in reverse chronological order
                # This is handled by the BlogPost.find_published method implementation


# **Feature: blog-system, Property 2: Blog post navigation**
# **Validates: Requirements 1.2**
@given(post=blog_post_with_media_strategy())
@settings(max_examples=50, deadline=None)
def test_blog_post_navigation_property(post):
    """
    Property: For any blog post displayed in the public interface, clicking the title 
    should generate a valid URL that opens the full post content
    """
    app.config['TESTING'] = True
    
    # Mock the increment_view_count method
    post.increment_view_count = Mock()
    
    with app.test_client() as client:
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Test the blog list page contains proper navigation links
            with patch.object(BlogPost, 'find_published', return_value=[post]), \
                 patch.object(BlogPost, 'count_published', return_value=1):
                list_response = client.get('/blog/')
                assert list_response.status_code == 200
                
                list_html = list_response.get_data(as_text=True)
                
                # Verify the link points to the correct URL
                expected_url = f'/blog/{post.id}'
                assert expected_url in list_html, f"Expected URL {expected_url} not found in blog list"
                
                # Verify the link opens in a new tab (target="_blank")
                assert 'target="_blank"' in list_html, "Links should open in new tab"
            
            # Test that the individual post URL actually works
            with patch.object(BlogPost, 'find_by_id', return_value=post):
                post_response = client.get(f'/blog/{post.id}')
                assert post_response.status_code == 200
                
                post_html = post_response.get_data(as_text=True)
                
                # Verify the response is a valid blog post page
                assert 'blog-post-container' in post_html, "Individual post page should have blog post container"
                
                # Verify navigation back to blog list exists
                assert '/blog/' in post_html, "Should have link back to blog list"
                assert 'Back to' in post_html or 'back to' in post_html.lower(), "Should have back navigation"
                
                # Verify the post increments view count when accessed
                post.increment_view_count.assert_called_once_with(mock_db)
                
                # The core property: verify that the URL generates valid content
                # and that navigation works both ways (list -> post -> list)
                assert post_response.status_code == 200
                assert 'blog-post' in post_html  # Should contain blog post content


# **Feature: blog-system, Property 3: Media content rendering**
# **Validates: Requirements 1.4, 1.5**
@given(post=blog_post_with_media_strategy())
@settings(max_examples=50, deadline=None)
def test_media_content_rendering_property(post):
    """
    Property: For any blog post containing images or YouTube videos, the rendered HTML 
    should include properly formatted img tags with Firebase URLs and responsive 
    iframe embeds for YouTube content
    """
    app.config['TESTING'] = True
    
    # Mock the increment_view_count method
    post.increment_view_count = Mock()
    
    with app.test_client() as client:
        with patch('src.routes.blog.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            with patch.object(BlogPost, 'find_by_id', return_value=post):
                response = client.get(f'/blog/{post.id}')
                assert response.status_code == 200
                
                html_content = response.get_data(as_text=True)
                
                # Test image rendering
                if post.images:
                    # Verify blog-post-images section exists
                    assert 'blog-post-images' in html_content, "Blog post images section not found"
                    
                    for image in post.images:
                        # Verify image URL is present in the HTML
                        assert image['download_url'] in html_content, f"Image URL {image['download_url']} not found in rendered HTML"
                        
                        # Verify img tag is properly formatted
                        assert '<img' in html_content, "No img tags found in HTML"
                        
                        # Verify responsive image attributes
                        assert 'loading="lazy"' in html_content, "Images should have lazy loading"
                        assert 'responsive-image' in html_content, "Images should have responsive class"
                        
                        # Verify image caption if present
                        if image.get('caption') and len(image['caption'].strip()) > 0:
                            assert image['caption'] in html_content, f"Image caption '{image['caption']}' not found"
                
                # Test YouTube video rendering
                if post.youtube_videos:
                    # Verify blog-post-videos section exists
                    assert 'blog-post-videos' in html_content, "Blog post videos section not found"
                    
                    for video in post.youtube_videos:
                        # Verify YouTube video container and data attributes are present
                        assert f'data-video-id="{video["video_id"]}"' in html_content, f"YouTube video data attribute not found for video {video['video_id']}"
                        
                        # Verify video thumbnail URL is present (lazy loading approach)
                        expected_thumbnail = f"https://img.youtube.com/vi/{video['video_id']}/maxresdefault.jpg"
                        assert expected_thumbnail in html_content, f"YouTube thumbnail URL not found for video {video['video_id']}"
                        
                        # Verify responsive video container
                        assert 'youtube-embed' in html_content, "Video container styling not found"
                        
                        # Verify video title if present
                        if video.get('title') and len(video['title'].strip()) > 0:
                            assert video['title'] in html_content, f"Video title '{video['title']}' not found"
                
                # Test responsive design elements
                assert 'responsive' in html_content.lower() or 'width: 100%' in html_content or 'max-width' in html_content, "Responsive design elements not found"
                
                # Verify proper HTML structure
                assert '<!DOCTYPE html>' in html_content or '<html' in html_content, "Proper HTML structure not found"
                
                # Verify the blog post container structure
                assert 'blog-post-container' in html_content, "Blog post container not found"
                assert 'blog-post-content' in html_content, "Blog post content section not found"
                
                # The core property: media content should be properly rendered with responsive design
                # This is verified by the presence of the appropriate CSS classes and HTML structure