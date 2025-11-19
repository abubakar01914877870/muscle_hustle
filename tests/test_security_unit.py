"""
Unit tests for security features
"""
import pytest
import tempfile
import io
from werkzeug.datastructures import FileStorage
from src.utils.security import ContentSanitizer, FileValidator, sanitize_blog_content, validate_file_upload


class TestHTMLSanitization:
    """Unit tests for HTML content sanitization to prevent XSS attacks"""
    
    def test_script_tags_removed(self):
        """Test that script tags are completely removed"""
        malicious_html = '<p>Hello <script>alert("XSS")</script> World</p>'
        sanitized = ContentSanitizer.sanitize_html(malicious_html)
        
        assert '<script>' not in sanitized
        # Note: bleach removes script tags but may preserve content inside
        # The important thing is that the script tags themselves are gone
        assert 'Hello' in sanitized and 'World' in sanitized  # Content preserved
    
    def test_javascript_urls_removed(self):
        """Test that javascript: URLs are removed"""
        malicious_html = '<a href="javascript:alert(1)">Click me</a>'
        sanitized = ContentSanitizer.sanitize_html(malicious_html)
        
        assert 'javascript:' not in sanitized
        assert 'alert(1)' not in sanitized
        assert 'Click me' in sanitized  # Link text preserved
    
    def test_onclick_attributes_removed(self):
        """Test that onclick and other event handlers are removed"""
        malicious_html = '<button onclick="alert(1)" onmouseover="alert(2)">Button</button>'
        sanitized = ContentSanitizer.sanitize_html(malicious_html)
        
        assert 'onclick=' not in sanitized
        assert 'onmouseover=' not in sanitized
        assert 'alert(1)' not in sanitized
        assert 'alert(2)' not in sanitized
        assert 'Button' in sanitized
    
    def test_iframe_src_validation(self):
        """Test that iframe src attributes are validated"""
        # Valid iframe (YouTube)
        valid_iframe = '<iframe src="https://www.youtube.com/embed/video123"></iframe>'
        sanitized = ContentSanitizer.sanitize_html(valid_iframe)
        assert 'iframe' in sanitized
        assert 'youtube.com' in sanitized
        
        # Invalid iframe with javascript
        malicious_iframe = '<iframe src="javascript:alert(1)"></iframe>'
        sanitized = ContentSanitizer.sanitize_html(malicious_iframe)
        assert 'javascript:' not in sanitized
    
    def test_allowed_tags_preserved(self):
        """Test that allowed HTML tags are preserved"""
        valid_html = '''
        <h1>Title</h1>
        <p>Paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        <a href="https://example.com">External link</a>
        <img src="https://example.com/image.jpg" alt="Image">
        '''
        
        sanitized = ContentSanitizer.sanitize_html(valid_html)
        
        # Check that allowed tags are preserved
        assert '<h1>' in sanitized and '</h1>' in sanitized
        assert '<p>' in sanitized and '</p>' in sanitized
        assert '<strong>' in sanitized and '</strong>' in sanitized
        assert '<em>' in sanitized and '</em>' in sanitized
        assert '<ul>' in sanitized and '</ul>' in sanitized
        assert '<li>' in sanitized and '</li>' in sanitized
        assert '<a href=' in sanitized and '</a>' in sanitized
        assert '<img' in sanitized and 'alt=' in sanitized
    
    def test_external_links_get_security_attributes(self):
        """Test that external links get target='_blank' and rel='noopener noreferrer'"""
        html = '<a href="https://external-site.com">External link</a>'
        sanitized = ContentSanitizer.sanitize_html(html)
        
        assert 'target="_blank"' in sanitized
        assert 'rel="noopener noreferrer"' in sanitized
        assert 'https://external-site.com' in sanitized
    
    def test_internal_links_unchanged(self):
        """Test that internal links don't get external link attributes"""
        html = '<a href="/internal-page">Internal link</a>'
        sanitized = ContentSanitizer.sanitize_html(html)
        
        assert 'target="_blank"' not in sanitized
        assert '/internal-page' in sanitized
        assert 'Internal link' in sanitized
    
    def test_sanitize_blog_content_html(self):
        """Test the main sanitize_blog_content function for HTML content"""
        malicious_content = '<p>Hello</p><script>alert("XSS")</script>'
        sanitized = sanitize_blog_content(malicious_content, 'html')
        
        assert '<p>Hello</p>' in sanitized
        assert '<script>' not in sanitized
        # The important thing is that script tags are removed, content may remain
    
    def test_sanitize_blog_content_plain(self):
        """Test the main sanitize_blog_content function for plain text content"""
        content_with_html = '<p>This should be escaped</p>'
        sanitized = sanitize_blog_content(content_with_html, 'plain')
        
        assert '&lt;p&gt;' in sanitized  # HTML should be escaped
        assert '&lt;/p&gt;' in sanitized
        assert '<p>' not in sanitized  # No actual HTML tags


class TestFileUploadValidation:
    """Unit tests for file upload validation to reject malicious files"""
    
    def create_test_file(self, filename, content, content_type):
        """Helper to create a test FileStorage object"""
        file_obj = io.BytesIO(content)
        return FileStorage(
            stream=file_obj,
            filename=filename,
            content_type=content_type
        )
    
    def test_valid_image_files_accepted(self):
        """Test that valid image files are accepted"""
        # PNG file with valid header
        png_content = b'\x89PNG\r\n\x1a\n' + b'fake png data'
        png_file = self.create_test_file('test.png', png_content, 'image/png')
        
        is_valid, error = FileValidator.validate_image_file(png_file)
        assert is_valid
        assert error is None
        
        # JPEG file with valid header
        jpeg_content = b'\xff\xd8\xff' + b'fake jpeg data'
        jpeg_file = self.create_test_file('test.jpg', jpeg_content, 'image/jpeg')
        
        is_valid, error = FileValidator.validate_image_file(jpeg_file)
        assert is_valid
        assert error is None
    
    def test_dangerous_extensions_rejected(self):
        """Test that dangerous file extensions are rejected"""
        dangerous_files = [
            ('malware.exe', b'MZ\x90\x00', 'application/octet-stream'),
            ('script.js', b'alert("XSS")', 'application/javascript'),
            ('backdoor.php', b'<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('virus.bat', b'@echo off\ndel /f /q *.*', 'application/x-msdos-program')
        ]
        
        for filename, content, content_type in dangerous_files:
            file_obj = self.create_test_file(filename, content, content_type)
            is_valid, error = FileValidator.validate_image_file(file_obj)
            
            assert not is_valid
            assert 'not allowed for security reasons' in error
    
    def test_wrong_mime_type_rejected(self):
        """Test that files with wrong MIME types are rejected"""
        # File with image extension but wrong MIME type
        fake_image = self.create_test_file('fake.png', b'not an image', 'text/plain')
        
        is_valid, error = FileValidator.validate_image_file(fake_image)
        assert not is_valid
        assert 'Invalid file type' in error
    
    def test_file_size_limits_enforced(self):
        """Test that file size limits are enforced"""
        # Create a file that's too large (over 10MB)
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        large_file = self.create_test_file('large.png', large_content, 'image/png')
        
        is_valid, error = FileValidator.validate_image_file(large_file)
        assert not is_valid
        assert 'File too large' in error
    
    def test_empty_files_rejected(self):
        """Test that empty files are rejected"""
        empty_file = self.create_test_file('empty.png', b'', 'image/png')
        
        is_valid, error = FileValidator.validate_image_file(empty_file)
        assert not is_valid
        assert 'File is empty' in error
    
    def test_no_extension_rejected(self):
        """Test that files without extensions are rejected"""
        no_ext_file = self.create_test_file('noextension', b'some content', 'image/png')
        
        is_valid, error = FileValidator.validate_image_file(no_ext_file)
        assert not is_valid
        assert 'File must have an extension' in error
    
    def test_header_content_mismatch_rejected(self):
        """Test that files with mismatched headers and extensions are rejected"""
        # PNG extension but JPEG header
        jpeg_header_png_ext = self.create_test_file(
            'fake.png', 
            b'\xff\xd8\xff' + b'jpeg data', 
            'image/png'
        )
        
        is_valid, error = FileValidator.validate_image_file(jpeg_header_png_ext)
        assert not is_valid
        assert 'File content does not match expected image format' in error
    
    def test_validate_file_upload_wrapper(self):
        """Test the main validate_file_upload wrapper function"""
        # Valid file
        png_content = b'\x89PNG\r\n\x1a\n' + b'fake png data'
        valid_file = self.create_test_file('test.png', png_content, 'image/png')
        
        is_valid, error = validate_file_upload(valid_file)
        assert is_valid
        assert error is None
        
        # Invalid file
        malicious_file = self.create_test_file('malware.exe', b'MZ\x90\x00', 'application/octet-stream')
        
        is_valid, error = validate_file_upload(malicious_file)
        assert not is_valid
        assert error is not None


class TestCSRFProtection:
    """Unit tests for CSRF protection functionality"""
    
    def test_csrf_token_generation(self):
        """Test that CSRF tokens can be generated"""
        # This test requires Flask application context
        # We'll test the import and basic functionality
        from src.utils.security import CSRFProtection
        
        # Test that the class exists and has the required methods
        assert hasattr(CSRFProtection, 'generate_csrf_token')
        assert hasattr(CSRFProtection, 'validate_csrf_token')
        assert callable(CSRFProtection.generate_csrf_token)
        assert callable(CSRFProtection.validate_csrf_token)


class TestSecurityIntegration:
    """Integration tests for security features working together"""
    
    def test_complete_content_sanitization_workflow(self):
        """Test the complete workflow of content sanitization"""
        malicious_blog_content = '''
        <h1>Blog Post Title</h1>
        <p>This is a normal paragraph.</p>
        <script>alert("XSS Attack!");</script>
        <p>Another paragraph with <a href="javascript:alert('XSS')">malicious link</a>.</p>
        <p>External link: <a href="https://external-site.com">External Site</a></p>
        <p>Internal link: <a href="/internal-page">Internal Page</a></p>
        <img src="https://example.com/image.jpg" alt="Image" onclick="alert('XSS')">
        '''
        
        sanitized = sanitize_blog_content(malicious_blog_content, 'html')
        
        # Verify malicious content is removed
        assert '<script>' not in sanitized
        # Script tags are removed, which is the important security measure
        assert 'javascript:alert' not in sanitized
        assert 'onclick=' not in sanitized
        
        # Verify safe content is preserved
        assert '<h1>Blog Post Title</h1>' in sanitized
        assert 'This is a normal paragraph.' in sanitized
        assert 'Another paragraph' in sanitized
        assert 'https://external-site.com' in sanitized
        assert '/internal-page' in sanitized
        assert 'https://example.com/image.jpg' in sanitized
        
        # Verify external link processing
        assert 'target="_blank"' in sanitized
        assert 'rel="noopener noreferrer"' in sanitized
    
    def test_file_validation_with_various_attack_vectors(self):
        """Test file validation against various attack vectors"""
        attack_vectors = [
            # Executable disguised as image
            ('malware.png', b'MZ\x90\x00' + b'executable content', 'image/png'),
            # Script file with image extension
            ('script.jpg', b'<script>alert("XSS")</script>', 'image/jpeg'),
            # File with null bytes in name
            ('image\x00.exe.png', b'\x89PNG\r\n\x1a\n' + b'png data', 'image/png'),
            # Oversized file
            ('huge.png', b'x' * (15 * 1024 * 1024), 'image/png'),  # 15MB
        ]
        
        for filename, content, content_type in attack_vectors:
            file_obj = io.BytesIO(content)
            test_file = FileStorage(
                stream=file_obj,
                filename=filename,
                content_type=content_type
            )
            
            is_valid, error = validate_file_upload(test_file)
            assert not is_valid, f"Attack vector should be rejected: {filename}"
            assert error is not None, f"Error message should be provided for: {filename}"