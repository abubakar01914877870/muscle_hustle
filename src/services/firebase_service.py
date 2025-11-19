"""
Firebase Storage Service for Blog System
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import firebase_admin
from firebase_admin import credentials, storage
from werkzeug.datastructures import FileStorage
from flask import current_app
from ..utils.security import validate_file_upload


class FirebaseService:
    """Service for handling Firebase Storage operations"""
    
    _app = None
    _bucket = None
    
    @classmethod
    def initialize(cls, app=None):
        """Initialize Firebase Admin SDK"""
        if cls._app is not None:
            return  # Already initialized
            
        try:
            # Get credentials path from config
            creds_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH') if app is None else app.config.get('FIREBASE_CREDENTIALS_PATH')
            bucket_name = current_app.config.get('FIREBASE_STORAGE_BUCKET') if app is None else app.config.get('FIREBASE_STORAGE_BUCKET')
            
            if not creds_path or not bucket_name:
                raise ValueError("Firebase credentials path and storage bucket must be configured")
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Firebase credentials file not found: {creds_path}")
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(creds_path)
            cls._app = firebase_admin.initialize_app(cred, {
                'storageBucket': bucket_name
            })
            
            # Get storage bucket
            cls._bucket = storage.bucket()
            
        except Exception as e:
            print(f"Warning: Firebase initialization failed: {str(e)}")
            print("Blog image uploads will not be available")
            cls._app = None
            cls._bucket = None
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Firebase service is available"""
        return cls._bucket is not None
    
    @classmethod
    def upload_image(cls, file: FileStorage, path_prefix: str = "blog-images") -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Upload image to Firebase Storage with comprehensive security validation and error handling
        
        Args:
            file: FileStorage object from Flask request
            path_prefix: Prefix for the storage path
            
        Returns:
            Tuple of (success, image_data, error_message)
            image_data contains: firebase_path, download_url, filename, size
        """
        if not cls.is_available():
            return False, None, "Image upload service is currently unavailable. Please try again later."
        
        try:
            # Comprehensive file validation using security utilities
            is_valid, validation_error = validate_file_upload(file)
            if not is_valid:
                return False, None, f"File validation failed: {validation_error}"
            
            # Generate unique filename with secure naming
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{timestamp}_{unique_id}.{file_ext}"
            firebase_path = f"{path_prefix}/{filename}"
            
            # Upload to Firebase Storage with timeout and retry logic
            blob = cls._bucket.blob(firebase_path)
            file.seek(0)  # Reset file pointer
            
            try:
                blob.upload_from_file(file, content_type=file.content_type, timeout=30)
            except Exception as upload_error:
                # Handle specific upload errors
                error_str = str(upload_error).lower()
                if 'timeout' in error_str:
                    return False, None, "Upload timed out. Please check your connection and try again."
                elif 'permission' in error_str or 'forbidden' in error_str:
                    return False, None, "Upload permission denied. Please contact support."
                elif 'quota' in error_str or 'limit' in error_str:
                    return False, None, "Storage quota exceeded. Please try again later."
                else:
                    return False, None, f"Upload failed: {str(upload_error)}"
            
            # Make the blob publicly readable with error handling
            try:
                blob.make_public()
            except Exception as public_error:
                # Log the error but continue - the file was uploaded
                print(f"Warning: Failed to make blob public: {str(public_error)}")
                # Try to get a signed URL instead
                try:
                    from datetime import timedelta
                    download_url = blob.generate_signed_url(timedelta(days=365))
                except Exception:
                    return False, None, "Upload succeeded but failed to generate access URL. Please try again."
            else:
                # Get download URL
                download_url = blob.public_url
            
            # Get file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset
            
            image_data = {
                'firebase_path': firebase_path,
                'download_url': download_url,
                'filename': file.filename,
                'size': file_size,
                'content_type': file.content_type
            }
            
            return True, image_data, None
            
        except ImportError as e:
            return False, None, "Firebase service dependencies are not properly installed."
        except ConnectionError as e:
            return False, None, "Network connection error. Please check your internet connection and try again."
        except Exception as e:
            error_str = str(e).lower()
            if 'authentication' in error_str or 'credential' in error_str:
                return False, None, "Authentication error with storage service. Please contact support."
            elif 'network' in error_str or 'connection' in error_str:
                return False, None, "Network error occurred during upload. Please try again."
            else:
                return False, None, f"An unexpected error occurred during upload: {str(e)}"
    
    @classmethod
    def delete_image(cls, firebase_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete image from Firebase Storage with enhanced error handling
        
        Args:
            firebase_path: Path to the file in Firebase Storage
            
        Returns:
            Tuple of (success, error_message)
        """
        if not cls.is_available():
            return False, "Image deletion service is currently unavailable"
        
        if not firebase_path or not isinstance(firebase_path, str):
            return False, "Invalid file path provided"
        
        try:
            blob = cls._bucket.blob(firebase_path)
            
            # Check if file exists before attempting deletion
            try:
                if blob.exists():
                    blob.delete(timeout=30)
                    return True, None
                else:
                    # File doesn't exist - this is not necessarily an error
                    return True, None  # Consider it successful since the end result is the same
            except Exception as delete_error:
                error_str = str(delete_error).lower()
                if 'timeout' in error_str:
                    return False, "Delete operation timed out. Please try again."
                elif 'permission' in error_str or 'forbidden' in error_str:
                    return False, "Permission denied for file deletion."
                elif 'not found' in error_str:
                    return True, None  # File already gone
                else:
                    return False, f"Failed to delete file: {str(delete_error)}"
                
        except ConnectionError as e:
            return False, "Network connection error during file deletion."
        except Exception as e:
            error_str = str(e).lower()
            if 'authentication' in error_str or 'credential' in error_str:
                return False, "Authentication error with storage service."
            else:
                return False, f"Unexpected error during file deletion: {str(e)}"
    
    @classmethod
    def get_download_url(cls, firebase_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get fresh download URL for existing file
        
        Args:
            firebase_path: Path to the file in Firebase Storage
            
        Returns:
            Tuple of (success, download_url, error_message)
        """
        if not cls.is_available():
            return False, None, "Firebase Storage is not available"
        
        try:
            blob = cls._bucket.blob(firebase_path)
            if blob.exists():
                # Refresh the blob to get current public URL
                blob.reload()
                return True, blob.public_url, None
            else:
                return False, None, "File not found"
                
        except Exception as e:
            return False, None, f"URL generation failed: {str(e)}"