"""
Security utilities for content processing and validation
"""
import re
import bleach
from typing import List, Dict, Any, Optional
from werkzeug.datastructures import FileStorage


class ContentSanitizer:
    """HTML content sanitization for blog posts"""
    
    # Allowed HTML tags for blog content
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'a', 'img', 'div', 'span',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'iframe'
    ]
    
    # Allowed attributes for HTML tags
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen', 'class'],
        'div': ['class'],
        'span': ['class'],
        'p': ['class'],
        'h1': ['class'], 'h2': ['class'], 'h3': ['class'], 'h4': ['class'], 'h5': ['class'], 'h6': ['class'],
        'table': ['class'], 'thead': ['class'], 'tbody': ['class'], 'tr': ['class'], 'th': ['class'], 'td': ['class']
    }
    
    # Allowed protocols for links
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @classmethod
    def sanitize_html(cls, content: str) -> str:
        """
        Sanitize HTML content to prevent XSS attacks while preserving formatting
        
        Args:
            content: Raw HTML content
            
        Returns:
            Sanitized HTML content
        """
        if not content:
            return ""
        
        # First pass: sanitize with bleach
        sanitized = bleach.clean(
            content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            protocols=cls.ALLOWED_PROTOCOLS,
            strip=True
        )
        
        # Second pass: process external links to open in new tabs
        sanitized = cls._process_external_links(sanitized)
        
        return sanitized
    
    @classmethod
    def _process_external_links(cls, content: str) -> str:
        """
        Process external links to add target="_blank" and rel="noopener noreferrer"
        
        Args:
            content: HTML content with links
            
        Returns:
            HTML content with processed external links
        """
        # Pattern to match <a> tags with href attributes
        link_pattern = r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*?)>'
        
        def process_link(match):
            before_href = match.group(1)
            href = match.group(2)
            after_href = match.group(3)
            
            # Check if it's an external link (starts with http/https and not our domain)
            is_external = href.startswith(('http://', 'https://')) and not href.startswith(('http://localhost', 'https://localhost'))
            
            if is_external:
                # Add target="_blank" and rel="noopener noreferrer" for security
                attributes = f'{before_href}href="{href}"{after_href}'
                
                # Check if target is already set
                if 'target=' not in attributes:
                    attributes += ' target="_blank"'
                
                # Check if rel is already set
                if 'rel=' not in attributes:
                    attributes += ' rel="noopener noreferrer"'
                elif 'noopener' not in attributes:
                    # Add noopener to existing rel
                    attributes = re.sub(r'rel=["\']([^"\']*)["\']', r'rel="\1 noopener noreferrer"', attributes)
                
                return f'<a {attributes}>'
            
            return match.group(0)  # Return unchanged for internal links
        
        return re.sub(link_pattern, process_link, content)


class FileValidator:
    """File upload validation and security checks"""
    
    # Allowed image file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Dangerous file extensions that should never be allowed
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 'php', 'py', 'pl', 'sh', 'asp', 'aspx'
    }
    
    # MIME types for allowed image formats
    ALLOWED_MIME_TYPES = {
        'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'
    }
    
    @classmethod
    def validate_image_file(cls, file: FileStorage) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded image file for security
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check for suspicious filename patterns
        if '\x00' in file.filename or any(ord(c) < 32 for c in file.filename):
            return False, "Filename contains invalid characters"
        
        # Check file extension
        file_ext = cls._get_file_extension(file.filename)
        if not file_ext:
            return False, "File must have an extension"
        
        if file_ext in cls.DANGEROUS_EXTENSIONS:
            return False, f"File type '{file_ext}' is not allowed for security reasons"
        
        if file_ext not in cls.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"File type '{file_ext}' not allowed. Allowed types: {', '.join(cls.ALLOWED_IMAGE_EXTENSIONS)}"
        
        # Check MIME type
        if file.content_type not in cls.ALLOWED_MIME_TYPES:
            return False, f"Invalid file type. Expected image file, got '{file.content_type}'"
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Basic content validation - check if file starts with valid image headers
        file.seek(0)
        header = file.read(16)
        file.seek(0)
        
        if not cls._is_valid_image_header(header, file_ext):
            return False, "File content does not match expected image format"
        
        return True, None
    
    @classmethod
    def _get_file_extension(cls, filename: str) -> Optional[str]:
        """Extract file extension from filename, handling security issues"""
        if not filename or '.' not in filename:
            return None
        
        # Remove null bytes and other control characters for security
        clean_filename = ''.join(c for c in filename if ord(c) >= 32)
        
        if '.' not in clean_filename:
            return None
            
        return clean_filename.rsplit('.', 1)[1].lower()
    
    @classmethod
    def _is_valid_image_header(cls, header: bytes, extension: str) -> bool:
        """
        Check if file header matches expected image format
        
        Args:
            header: First 16 bytes of file
            extension: File extension
            
        Returns:
            True if header matches expected format
        """
        if not header:
            return False
        
        # PNG signature
        if extension == 'png':
            return header.startswith(b'\x89PNG\r\n\x1a\n')
        
        # JPEG signature
        elif extension in ('jpg', 'jpeg'):
            return header.startswith(b'\xff\xd8\xff')
        
        # GIF signature
        elif extension == 'gif':
            return header.startswith(b'GIF87a') or header.startswith(b'GIF89a')
        
        # WebP signature
        elif extension == 'webp':
            return header.startswith(b'RIFF') and b'WEBP' in header[:16]
        
        return False


class CSRFProtection:
    """CSRF protection utilities"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token for forms"""
        from flask_wtf.csrf import generate_csrf
        return generate_csrf()
    
    @staticmethod
    def validate_csrf_token(token: str) -> bool:
        """Validate CSRF token"""
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(token)
            return True
        except Exception:
            return False


def sanitize_blog_content(content: str, content_type: str = 'html') -> str:
    """
    Sanitize blog post content based on content type
    
    Args:
        content: Raw content
        content_type: 'html' or 'plain'
        
    Returns:
        Sanitized content
    """
    if not content:
        return ""
    
    if content_type == 'html':
        return ContentSanitizer.sanitize_html(content)
    else:
        # For plain text, just escape HTML characters
        import html
        return html.escape(content)


def validate_file_upload(file: FileStorage) -> tuple[bool, Optional[str]]:
    """
    Validate file upload for security
    
    Args:
        file: FileStorage object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return FileValidator.validate_image_file(file)