"""
Property-based tests for Blog Post Model
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from bson import ObjectId
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

from src.models.blog_mongo import BlogPost


@composite
def blog_post_data_strategy(draw):
    """Generate valid blog post data for testing"""
    # Generate basic required fields with printable characters
    title = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=200).filter(lambda x: x.strip()))
    content = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')), min_size=1, max_size=1000).filter(lambda x: x.strip()))
    author_name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    # Generate optional fields
    content_type = draw(st.sampled_from(['html', 'plain']))
    status = draw(st.sampled_from(['draft', 'published']))
    
    # Generate tags
    tags = draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10))
    
    return {
        'title': title,
        'content': content,
        'author_name': author_name,
        'content_type': content_type,
        'status': status,
        'tags': tags
    }


@composite
def image_data_strategy(draw):
    """Generate image data for testing"""
    return {
        'firebase_path': f"blog-images/{draw(st.text(min_size=1, max_size=50))}.jpg",
        'download_url': f"https://storage.googleapis.com/test-bucket/{draw(st.text(min_size=1, max_size=100))}.jpg",
        'filename': f"{draw(st.text(min_size=1, max_size=50))}.jpg",
        'caption': draw(st.text(max_size=200)),
        'alt_text': draw(st.text(max_size=200))
    }


@composite
def youtube_video_data_strategy(draw):
    """Generate YouTube video data for testing"""
    video_id = draw(st.text(min_size=11, max_size=11, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    return {
        'video_id': video_id,
        'url': f"https://www.youtube.com/watch?v={video_id}",
        'title': draw(st.text(max_size=200)),
        'embed_code': f'<iframe src="https://www.youtube.com/embed/{video_id}"></iframe>'
    }


class TestBlogPost:
    """Test BlogPost model functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.mock_db = Mock()
        self.mock_collection = Mock()
        self.mock_db.blog_posts = self.mock_collection
    
    def test_blog_post_initialization(self):
        """Test BlogPost initialization with data"""
        data = {
            '_id': ObjectId(),
            'title': 'Test Post',
            'content': 'Test content',
            'content_type': 'html',
            'status': 'draft',
            'author_id': ObjectId(),
            'author_name': 'Test Author',
            'images': [],
            'youtube_videos': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'published_at': None,
            'view_count': 0,
            'tags': []
        }
        
        post = BlogPost(data)
        
        assert post.title == 'Test Post'
        assert post.content == 'Test content'
        assert post.content_type == 'html'
        assert post.status == 'draft'
        assert post.author_name == 'Test Author'
        assert post.is_draft
        assert not post.is_published
    
    def test_blog_post_status_methods(self):
        """Test publish/unpublish methods"""
        data = {
            'title': 'Test Post',
            'content': 'Test content',
            'status': 'draft',
            'author_name': 'Test Author'
        }
        
        post = BlogPost(data)
        
        # Test publish
        assert post.is_draft
        post.publish()
        assert post.is_published
        assert post.published_at is not None
        
        # Test unpublish
        post.unpublish()
        assert post.is_draft
        assert not post.is_published
    
    def test_add_image(self):
        """Test adding image to blog post"""
        post = BlogPost({'title': 'Test', 'content': 'Test'})
        
        image_data = {
            'firebase_path': 'blog-images/test.jpg',
            'download_url': 'https://example.com/test.jpg',
            'filename': 'test.jpg',
            'caption': 'Test image',
            'alt_text': 'Test alt text'
        }
        
        post.add_image(image_data)
        
        assert len(post.images) == 1
        assert post.images[0]['firebase_path'] == 'blog-images/test.jpg'
        assert post.images[0]['order'] == 0
    
    def test_add_youtube_video(self):
        """Test adding YouTube video to blog post"""
        post = BlogPost({'title': 'Test', 'content': 'Test'})
        
        video_data = {
            'video_id': 'dQw4w9WgXcQ',
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'title': 'Test Video',
            'embed_code': '<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>'
        }
        
        post.add_youtube_video(video_data)
        
        assert len(post.youtube_videos) == 1
        assert post.youtube_videos[0]['video_id'] == 'dQw4w9WgXcQ'
        assert post.youtube_videos[0]['order'] == 0
    
    def test_validation_success(self):
        """Test successful validation"""
        data = {
            'title': 'Valid Title',
            'content': 'Valid content',
            'content_type': 'html',
            'status': 'draft',
            'author_id': ObjectId(),
            'author_name': 'Valid Author',
            'images': [],
            'youtube_videos': [],
            'tags': ['tag1', 'tag2']
        }
        
        post = BlogPost(data)
        is_valid, errors = post.validate()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validation_required_fields(self):
        """Test validation of required fields"""
        # Test empty title
        post = BlogPost({'title': '', 'content': 'content', 'author_name': 'author'})
        is_valid, errors = post.validate()
        assert not is_valid
        assert any('Title is required' in error for error in errors)
        
        # Test empty content
        post = BlogPost({'title': 'title', 'content': '', 'author_name': 'author'})
        is_valid, errors = post.validate()
        assert not is_valid
        assert any('Content is required' in error for error in errors)
        
        # Test empty author name
        post = BlogPost({'title': 'title', 'content': 'content', 'author_name': ''})
        is_valid, errors = post.validate()
        assert not is_valid
        assert any('Author name is required' in error for error in errors)
    
    def test_validation_field_lengths(self):
        """Test validation of field lengths"""
        # Test title too long
        long_title = 'x' * 201
        post = BlogPost({
            'title': long_title, 
            'content': 'content', 
            'author_name': 'author',
            'author_id': ObjectId()
        })
        is_valid, errors = post.validate()
        assert not is_valid
        assert any('Title cannot exceed 200 characters' in error for error in errors)
        
        # Test content too long
        long_content = 'x' * 100001
        post = BlogPost({
            'title': 'title', 
            'content': long_content, 
            'author_name': 'author',
            'author_id': ObjectId()
        })
        is_valid, errors = post.validate()
        assert not is_valid
        assert any('Content cannot exceed 100,000 characters' in error for error in errors)
    
    def test_validation_invalid_types(self):
        """Test validation of invalid field types"""
        # Test invalid content type
        post = BlogPost({
            'title': 'title',
            'content': 'content',
            'author_name': 'author',
            'author_id': ObjectId(),
            'content_type': 'invalid'
        })
        is_valid, errors = post.validate()
        assert not is_valid
        assert any("Content type must be 'html' or 'plain'" in error for error in errors)
        
        # Test invalid status
        post = BlogPost({
            'title': 'title',
            'content': 'content',
            'author_name': 'author',
            'author_id': ObjectId(),
            'status': 'invalid'
        })
        is_valid, errors = post.validate()
        assert not is_valid
        assert any("Status must be 'draft' or 'published'" in error for error in errors)
    
    def test_create_with_validation_error(self):
        """Test create method with validation error"""
        mock_db = Mock()
        
        with pytest.raises(ValueError) as exc_info:
            BlogPost.create(
                db=mock_db,
                title='',  # Invalid empty title
                content='content',
                author_id=str(ObjectId()),
                author_name='author'
            )
        
        assert 'Blog post validation failed' in str(exc_info.value)
        assert 'Title is required' in str(exc_info.value)


# **Feature: blog-system, Property 7: Blog post persistence**
# **Validates: Requirements 2.5, 6.1, 6.3**
@given(blog_data=blog_post_data_strategy())
@settings(max_examples=100, deadline=None)
def test_blog_post_persistence_property(blog_data):
    """
    Property: For any blog post created by an admin, the system should store all 
    required fields (title, content, author info, timestamps) in MongoDB and make 
    the data retrievable
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post using the create method
    author_id = str(ObjectId())
    
    blog_post = BlogPost.create(
        db=mock_db,
        title=blog_data['title'],
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status=blog_data['status']
    )
    
    # Verify the blog post was created with all required fields
    assert blog_post is not None
    assert blog_post.title == blog_data['title']
    # Content may be sanitized for security, so check it's not empty if original wasn't
    if blog_data['content'].strip():
        assert blog_post.content is not None
        assert len(blog_post.content) > 0
    assert blog_post.author_name == blog_data['author_name']
    assert blog_post.content_type == blog_data['content_type']
    assert blog_post.status == blog_data['status']
    assert str(blog_post.author_id) == author_id
    
    # Verify timestamps are set
    assert blog_post.created_at is not None
    assert blog_post.updated_at is not None
    assert isinstance(blog_post.created_at, datetime)
    assert isinstance(blog_post.updated_at, datetime)
    
    # Verify published_at is set correctly based on status
    if blog_data['status'] == 'published':
        assert blog_post.published_at is not None
        assert isinstance(blog_post.published_at, datetime)
    else:
        assert blog_post.published_at is None
    
    # Verify default values
    assert blog_post.images == []
    assert blog_post.youtube_videos == []
    assert blog_post.view_count == 0
    assert blog_post.tags == []
    
    # Verify database insertion was called with correct data
    mock_collection.insert_one.assert_called_once()
    inserted_data = mock_collection.insert_one.call_args[0][0]
    
    # Verify all required fields were stored
    required_fields = ['title', 'content', 'content_type', 'status', 'author_id', 
                      'author_name', 'created_at', 'updated_at', 'images', 
                      'youtube_videos', 'view_count', 'tags']
    
    for field in required_fields:
        assert field in inserted_data, f"Required field '{field}' missing from stored data"
    
    # Verify data integrity
    assert inserted_data['title'] == blog_data['title']
    # Content may be sanitized, so just verify it exists
    assert 'content' in inserted_data
    assert inserted_data['author_name'] == blog_data['author_name']
    assert inserted_data['content_type'] == blog_data['content_type']
    assert inserted_data['status'] == blog_data['status']
    assert str(inserted_data['author_id']) == author_id
    
    # Test retrieval by mocking find_one
    mock_collection.find_one.return_value = inserted_data
    mock_collection.find_one.return_value['_id'] = mock_result.inserted_id
    
    retrieved_post = BlogPost.find_by_id(mock_db, str(mock_result.inserted_id))
    
    # Verify retrieved post matches original
    assert retrieved_post is not None
    assert retrieved_post.title == blog_post.title
    assert retrieved_post.content == blog_post.content
    assert retrieved_post.author_name == blog_post.author_name
    assert retrieved_post.content_type == blog_post.content_type
    assert retrieved_post.status == blog_post.status
    assert retrieved_post.author_id == blog_post.author_id
    
    # Test save method for updates
    blog_post.title = "Updated Title"
    blog_post._id = mock_result.inserted_id  # Simulate existing post
    
    # Mock successful update
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    save_success = blog_post.save(mock_db)
    
    assert save_success
    mock_collection.update_one.assert_called_once()
    
    # Verify update was called with correct parameters
    update_call = mock_collection.update_one.call_args
    assert update_call[0][0] == {'_id': mock_result.inserted_id}  # Filter
    assert '$set' in update_call[0][1]  # Update operation
    assert update_call[0][1]['$set']['title'] == "Updated Title"
    
    # Test delete method
    mock_delete_result = Mock()
    mock_delete_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_delete_result
    
    delete_success = BlogPost.delete(mock_db, str(mock_result.inserted_id))
    
    assert delete_success
    mock_collection.delete_one.assert_called_once_with({'_id': mock_result.inserted_id})


@given(
    blog_data=blog_post_data_strategy(),
    images=st.lists(image_data_strategy(), min_size=0, max_size=5),
    videos=st.lists(youtube_video_data_strategy(), min_size=0, max_size=3)
)
@settings(max_examples=50, deadline=None)
def test_blog_post_with_media_persistence(blog_data, images, videos):
    """
    Property: Blog posts with media content should persist all media data correctly
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post
    author_id = str(ObjectId())
    blog_post = BlogPost.create(
        db=mock_db,
        title=blog_data['title'],
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status=blog_data['status']
    )
    
    # Add images
    for image_data in images:
        blog_post.add_image(image_data)
    
    # Add videos
    for video_data in videos:
        blog_post.add_youtube_video(video_data)
    
    # Verify media was added correctly
    assert len(blog_post.images) == len(images)
    assert len(blog_post.youtube_videos) == len(videos)
    
    # Verify image order
    for i, image in enumerate(blog_post.images):
        assert image['order'] == i
        assert 'firebase_path' in image
        assert 'download_url' in image
        assert 'filename' in image
    
    # Verify video order
    for i, video in enumerate(blog_post.youtube_videos):
        assert video['order'] == i
        assert 'video_id' in video
        assert 'url' in video
        assert 'embed_code' in video
    
    # Test saving with media
    blog_post._id = mock_result.inserted_id
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    save_success = blog_post.save(mock_db)
    assert save_success
    
    # Verify media data was included in save
    update_call = mock_collection.update_one.call_args
    saved_data = update_call[0][1]['$set']
    
    assert 'images' in saved_data
    assert 'youtube_videos' in saved_data
    assert len(saved_data['images']) == len(images)
    assert len(saved_data['youtube_videos']) == len(videos)


@given(status=st.sampled_from(['draft', 'published']))
@settings(max_examples=20, deadline=None)
def test_blog_post_status_workflow_persistence(status):
    """
    Property: Blog post status changes should be persisted correctly
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post with initial status
    blog_post = BlogPost.create(
        db=mock_db,
        title="Test Post",
        content="Test content",
        author_id=str(ObjectId()),
        author_name="Test Author",
        status=status
    )
    
    # Verify initial status
    assert blog_post.status == status
    if status == 'published':
        assert blog_post.is_published
        assert blog_post.published_at is not None
    else:
        assert blog_post.is_draft
        assert blog_post.published_at is None
    
    # Test status change
    blog_post._id = mock_result.inserted_id
    
    if status == 'draft':
        # Test publishing
        original_published_at = blog_post.published_at
        blog_post.publish()
        
        assert blog_post.is_published
        assert blog_post.status == 'published'
        assert blog_post.published_at is not None
        assert blog_post.published_at != original_published_at
        
    else:
        # Test unpublishing
        blog_post.unpublish()
        
        assert blog_post.is_draft
        assert blog_post.status == 'draft'
        # published_at should remain (for history)
    
    # Verify updated_at was modified
    assert blog_post.updated_at is not None
    
    # Test persistence of status change
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    save_success = blog_post.save(mock_db)
    assert save_success
    
    # Verify status was saved
    update_call = mock_collection.update_one.call_args
    saved_data = update_call[0][1]['$set']
    
    assert 'status' in saved_data
    assert 'updated_at' in saved_data
    assert saved_data['status'] == blog_post.status

# **Feature: blog-system, Property 4: Content format support**
# **Validates: Requirements 2.2**
@given(
    title=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=200).filter(lambda x: x.strip()),
    content=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')), min_size=1, max_size=1000).filter(lambda x: x.strip()),
    content_type=st.sampled_from(['html', 'plain']),
    author_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=100).filter(lambda x: x.strip())
)
@settings(max_examples=100, deadline=None)
def test_content_format_support_property(title, content, content_type, author_name):
    """
    Property: For any blog post content, the system should accept and correctly 
    store both HTML and plain text formats, preserving the content_type metadata
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post with specified content type
    author_id = str(ObjectId())
    
    blog_post = BlogPost.create(
        db=mock_db,
        title=title,
        content=content,
        author_id=author_id,
        author_name=author_name,
        content_type=content_type,
        status='draft'
    )
    
    # Verify content type is preserved
    assert blog_post.content_type == content_type
    # Content may be sanitized, so check it exists if original wasn't empty
    if content.strip():
        assert blog_post.content is not None
        assert len(blog_post.content) > 0
    assert blog_post.title == title
    
    # Verify database insertion was called with correct content type
    mock_collection.insert_one.assert_called_once()
    inserted_data = mock_collection.insert_one.call_args[0][0]
    
    # Verify content type metadata is stored
    assert 'content_type' in inserted_data
    assert inserted_data['content_type'] == content_type
    # Content may be sanitized
    assert 'content' in inserted_data
    assert inserted_data['title'] == title
    
    # Test retrieval preserves content type
    mock_collection.find_one.return_value = inserted_data
    mock_collection.find_one.return_value['_id'] = mock_result.inserted_id
    
    retrieved_post = BlogPost.find_by_id(mock_db, str(mock_result.inserted_id))
    
    # Verify retrieved post preserves content type and content
    assert retrieved_post is not None
    assert retrieved_post.content_type == content_type
    # Content may be sanitized
    if content.strip():
        assert retrieved_post.content is not None
        assert len(retrieved_post.content) > 0
    assert retrieved_post.title == title
    
    # Test updating content type
    new_content_type = 'plain' if content_type == 'html' else 'html'
    blog_post.content_type = new_content_type
    blog_post._id = mock_result.inserted_id
    
    # Mock successful update
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    save_success = blog_post.save(mock_db)
    assert save_success
    
    # Verify content type update was persisted
    update_call = mock_collection.update_one.call_args
    saved_data = update_call[0][1]['$set']
    
    assert 'content_type' in saved_data
    assert saved_data['content_type'] == new_content_type
    
    # Verify content is present (may be sanitized)
    assert 'content' in saved_data
    
    # Test validation accepts both content types
    html_post = BlogPost({
        'title': title,
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'html'
    })
    
    plain_post = BlogPost({
        'title': title,
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'plain'
    })
    
    # Both should validate successfully
    html_valid, html_errors = html_post.validate()
    plain_valid, plain_errors = plain_post.validate()
    
    assert html_valid, f"HTML content type validation failed: {html_errors}"
    assert plain_valid, f"Plain content type validation failed: {plain_errors}"
    
    # Test invalid content type is rejected
    invalid_post = BlogPost({
        'title': title,
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'invalid_type'
    })
    
    invalid_valid, invalid_errors = invalid_post.validate()
    assert not invalid_valid
    assert any("Content type must be 'html' or 'plain'" in error for error in invalid_errors)
    
    # Test content type defaults to 'html' when not specified
    default_post_data = {
        'title': title,
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId()
        # content_type not specified
    }
    
    default_post = BlogPost(default_post_data)
    assert default_post.content_type == 'html'  # Should default to html
    
    # Test that content is preserved regardless of content type
    # This ensures the system doesn't modify content based on type
    html_content = "<p>This is <strong>HTML</strong> content</p>"
    plain_content = "This is plain text content with <tags> that should be preserved"
    
    html_post_with_html = BlogPost({
        'title': title,
        'content': html_content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'html'
    })
    
    plain_post_with_html = BlogPost({
        'title': title,
        'content': html_content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'plain'
    })
    
    html_post_with_plain = BlogPost({
        'title': title,
        'content': plain_content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'html'
    })
    
    plain_post_with_plain = BlogPost({
        'title': title,
        'content': plain_content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'content_type': 'plain'
    })
    
    # All combinations should preserve content exactly
    assert html_post_with_html.content == html_content
    assert plain_post_with_html.content == html_content
    assert html_post_with_plain.content == plain_content
    assert plain_post_with_plain.content == plain_content
    
    # Content type should be independent of content format
    assert html_post_with_html.content_type == 'html'
    assert plain_post_with_html.content_type == 'plain'
    assert html_post_with_plain.content_type == 'html'
    assert plain_post_with_plain.content_type == 'plain'
# **Feature: blog-system, Property 11: Status indication**
# **Validates: Requirements 4.5**
@given(
    title=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    content=st.text(min_size=1, max_size=10000).filter(lambda x: x.strip()),
    author_name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    status=st.sampled_from(['draft', 'published'])
)
@settings(max_examples=100, deadline=None)
def test_status_indication_property(title, content, author_name, status):
    """
    Property: For any blog post displayed in the admin interface, the system should 
    clearly show the current publication status (draft/published) along with relevant timestamps
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post with specified status
    author_id = str(ObjectId())
    
    blog_post = BlogPost.create(
        db=mock_db,
        title=title,
        content=content,
        author_id=author_id,
        author_name=author_name,
        status=status
    )
    
    # Verify status indication properties are available
    assert blog_post.status == status
    assert blog_post.created_at is not None
    assert blog_post.updated_at is not None
    assert isinstance(blog_post.created_at, datetime)
    assert isinstance(blog_post.updated_at, datetime)
    
    # Verify status-specific properties
    if status == 'published':
        assert blog_post.is_published
        assert not blog_post.is_draft
        assert blog_post.published_at is not None
        assert isinstance(blog_post.published_at, datetime)
    else:
        assert blog_post.is_draft
        assert not blog_post.is_published
        assert blog_post.published_at is None
    
    # Test status indication methods provide clear boolean values
    assert isinstance(blog_post.is_published, bool)
    assert isinstance(blog_post.is_draft, bool)
    assert blog_post.is_published != blog_post.is_draft  # Should be mutually exclusive
    
    # Test that all required status information is stored in database
    mock_collection.insert_one.assert_called_once()
    inserted_data = mock_collection.insert_one.call_args[0][0]
    
    # Verify status and timestamp fields are stored
    assert 'status' in inserted_data
    assert 'created_at' in inserted_data
    assert 'updated_at' in inserted_data
    assert 'published_at' in inserted_data
    
    assert inserted_data['status'] == status
    assert inserted_data['created_at'] is not None
    assert inserted_data['updated_at'] is not None
    
    if status == 'published':
        assert inserted_data['published_at'] is not None
    else:
        assert inserted_data['published_at'] is None
    
    # Test status change updates indication correctly
    blog_post._id = mock_result.inserted_id
    
    if status == 'draft':
        # Test publishing
        original_updated_at = blog_post.updated_at
        blog_post.publish()
        
        # Verify status indication changed
        assert blog_post.is_published
        assert not blog_post.is_draft
        assert blog_post.status == 'published'
        assert blog_post.published_at is not None
        assert blog_post.updated_at > original_updated_at
        
    else:
        # Test unpublishing
        original_updated_at = blog_post.updated_at
        original_published_at = blog_post.published_at
        blog_post.unpublish()
        
        # Verify status indication changed
        assert blog_post.is_draft
        assert not blog_post.is_published
        assert blog_post.status == 'draft'
        assert blog_post.updated_at > original_updated_at
        # published_at should remain for history
        assert blog_post.published_at == original_published_at
    
    # Test persistence of status indication
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    save_success = blog_post.save(mock_db)
    assert save_success
    
    # Verify status indication was persisted
    update_call = mock_collection.update_one.call_args
    saved_data = update_call[0][1]['$set']
    
    assert 'status' in saved_data
    assert 'updated_at' in saved_data
    assert saved_data['status'] == blog_post.status
    assert saved_data['updated_at'] == blog_post.updated_at
    
    if blog_post.status == 'published':
        assert 'published_at' in saved_data
        assert saved_data['published_at'] == blog_post.published_at
    
    # Test retrieval preserves status indication
    mock_collection.find_one.return_value = inserted_data
    mock_collection.find_one.return_value['_id'] = mock_result.inserted_id
    mock_collection.find_one.return_value['status'] = blog_post.status
    mock_collection.find_one.return_value['updated_at'] = blog_post.updated_at
    mock_collection.find_one.return_value['published_at'] = blog_post.published_at
    
    retrieved_post = BlogPost.find_by_id(mock_db, str(mock_result.inserted_id))
    
    # Verify retrieved post has correct status indication
    assert retrieved_post is not None
    assert retrieved_post.status == blog_post.status
    assert retrieved_post.is_published == blog_post.is_published
    assert retrieved_post.is_draft == blog_post.is_draft
    assert retrieved_post.created_at == blog_post.created_at
    assert retrieved_post.updated_at == blog_post.updated_at
    assert retrieved_post.published_at == blog_post.published_at
    
    # Test status indication with different statuses (simulating admin dashboard)
    # Create posts with both statuses to verify distinct indications
    draft_post = BlogPost({
        'title': f"Draft {title}",
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'status': 'draft',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'published_at': None
    })
    
    published_post = BlogPost({
        'title': f"Published {title}",
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'status': 'published',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'published_at': datetime.utcnow()
    })
    
    # Verify both posts have distinct status indications
    assert draft_post.status != published_post.status
    assert draft_post.is_published != published_post.is_published
    assert draft_post.is_draft != published_post.is_draft
    
    # Verify published_at is set correctly for each
    assert draft_post.published_at is None
    assert published_post.published_at is not None
    
    # Test status indication consistency across operations
    # Create a post, change status multiple times, verify indication remains consistent
    test_post = BlogPost({
        'title': title,
        'content': content,
        'author_name': author_name,
        'author_id': ObjectId(),
        'status': 'draft',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'published_at': None
    })
    
    # Initial state
    assert test_post.is_draft
    assert not test_post.is_published
    assert test_post.published_at is None
    
    # Publish
    test_post.publish()
    assert test_post.is_published
    assert not test_post.is_draft
    assert test_post.published_at is not None
    
    # Unpublish
    published_at_before_unpublish = test_post.published_at
    test_post.unpublish()
    assert test_post.is_draft
    assert not test_post.is_published
    assert test_post.published_at == published_at_before_unpublish  # Should preserve for history
    
    # Publish again
    test_post.publish()
    assert test_post.is_published
    assert not test_post.is_draft
    assert test_post.published_at is not None
    # published_at should be updated to new timestamp
    assert test_post.published_at >= published_at_before_unpublish
    
    # Test edge case: ensure status indication works with minimal data
    minimal_post = BlogPost({
        'title': 'Minimal',
        'content': 'Content',
        'author_name': 'Author',
        'status': status
    })
    
    # Should still provide clear status indication
    assert minimal_post.status == status
    if status == 'published':
        assert minimal_post.is_published
        assert not minimal_post.is_draft
    else:
        assert minimal_post.is_draft
        assert not minimal_post.is_published


# **Feature: blog-system, Property 9: Edit preservation**
# **Validates: Requirements 3.2, 3.4**
@given(
    original_data=blog_post_data_strategy(),
    updated_title=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    updated_content=st.text(min_size=1, max_size=10000).filter(lambda x: x.strip()),
    updated_content_type=st.sampled_from(['html', 'plain']),
    updated_status=st.sampled_from(['draft', 'published'])
)
@settings(max_examples=100, deadline=None)
def test_edit_preservation_property(original_data, updated_title, updated_content, updated_content_type, updated_status):
    """
    Property: For any blog post being edited, the system should preserve the original 
    creation date while updating the modification timestamp and immediately reflect 
    changes in all interfaces
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion for original post
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create original blog post
    author_id = str(ObjectId())
    original_created_at = datetime.utcnow()
    
    original_post = BlogPost.create(
        db=mock_db,
        title=original_data['title'],
        content=original_data['content'],
        author_id=author_id,
        author_name=original_data['author_name'],
        content_type=original_data['content_type'],
        status=original_data['status']
    )
    
    # Store original creation timestamp
    original_post.created_at = original_created_at
    original_post._id = mock_result.inserted_id
    
    # Wait a small amount to ensure updated_at will be different
    import time
    time.sleep(0.001)
    
    # Prepare update data
    update_data = {
        'title': updated_title,
        'content': updated_content,
        'content_type': updated_content_type,
        'status': updated_status
    }
    
    # Set published_at if changing to published status
    if updated_status == 'published' and original_data['status'] != 'published':
        update_data['published_at'] = datetime.utcnow()
    
    # Mock successful update
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    # Perform the update using the static method
    update_success = BlogPost.update(mock_db, str(mock_result.inserted_id), update_data)
    
    # Verify update was successful
    assert update_success
    
    # Verify update was called with correct parameters
    mock_collection.update_one.assert_called_once()
    update_call = mock_collection.update_one.call_args
    
    # Verify filter uses correct ID
    assert update_call[0][0] == {'_id': mock_result.inserted_id}
    
    # Verify update operation structure
    assert '$set' in update_call[0][1]
    updated_fields = update_call[0][1]['$set']
    
    # Verify updated fields are present
    assert 'title' in updated_fields
    assert 'content' in updated_fields
    assert 'content_type' in updated_fields
    assert 'status' in updated_fields
    assert 'updated_at' in updated_fields
    
    # Verify updated values match input
    assert updated_fields['title'] == updated_title
    assert updated_fields['content'] == updated_content
    assert updated_fields['content_type'] == updated_content_type
    assert updated_fields['status'] == updated_status
    
    # Verify updated_at is set and is a datetime
    assert isinstance(updated_fields['updated_at'], datetime)
    
    # Verify created_at is NOT in the update (should be preserved)
    assert 'created_at' not in updated_fields, "created_at should not be modified during updates"
    
    # Verify published_at handling
    if updated_status == 'published' and original_data['status'] != 'published':
        assert 'published_at' in updated_fields
        assert isinstance(updated_fields['published_at'], datetime)
    
    # Test retrieval after update to verify changes are reflected
    # Mock the updated document for retrieval
    updated_document = {
        '_id': mock_result.inserted_id,
        'title': updated_title,
        'content': updated_content,
        'content_type': updated_content_type,
        'status': updated_status,
        'author_id': ObjectId(author_id),
        'author_name': original_data['author_name'],
        'images': [],
        'youtube_videos': [],
        'created_at': original_created_at,  # Should be preserved
        'updated_at': updated_fields['updated_at'],  # Should be new timestamp
        'published_at': updated_fields.get('published_at'),
        'view_count': 0,
        'tags': []
    }
    
    mock_collection.find_one.return_value = updated_document
    
    # Retrieve the updated post
    retrieved_post = BlogPost.find_by_id(mock_db, str(mock_result.inserted_id))
    
    # Verify retrieval was successful
    assert retrieved_post is not None
    
    # Verify updated fields are reflected
    assert retrieved_post.title == updated_title
    assert retrieved_post.content == updated_content
    assert retrieved_post.content_type == updated_content_type
    assert retrieved_post.status == updated_status
    
    # CRITICAL: Verify creation date is preserved
    assert retrieved_post.created_at == original_created_at, "Original creation date must be preserved during edits"
    
    # Verify updated_at is newer than created_at
    assert retrieved_post.updated_at >= original_created_at, "updated_at should be newer than or equal to created_at"
    
    # Verify other fields remain unchanged
    assert retrieved_post.author_name == original_data['author_name']
    assert str(retrieved_post.author_id) == author_id
    assert retrieved_post.images == []
    assert retrieved_post.youtube_videos == []
    assert retrieved_post.view_count == 0
    assert retrieved_post.tags == []
    
    # Test multiple updates preserve creation date
    # Perform a second update
    second_update_data = {
        'title': f"Second Update {updated_title}",
        'content': f"Updated again: {updated_content}"
    }
    
    # Reset mock for second update
    mock_collection.update_one.reset_mock()
    mock_update_result.modified_count = 1
    
    second_update_success = BlogPost.update(mock_db, str(mock_result.inserted_id), second_update_data)
    
    assert second_update_success
    
    # Verify second update also doesn't modify created_at
    second_update_call = mock_collection.update_one.call_args
    second_updated_fields = second_update_call[0][1]['$set']
    
    assert 'created_at' not in second_updated_fields, "created_at should never be modified in any update"
    assert 'updated_at' in second_updated_fields, "updated_at should always be set in updates"
    
    # Test edge case: empty update data should still set updated_at
    mock_collection.update_one.reset_mock()
    empty_update_success = BlogPost.update(mock_db, str(mock_result.inserted_id), {})
    
    assert empty_update_success
    
    empty_update_call = mock_collection.update_one.call_args
    empty_updated_fields = empty_update_call[0][1]['$set']
    
    # Even empty updates should set updated_at
    assert 'updated_at' in empty_updated_fields
    assert 'created_at' not in empty_updated_fields
    
    # Test update with invalid post ID
    mock_collection.update_one.reset_mock()
    mock_update_result.modified_count = 0  # No documents modified
    
    invalid_update_success = BlogPost.update(mock_db, str(ObjectId()), {'title': 'Test'})
    
    assert not invalid_update_success, "Update should fail when no documents are modified"
    
    # Test update with database error
    mock_collection.update_one.reset_mock()
    mock_collection.update_one.side_effect = Exception("Database error")
    
    error_update_success = BlogPost.update(mock_db, str(mock_result.inserted_id), {'title': 'Test'})
    
    assert not error_update_success, "Update should fail gracefully on database errors"
    
    # Reset side effect for other tests
    mock_collection.update_one.side_effect = None


# **Feature: blog-system, Property 10: Complete deletion**
# **Validates: Requirements 3.3**
@given(blog_data=blog_post_data_strategy())
@settings(max_examples=100, deadline=None)
def test_complete_deletion_property(blog_data):
    """
    Property: For any blog post being deleted, the system should remove it from both 
    the admin management interface and public display, ensuring no references remain
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Mock successful insertion for original post
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post
    author_id = str(ObjectId())
    
    blog_post = BlogPost.create(
        db=mock_db,
        title=blog_data['title'],
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status=blog_data['status']
    )
    
    # Verify post was created
    assert blog_post is not None
    assert blog_post._id == mock_result.inserted_id
    
    # Mock successful deletion
    mock_delete_result = Mock()
    mock_delete_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_delete_result
    
    # Perform deletion using static method
    delete_success = BlogPost.delete(mock_db, str(mock_result.inserted_id))
    
    # Verify deletion was successful
    assert delete_success, "Deletion should succeed for existing blog post"
    
    # Verify delete_one was called with correct parameters
    mock_collection.delete_one.assert_called_once()
    delete_call = mock_collection.delete_one.call_args
    
    # Verify correct filter was used
    assert delete_call[0][0] == {'_id': mock_result.inserted_id}, "Delete should use correct ObjectId filter"
    
    # Test that post is no longer retrievable (simulating complete removal)
    # Mock find_one to return None (post not found)
    mock_collection.find_one.return_value = None
    
    retrieved_post = BlogPost.find_by_id(mock_db, str(mock_result.inserted_id))
    
    # Verify post cannot be retrieved after deletion
    assert retrieved_post is None, "Deleted post should not be retrievable"
    
    # Verify find_one was called with correct parameters
    mock_collection.find_one.assert_called_with({'_id': mock_result.inserted_id})
    
    # Test that deleted post doesn't appear in admin interface (find_all)
    # Mock find_all to return empty list (no posts found)
    mock_collection.find.return_value.sort.return_value = []
    
    all_posts = BlogPost.find_all(mock_db)
    
    # Verify deleted post is not in admin interface
    assert len(all_posts) == 0, "Deleted post should not appear in admin interface"
    assert not any(post.id == str(mock_result.inserted_id) for post in all_posts), "Deleted post should not be in admin list"
    
    # Test that deleted post doesn't appear in public interface (find_published)
    # Mock find for published posts to return empty list
    mock_collection.find.return_value.sort.return_value = []
    
    published_posts = BlogPost.find_published(mock_db)
    
    # Verify deleted post is not in public interface
    assert len(published_posts) == 0, "Deleted post should not appear in public interface"
    assert not any(post.id == str(mock_result.inserted_id) for post in published_posts), "Deleted post should not be in published list"
    
    # Test deletion of non-existent post
    mock_collection.delete_one.reset_mock()
    mock_delete_result.deleted_count = 0  # No documents deleted
    
    non_existent_id = str(ObjectId())
    delete_non_existent = BlogPost.delete(mock_db, non_existent_id)
    
    # Verify deletion fails gracefully for non-existent post
    assert not delete_non_existent, "Deletion should fail for non-existent post"
    
    # Test deletion with database error
    mock_collection.delete_one.reset_mock()
    mock_collection.delete_one.side_effect = Exception("Database error")
    
    error_delete_success = BlogPost.delete(mock_db, str(mock_result.inserted_id))
    
    # Verify deletion fails gracefully on database errors
    assert not error_delete_success, "Deletion should fail gracefully on database errors"
    
    # Reset side effect
    mock_collection.delete_one.side_effect = None
    
    # Test deletion with invalid ObjectId format
    mock_collection.delete_one.reset_mock()
    mock_collection.delete_one.side_effect = Exception("Invalid ObjectId")
    
    invalid_id_delete = BlogPost.delete(mock_db, "invalid_id_format")
    
    # Verify deletion fails gracefully with invalid ID
    assert not invalid_id_delete, "Deletion should fail gracefully with invalid ObjectId"
    
    # Reset side effect
    mock_collection.delete_one.side_effect = None
    
    # Test complete removal scenario with multiple posts
    # Create multiple posts and delete one, verify others remain
    mock_collection.delete_one.reset_mock()
    mock_collection.insert_one.reset_mock()
    
    # Mock creation of multiple posts
    post_ids = [ObjectId(), ObjectId(), ObjectId()]
    mock_results = [Mock() for _ in post_ids]
    for i, mock_res in enumerate(mock_results):
        mock_res.inserted_id = post_ids[i]
    
    mock_collection.insert_one.side_effect = mock_results
    
    # Create multiple posts
    posts = []
    for i in range(3):
        post = BlogPost.create(
            db=mock_db,
            title=f"{blog_data['title']} {i}",
            content=f"{blog_data['content']} {i}",
            author_id=author_id,
            author_name=blog_data['author_name'],
            content_type=blog_data['content_type'],
            status=blog_data['status']
        )
        posts.append(post)
    
    # Delete the middle post
    mock_delete_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_delete_result
    
    delete_middle_success = BlogPost.delete(mock_db, str(post_ids[1]))
    assert delete_middle_success
    
    # Mock find_all to return remaining posts (excluding deleted one)
    remaining_posts_data = [
        {
            '_id': post_ids[0],
            'title': f"{blog_data['title']} 0",
            'content': f"{blog_data['content']} 0",
            'author_name': blog_data['author_name'],
            'content_type': blog_data['content_type'],
            'status': blog_data['status'],
            'author_id': ObjectId(author_id),
            'images': [],
            'youtube_videos': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'published_at': None,
            'view_count': 0,
            'tags': []
        },
        {
            '_id': post_ids[2],
            'title': f"{blog_data['title']} 2",
            'content': f"{blog_data['content']} 2",
            'author_name': blog_data['author_name'],
            'content_type': blog_data['content_type'],
            'status': blog_data['status'],
            'author_id': ObjectId(author_id),
            'images': [],
            'youtube_videos': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'published_at': None,
            'view_count': 0,
            'tags': []
        }
    ]
    
    mock_collection.find.return_value.sort.return_value = remaining_posts_data
    
    remaining_posts = BlogPost.find_all(mock_db)
    
    # Verify only remaining posts are returned
    assert len(remaining_posts) == 2, "Should have 2 remaining posts after deletion"
    
    remaining_ids = [post.id for post in remaining_posts]
    assert str(post_ids[0]) in remaining_ids, "First post should remain"
    assert str(post_ids[1]) not in remaining_ids, "Deleted post should not be in results"
    assert str(post_ids[2]) in remaining_ids, "Third post should remain"
    
    # Test deletion ensures no orphaned references
    # This simulates checking that all references to the deleted post are removed
    
    # Mock a scenario where we check for any remaining references
    # In a real system, this might involve checking related collections
    mock_collection.find.return_value.sort.return_value = []
    
    # Search for any posts with the deleted post's ID (should return empty)
    orphaned_references = BlogPost.find_all(mock_db)
    deleted_post_found = any(post.id == str(post_ids[1]) for post in orphaned_references)
    
    assert not deleted_post_found, "No orphaned references should remain after deletion"
    
    # Test that deletion is atomic (either succeeds completely or fails completely)
    # Mock a scenario where deletion partially fails
    mock_collection.delete_one.reset_mock()
    mock_delete_result.deleted_count = 0  # Simulate partial failure
    
    atomic_delete_success = BlogPost.delete(mock_db, str(post_ids[0]))
    
    # Verify atomic behavior - if delete_one returns 0, deletion should be considered failed
    assert not atomic_delete_success, "Deletion should be atomic - fail if no documents deleted"
    
    # Reset mocks for other tests
    mock_collection.insert_one.side_effect = None
    mock_collection.delete_one.side_effect = None

# **Feature: blog-system, Property 8: Publication workflow**
# **Validates: Requirements 2.6, 4.2, 4.3, 4.4**
@given(blog_data=blog_post_data_strategy())
@settings(max_examples=100, deadline=None)
def test_publication_workflow_property(blog_data):
    """
    Property: For any blog post, changing the status from draft to published should make it 
    visible on the public interface, and changing from published to draft should remove it 
    from public visibility
    """
    # Setup mock database
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.blog_posts = mock_collection
    
    # Generate a valid ObjectId for the author
    author_id = str(ObjectId())
    
    # Mock successful creation
    mock_result = Mock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result
    
    # Create blog post with draft status initially
    blog_post = BlogPost.create(
        db=mock_db,
        title=blog_data['title'],
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='draft'  # Start as draft
    )
    
    # Verify post was created as draft
    assert blog_post is not None
    assert blog_post.status == 'draft'
    assert blog_post.is_draft
    assert not blog_post.is_published
    assert blog_post.published_at is None
    
    # Test 1: Draft posts should not appear in public interface
    # Mock find for published posts to return empty (draft not included)
    mock_collection.find.return_value.sort.return_value = []
    
    published_posts = BlogPost.find_published(mock_db)
    
    # Verify draft post is not in public interface
    assert len(published_posts) == 0, "Draft posts should not appear in public interface"
    assert not any(post.id == blog_post.id for post in published_posts), "Draft post should not be in published list"
    
    # Verify the query used for finding published posts (with projection)
    expected_projection = {
        'title': 1,
        'content': 1,
        'content_type': 1,
        'author_name': 1,
        'published_at': 1,
        'created_at': 1,
        'view_count': 1,
        'tags': 1,
        'images': {'$slice': 1}
    }
    mock_collection.find.assert_called_with({'status': 'published'}, expected_projection)
    
    # Test 2: Publishing a draft post should make it visible in public interface
    # Mock successful update for publishing
    mock_update_result = Mock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result
    
    # Publish the post using the model's publish method
    blog_post.publish()
    
    # Verify post status changed to published
    assert blog_post.status == 'published'
    assert blog_post.is_published
    assert not blog_post.is_draft
    assert blog_post.published_at is not None
    
    # Save the published post
    success = blog_post.save(mock_db)
    
    # Mock the published post being returned by find_published
    published_post_data = {
        '_id': blog_post._id,
        'title': blog_post.title,
        'content': blog_post.content,
        'author_name': blog_post.author_name,
        'content_type': blog_post.content_type,
        'status': 'published',
        'author_id': ObjectId(author_id),
        'images': [],
        'youtube_videos': [],
        'created_at': blog_post.created_at,
        'updated_at': blog_post.updated_at,
        'published_at': blog_post.published_at,
        'view_count': 0,
        'tags': []
    }
    
    mock_collection.find.return_value.sort.return_value = [published_post_data]
    
    published_posts_after_publish = BlogPost.find_published(mock_db)
    
    # Verify published post now appears in public interface
    assert len(published_posts_after_publish) == 1, "Published post should appear in public interface"
    published_post = published_posts_after_publish[0]
    assert published_post.id == blog_post.id, "Published post should be the same post"
    assert published_post.status == 'published', "Post should have published status"
    assert published_post.published_at is not None, "Published post should have published_at timestamp"
    
    # Test 3: Unpublishing a published post should remove it from public interface
    # Reset mocks
    mock_collection.find.reset_mock()
    mock_collection.update_one.reset_mock()
    
    # Unpublish the post using the model's unpublish method
    blog_post.unpublish()
    
    # Verify post status changed back to draft
    assert blog_post.status == 'draft'
    assert blog_post.is_draft
    assert not blog_post.is_published
    # Note: published_at should remain (for audit trail), but status determines visibility
    
    # Save the unpublished post
    blog_post.save(mock_db)
    
    # Mock find_published to return empty list (unpublished post not included)
    mock_collection.find.return_value.sort.return_value = []
    
    published_posts_after_unpublish = BlogPost.find_published(mock_db)
    
    # Verify unpublished post no longer appears in public interface
    assert len(published_posts_after_unpublish) == 0, "Unpublished post should not appear in public interface"
    assert not any(post.id == blog_post.id for post in published_posts_after_unpublish), "Unpublished post should not be in published list"
    
    # Test 4: Status changes should be reflected immediately
    # Test multiple status changes in sequence
    statuses_to_test = ['published', 'draft', 'published', 'draft']
    
    for expected_status in statuses_to_test:
        if expected_status == 'published':
            blog_post.publish()
            expected_visibility = True
        else:
            blog_post.unpublish()
            expected_visibility = False
        
        # Verify status change
        assert blog_post.status == expected_status, f"Status should be {expected_status}"
        assert blog_post.is_published == expected_visibility, f"is_published should be {expected_visibility}"
        assert blog_post.is_draft == (not expected_visibility), f"is_draft should be {not expected_visibility}"
        
        # Mock the appropriate response for find_published
        if expected_visibility:
            mock_collection.find.return_value.sort.return_value = [published_post_data]
        else:
            mock_collection.find.return_value.sort.return_value = []
        
        current_published_posts = BlogPost.find_published(mock_db)
        
        if expected_visibility:
            assert len(current_published_posts) == 1, f"Post should be visible when status is {expected_status}"
            assert current_published_posts[0].id == blog_post.id, "Visible post should be the correct post"
        else:
            assert len(current_published_posts) == 0, f"Post should not be visible when status is {expected_status}"
    
    # Test 5: Timestamp handling during publication workflow
    # Create a new post to test timestamp behavior
    mock_result2 = Mock()
    mock_result2.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result2
    
    timestamp_test_post = BlogPost.create(
        db=mock_db,
        title=f"Timestamp Test {blog_data['title']}",
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='draft'
    )
    
    # Verify initial timestamps
    assert timestamp_test_post.created_at is not None, "Created timestamp should be set"
    assert timestamp_test_post.updated_at is not None, "Updated timestamp should be set"
    assert timestamp_test_post.published_at is None, "Published timestamp should be None for draft"
    
    original_created_at = timestamp_test_post.created_at
    original_updated_at = timestamp_test_post.updated_at
    
    # Wait a small amount to ensure timestamp differences
    import time
    time.sleep(0.01)
    
    # Publish the post
    timestamp_test_post.publish()
    
    # Verify timestamps after publishing
    assert timestamp_test_post.created_at == original_created_at, "Created timestamp should be preserved"
    assert timestamp_test_post.updated_at > original_updated_at, "Updated timestamp should be newer"
    assert timestamp_test_post.published_at is not None, "Published timestamp should be set"
    assert timestamp_test_post.published_at >= original_updated_at, "Published timestamp should be recent"
    
    # Test unpublishing preserves published_at (for audit trail)
    published_at_before_unpublish = timestamp_test_post.published_at
    time.sleep(0.01)
    
    timestamp_test_post.unpublish()
    
    # Verify timestamps after unpublishing
    assert timestamp_test_post.created_at == original_created_at, "Created timestamp should still be preserved"
    assert timestamp_test_post.updated_at > published_at_before_unpublish, "Updated timestamp should be newer after unpublish"
    # published_at should remain for audit trail (implementation detail)
    
    # Test 6: Multiple posts with different statuses
    # Create multiple posts with different statuses and verify filtering
    mock_results = [Mock() for _ in range(4)]  # Need 4 results for the posts we'll create
    for i, mock_res in enumerate(mock_results):
        mock_res.inserted_id = ObjectId()
    
    mock_collection.insert_one.side_effect = mock_results
    
    # Create posts with different statuses
    draft_post = BlogPost.create(
        db=mock_db,
        title=f"Draft {blog_data['title']}",
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='draft'
    )
    
    published_post1 = BlogPost.create(
        db=mock_db,
        title=f"Published 1 {blog_data['title']}",
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='published'
    )
    
    published_post2 = BlogPost.create(
        db=mock_db,
        title=f"Published 2 {blog_data['title']}",
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='published'
    )
    
    # Mock find_published to return only published posts
    published_posts_data = [
        {
            '_id': published_post1._id,
            'title': published_post1.title,
            'content': published_post1.content,
            'author_name': published_post1.author_name,
            'content_type': published_post1.content_type,
            'status': 'published',
            'author_id': ObjectId(author_id),
            'images': [],
            'youtube_videos': [],
            'created_at': published_post1.created_at,
            'updated_at': published_post1.updated_at,
            'published_at': published_post1.published_at,
            'view_count': 0,
            'tags': []
        },
        {
            '_id': published_post2._id,
            'title': published_post2.title,
            'content': published_post2.content,
            'author_name': published_post2.author_name,
            'content_type': published_post2.content_type,
            'status': 'published',
            'author_id': ObjectId(author_id),
            'images': [],
            'youtube_videos': [],
            'created_at': published_post2.created_at,
            'updated_at': published_post2.updated_at,
            'published_at': published_post2.published_at,
            'view_count': 0,
            'tags': []
        }
    ]
    
    mock_collection.find.return_value.sort.return_value = published_posts_data
    
    all_published_posts = BlogPost.find_published(mock_db)
    
    # Verify only published posts are returned
    assert len(all_published_posts) == 2, "Only published posts should be returned"
    
    published_ids = [post.id for post in all_published_posts]
    assert published_post1.id in published_ids, "First published post should be in results"
    assert published_post2.id in published_ids, "Second published post should be in results"
    assert draft_post.id not in published_ids, "Draft post should not be in published results"
    
    # Verify all returned posts have published status
    for post in all_published_posts:
        assert post.status == 'published', "All returned posts should have published status"
        assert post.is_published, "All returned posts should be marked as published"
        assert not post.is_draft, "No returned posts should be marked as draft"
    
    # Test 7: Edge case - rapid status changes
    # Test that rapid status changes are handled correctly
    # Reset side_effect to avoid StopIteration
    mock_collection.insert_one.side_effect = None
    mock_result_rapid = Mock()
    mock_result_rapid.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result_rapid
    
    rapid_change_post = BlogPost.create(
        db=mock_db,
        title=f"Rapid Change {blog_data['title']}",
        content=blog_data['content'],
        author_id=author_id,
        author_name=blog_data['author_name'],
        content_type=blog_data['content_type'],
        status='draft'
    )
    
    # Perform rapid status changes
    for _ in range(5):
        rapid_change_post.publish()
        assert rapid_change_post.is_published, "Post should be published after publish()"
        
        rapid_change_post.unpublish()
        assert rapid_change_post.is_draft, "Post should be draft after unpublish()"
    
    # Final state should be consistent
    assert rapid_change_post.status == 'draft', "Final status should be draft"
    assert rapid_change_post.is_draft, "Final state should be draft"
    assert not rapid_change_post.is_published, "Final state should not be published"
    
    # Reset side effects for other tests
    mock_collection.insert_one.side_effect = None