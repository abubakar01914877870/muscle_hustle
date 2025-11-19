"""
Property-based tests for YouTube Service
"""
import re
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
import pytest

from src.services.youtube_service import YouTubeService


@composite
def youtube_url_strategy(draw):
    """Generate valid YouTube URLs for testing"""
    # Generate a valid 11-character video ID
    video_id = ''.join(draw(st.lists(
        st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'),
        min_size=11,
        max_size=11
    )))
    
    # Choose URL format
    url_formats = [
        f"https://www.youtube.com/watch?v={video_id}",
        f"https://youtube.com/watch?v={video_id}",
        f"http://www.youtube.com/watch?v={video_id}",
        f"www.youtube.com/watch?v={video_id}",
        f"youtube.com/watch?v={video_id}",
        f"https://youtu.be/{video_id}",
        f"http://youtu.be/{video_id}",
        f"youtu.be/{video_id}",
        f"https://www.youtube.com/embed/{video_id}",
        f"https://youtube.com/embed/{video_id}",
        f"https://www.youtube.com/v/{video_id}",
    ]
    
    url_format = draw(st.sampled_from(url_formats))
    return url_format, video_id


@composite
def invalid_youtube_url_strategy(draw):
    """Generate invalid YouTube URLs for testing"""
    invalid_urls = [
        "",  # Empty string
        "   ",  # Whitespace only
        "not a url",  # Not a URL
        "https://www.google.com",  # Different domain
        "https://www.youtube.com/watch",  # Missing video ID
        "https://www.youtube.com/watch?v=",  # Empty video ID
        "https://www.youtube.com/watch?v=invalid",  # Invalid video ID (too short)
        "https://www.youtube.com/watch?v=toolongvideoid123",  # Invalid video ID (too long)
        "https://www.youtube.com/watch?v=invalid@#$",  # Invalid characters
        "https://youtu.be/",  # Missing video ID
        "https://youtu.be/invalid",  # Invalid video ID
        "https://vimeo.com/123456789",  # Different video platform
    ]
    
    return draw(st.sampled_from(invalid_urls))


@composite
def video_id_strategy(draw):
    """Generate valid YouTube video IDs"""
    return ''.join(draw(st.lists(
        st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'),
        min_size=11,
        max_size=11
    )))


class TestYouTubeService:
    """Test YouTube Service functionality"""
    
    def test_validate_empty_url(self):
        """Test validation with empty URL"""
        is_valid, video_id, error = YouTubeService.validate_youtube_url("")
        assert not is_valid
        assert video_id is None
        assert "URL cannot be empty" in error
    
    def test_validate_none_url(self):
        """Test validation with None URL"""
        is_valid, video_id, error = YouTubeService.validate_youtube_url(None)
        assert not is_valid
        assert video_id is None
        assert "URL is required and must be a string" in error
    
    def test_generate_embed_with_invalid_video_id(self):
        """Test embed generation with invalid video ID"""
        success, embed_code, error = YouTubeService.generate_embed_code("invalid")
        assert not success
        assert embed_code is None
        assert "Invalid video ID format" in error
    
    def test_generate_embed_with_none_video_id(self):
        """Test embed generation with None video ID"""
        success, embed_code, error = YouTubeService.generate_embed_code(None)
        assert not success
        assert embed_code is None
        assert "Video ID is required and must be a string" in error


# **Feature: blog-system, Property 6: YouTube URL processing**
# **Validates: Requirements 2.4, 6.5**
@given(url_and_id=youtube_url_strategy())
@settings(max_examples=100, deadline=None)
def test_youtube_url_processing_property(url_and_id):
    """
    Property: For any valid YouTube URL provided by an admin, the system should 
    extract the video ID, validate the URL format, and generate proper responsive 
    iframe embed code
    """
    url, expected_video_id = url_and_id
    
    # Test URL validation and video ID extraction
    is_valid, extracted_video_id, error = YouTubeService.validate_youtube_url(url)
    
    # Verify URL is recognized as valid
    assert is_valid, f"Valid YouTube URL was rejected: {url}, error: {error}"
    assert error is None
    assert extracted_video_id == expected_video_id
    
    # Test embed code generation
    success, embed_code, embed_error = YouTubeService.generate_embed_code(extracted_video_id)
    
    # Verify embed code generation succeeds
    assert success, f"Embed code generation failed for video ID {extracted_video_id}: {embed_error}"
    assert embed_error is None
    assert embed_code is not None
    
    # Verify embed code structure
    assert f"https://www.youtube.com/embed/{extracted_video_id}" in embed_code
    assert "<iframe" in embed_code
    assert "</iframe>" in embed_code
    assert "youtube-embed-container" in embed_code
    
    # Verify responsive design elements
    assert "position: relative" in embed_code
    assert "padding-bottom: 56.25%" in embed_code  # 16:9 aspect ratio
    assert "width: 100%" in embed_code
    assert "height: 100%" in embed_code
    
    # Verify security and accessibility attributes
    assert 'allowfullscreen' in embed_code
    assert 'loading="lazy"' in embed_code
    assert 'frameborder="0"' in embed_code
    
    # Test metadata extraction
    meta_success, metadata, meta_error = YouTubeService.extract_video_metadata(extracted_video_id)
    
    # Verify metadata extraction succeeds
    assert meta_success, f"Metadata extraction failed for video ID {extracted_video_id}: {meta_error}"
    assert meta_error is None
    assert metadata is not None
    
    # Verify metadata structure
    required_metadata_fields = ['video_id', 'video_url', 'thumbnail_url', 'embed_url']
    for field in required_metadata_fields:
        assert field in metadata, f"Missing required metadata field: {field}"
    
    # Verify metadata content
    assert metadata['video_id'] == extracted_video_id
    assert f"watch?v={extracted_video_id}" in metadata['video_url']
    assert f"vi/{extracted_video_id}" in metadata['thumbnail_url']
    assert f"embed/{extracted_video_id}" in metadata['embed_url']
    
    # Test complete processing workflow
    process_success, video_data, process_error = YouTubeService.process_youtube_url(url)
    
    # Verify complete processing succeeds
    assert process_success, f"Complete processing failed for URL {url}: {process_error}"
    assert process_error is None
    assert video_data is not None
    
    # Verify complete processing data structure
    required_data_fields = ['video_id', 'url', 'embed_code', 'metadata']
    for field in required_data_fields:
        assert field in video_data, f"Missing required data field: {field}"
    
    # Verify data consistency
    assert video_data['video_id'] == extracted_video_id
    assert video_data['url'] == url
    assert video_data['embed_code'] == embed_code
    assert video_data['metadata'] == metadata


@given(invalid_url=invalid_youtube_url_strategy())
@settings(max_examples=50, deadline=None)
def test_youtube_invalid_url_rejection_property(invalid_url):
    """
    Property: For any invalid YouTube URL, the system should reject it gracefully 
    with appropriate error messages
    """
    is_valid, video_id, error = YouTubeService.validate_youtube_url(invalid_url)
    
    # Verify invalid URLs are rejected
    assert not is_valid, f"Invalid URL was accepted: {invalid_url}"
    assert video_id is None
    assert error is not None
    assert len(error) > 0
    
    # Verify error message is informative
    expected_error_patterns = [
        "URL is required",
        "URL cannot be empty",
        "Invalid YouTube URL format"
    ]
    
    assert any(pattern in error for pattern in expected_error_patterns), \
        f"Error message not informative enough: {error}"


@given(video_id=video_id_strategy())
@settings(max_examples=100, deadline=None)
def test_embed_code_generation_property(video_id):
    """
    Property: For any valid video ID, the system should generate proper embed code
    """
    success, embed_code, error = YouTubeService.generate_embed_code(video_id)
    
    # Verify embed generation succeeds
    assert success, f"Embed generation failed for valid video ID {video_id}: {error}"
    assert error is None
    assert embed_code is not None
    
    # Verify embed code contains required elements
    assert f"https://www.youtube.com/embed/{video_id}" in embed_code
    assert "<iframe" in embed_code
    assert "</iframe>" in embed_code
    
    # Verify responsive container
    assert "youtube-embed-container" in embed_code
    assert "position: relative" in embed_code
    assert "padding-bottom: 56.25%" in embed_code
    
    # Verify iframe attributes
    assert 'width="560"' in embed_code
    assert 'height="315"' in embed_code
    assert 'frameborder="0"' in embed_code
    assert 'allowfullscreen' in embed_code
    assert 'loading="lazy"' in embed_code
    
    # Verify security attributes
    assert 'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"' in embed_code


@given(video_id=video_id_strategy())
@settings(max_examples=100, deadline=None)
def test_metadata_extraction_property(video_id):
    """
    Property: For any valid video ID, the system should extract consistent metadata
    """
    success, metadata, error = YouTubeService.extract_video_metadata(video_id)
    
    # Verify metadata extraction succeeds
    assert success, f"Metadata extraction failed for valid video ID {video_id}: {error}"
    assert error is None
    assert metadata is not None
    
    # Verify all required fields are present
    required_fields = ['video_id', 'video_url', 'thumbnail_url', 'thumbnail_medium', 'thumbnail_small', 'embed_url']
    for field in required_fields:
        assert field in metadata, f"Missing required metadata field: {field}"
    
    # Verify field values are consistent with video ID
    assert metadata['video_id'] == video_id
    assert f"watch?v={video_id}" in metadata['video_url']
    assert f"vi/{video_id}/maxresdefault.jpg" in metadata['thumbnail_url']
    assert f"vi/{video_id}/mqdefault.jpg" in metadata['thumbnail_medium']
    assert f"vi/{video_id}/default.jpg" in metadata['thumbnail_small']
    assert f"embed/{video_id}" in metadata['embed_url']
    
    # Verify URLs are properly formatted
    assert metadata['video_url'].startswith('https://www.youtube.com/')
    assert metadata['thumbnail_url'].startswith('https://img.youtube.com/')
    assert metadata['embed_url'].startswith('https://www.youtube.com/')