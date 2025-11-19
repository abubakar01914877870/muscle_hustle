"""
Property-based tests for Firebase Service
"""
import os
import io
import tempfile
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
import pytest
from werkzeug.datastructures import FileStorage

from src.services.firebase_service import FirebaseService


@composite
def file_storage_strategy(draw):
    """Generate FileStorage objects for testing"""
    # Generate file content
    content_size = draw(st.integers(min_value=100, max_value=10000))
    content = draw(st.binary(min_size=content_size, max_size=content_size))
    
    # Generate filename with valid extension
    extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp']
    extension = draw(st.sampled_from(extensions))
    filename = f"test_image_{draw(st.integers(min_value=1, max_value=9999))}.{extension}"
    
    # Create FileStorage object
    file_obj = io.BytesIO(content)
    return FileStorage(
        stream=file_obj,
        filename=filename,
        content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}"
    )


class TestFirebaseService:
    """Test Firebase Service functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Reset Firebase service state
        FirebaseService._app = None
        FirebaseService._bucket = None
    
    def test_firebase_not_available_when_not_initialized(self):
        """Test that Firebase is not available when not initialized"""
        assert not FirebaseService.is_available()
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.storage.bucket')
    @patch('firebase_admin.credentials.Certificate')
    @patch('os.path.exists')
    def test_initialization_success(self, mock_exists, mock_cert, mock_bucket, mock_init):
        """Test successful Firebase initialization"""
        # Mock successful initialization
        mock_exists.return_value = True
        mock_app = Mock()
        mock_init.return_value = mock_app
        mock_bucket_instance = Mock()
        mock_bucket.return_value = mock_bucket_instance
        
        # Mock Flask app config
        mock_app_config = Mock()
        mock_app_config.config = {
            'FIREBASE_CREDENTIALS_PATH': '/path/to/creds.json',
            'FIREBASE_STORAGE_BUCKET': 'test-bucket'
        }
        
        with patch('src.services.firebase_service.current_app', mock_app_config):
            FirebaseService.initialize()
            
        assert FirebaseService.is_available()
        assert FirebaseService._bucket == mock_bucket_instance
    
    def test_upload_without_firebase_available(self):
        """Test upload when Firebase is not available"""
        file_obj = FileStorage(
            stream=io.BytesIO(b"test content"),
            filename="test.jpg",
            content_type="image/jpeg"
        )
        
        success, data, error = FirebaseService.upload_image(file_obj)
        
        assert not success
        assert data is None
        assert "Image upload service is currently unavailable" in error
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.storage.bucket')
    @patch('firebase_admin.credentials.Certificate')
    @patch('os.path.exists')
    def test_upload_invalid_file_type(self, mock_exists, mock_cert, mock_bucket, mock_init):
        """Test upload with invalid file type"""
        # Setup mocks for initialization
        mock_exists.return_value = True
        mock_app = Mock()
        mock_init.return_value = mock_app
        mock_bucket_instance = Mock()
        mock_bucket.return_value = mock_bucket_instance
        
        # Initialize Firebase service
        mock_app_config = Mock()
        mock_app_config.config = {
            'FIREBASE_CREDENTIALS_PATH': '/path/to/creds.json',
            'FIREBASE_STORAGE_BUCKET': 'test-bucket'
        }
        
        with patch('src.services.firebase_service.current_app', mock_app_config):
            FirebaseService.initialize()
        
        # Test invalid file type
        file_obj = FileStorage(
            stream=io.BytesIO(b"test content"),
            filename="test.txt",
            content_type="text/plain"
        )
        
        success, data, error = FirebaseService.upload_image(file_obj)
        
        assert not success
        assert data is None
        assert "File type 'txt' not allowed" in error


# **Feature: blog-system, Property 5: Image upload round-trip**
# **Validates: Requirements 2.3, 6.2**
@patch('src.services.firebase_service.firebase_admin.initialize_app')
@patch('src.services.firebase_service.storage.bucket')
@patch('src.services.firebase_service.credentials.Certificate')
@patch('src.services.firebase_service.os.path.exists')
@given(file_storage=file_storage_strategy())
@settings(max_examples=100, deadline=None)
def test_firebase_image_upload_round_trip(mock_exists, mock_cert, mock_bucket, mock_init, file_storage):
    """
    Property: For any valid image file uploaded by an admin, the system should 
    successfully upload to Firebase Storage, store the download URL in MongoDB, 
    and make the image accessible via the stored URL
    """
    # Reset Firebase service state
    FirebaseService._app = None
    FirebaseService._bucket = None
    
    # Setup mocks for successful Firebase initialization
    mock_exists.return_value = True
    mock_app = Mock()
    mock_init.return_value = mock_app
    mock_bucket_instance = Mock()
    mock_bucket.return_value = mock_bucket_instance
    
    # Mock blob operations
    mock_blob = Mock()
    mock_bucket_instance.blob.return_value = mock_blob
    mock_blob.public_url = f"https://storage.googleapis.com/test-bucket/blog-images/test_file.jpg"
    
    # Initialize Firebase service with mocked current_app
    mock_app_config = Mock()
    mock_app_config.config = {
        'FIREBASE_CREDENTIALS_PATH': '/path/to/creds.json',
        'FIREBASE_STORAGE_BUCKET': 'test-bucket'
    }
    
    with patch('src.services.firebase_service.current_app', mock_app_config):
        FirebaseService.initialize()
    
    # Test the upload with mocked validation
    with patch('src.services.firebase_service.validate_file_upload', return_value=(True, None)):
        success, image_data, error = FirebaseService.upload_image(file_storage)
    
    # Verify upload success
    assert success, f"Upload failed: {error}"
    assert error is None
    assert image_data is not None
    
    # Verify image data structure
    required_fields = ['firebase_path', 'download_url', 'filename', 'size', 'content_type']
    for field in required_fields:
        assert field in image_data, f"Missing required field: {field}"
    
    # Verify firebase_path format
    assert image_data['firebase_path'].startswith('blog-images/')
    assert image_data['firebase_path'].endswith(file_storage.filename.split('.')[-1])
    
    # Verify download_url is a valid URL
    assert image_data['download_url'].startswith('https://')
    assert 'storage.googleapis.com' in image_data['download_url']
    
    # Verify filename matches original
    assert image_data['filename'] == file_storage.filename
    
    # Verify content type is preserved
    assert image_data['content_type'] == file_storage.content_type
    
    # Verify size is positive
    assert image_data['size'] > 0
    
    # Verify Firebase operations were called correctly
    mock_bucket_instance.blob.assert_called_once()
    mock_blob.upload_from_file.assert_called_once()
    mock_blob.make_public.assert_called_once()
    
    # Test round-trip: verify we can get the download URL back
    firebase_path = image_data['firebase_path']
    
    # Mock the blob for get_download_url test
    mock_blob_get = Mock()
    mock_blob_get.exists.return_value = True
    mock_blob_get.public_url = image_data['download_url']
    mock_bucket_instance.blob.return_value = mock_blob_get
    
    success_url, download_url, error_url = FirebaseService.get_download_url(firebase_path)
    
    assert success_url, f"Failed to get download URL: {error_url}"
    assert download_url == image_data['download_url']
    assert error_url is None