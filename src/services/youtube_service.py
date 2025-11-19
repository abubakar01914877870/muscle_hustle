"""
YouTube Video Processing Service for Blog System
"""
import re
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs


class YouTubeService:
    """Service for handling YouTube video processing and embedding"""
    
    # YouTube URL patterns - capture exactly 11 characters for video ID
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&|$)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:/|$)',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?|$)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})(?:\?|&|$)',
    ]
    
    @classmethod
    def validate_youtube_url(cls, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate YouTube URL and extract video ID
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            Tuple of (is_valid, video_id, error_message)
        """
        if not isinstance(url, str):
            return False, None, "URL is required and must be a string"
        
        url = url.strip()
        if not url:
            return False, None, "URL cannot be empty"
        
        # Try each pattern to extract video ID
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Validate video ID format (exactly 11 characters, alphanumeric + _ -)
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id):
                    return True, video_id, None
        
        return False, None, "Invalid YouTube URL format"
    
    @classmethod
    def generate_embed_code(cls, video_id: str, options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate responsive iframe embed code for YouTube video
        
        Args:
            video_id: YouTube video ID (11 characters)
            options: Optional parameters for embed (width, height, autoplay, etc.)
            
        Returns:
            Tuple of (success, embed_code, error_message)
        """
        if not video_id or not isinstance(video_id, str):
            return False, None, "Video ID is required and must be a string"
        
        # Validate video ID format
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            return False, None, "Invalid video ID format"
        
        try:
            # Default options
            default_options = {
                'width': '560',
                'height': '315',
                'frameborder': '0',
                'allowfullscreen': True,
                'allow': 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
                'loading': 'lazy'
            }
            
            # Merge with provided options
            if options:
                default_options.update(options)
            
            # Build embed URL
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            # Add URL parameters if specified
            url_params = []
            if default_options.get('autoplay'):
                url_params.append('autoplay=1')
            if default_options.get('mute'):
                url_params.append('mute=1')
            if default_options.get('start'):
                url_params.append(f"start={default_options['start']}")
            if default_options.get('end'):
                url_params.append(f"end={default_options['end']}")
            
            if url_params:
                embed_url += '?' + '&'.join(url_params)
            
            # Generate responsive iframe HTML
            embed_code = f'''<div class="youtube-embed-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%;">
    <iframe 
        src="{embed_url}"
        width="{default_options['width']}"
        height="{default_options['height']}"
        frameborder="{default_options['frameborder']}"
        loading="{default_options['loading']}"
        allow="{default_options['allow']}"
        {'allowfullscreen' if default_options['allowfullscreen'] else ''}
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    </iframe>
</div>'''
            
            return True, embed_code, None
            
        except Exception as e:
            return False, None, f"Failed to generate embed code: {str(e)}"
    
    @classmethod
    def extract_video_metadata(cls, video_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract video metadata (basic info without API)
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple of (success, metadata_dict, error_message)
        """
        if not video_id or not isinstance(video_id, str):
            return False, None, "Video ID is required and must be a string"
        
        # Validate video ID format
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            return False, None, "Invalid video ID format"
        
        try:
            # Basic metadata we can provide without API
            metadata = {
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                'thumbnail_medium': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                'thumbnail_small': f"https://img.youtube.com/vi/{video_id}/default.jpg",
                'embed_url': f"https://www.youtube.com/embed/{video_id}"
            }
            
            return True, metadata, None
            
        except Exception as e:
            return False, None, f"Failed to extract metadata: {str(e)}"
    
    @classmethod
    def process_youtube_url(cls, url: str, embed_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Complete YouTube URL processing: validate, extract ID, generate embed code and metadata
        with comprehensive error handling
        
        Args:
            url: YouTube URL to process
            embed_options: Optional embed parameters
            
        Returns:
            Tuple of (success, video_data, error_message)
            video_data contains: video_id, url, embed_code, metadata
        """
        try:
            # Validate URL and extract video ID
            is_valid, video_id, error = cls.validate_youtube_url(url)
            if not is_valid:
                # Provide user-friendly error messages
                if not url or not url.strip():
                    return False, None, "Please provide a YouTube video URL."
                elif "Invalid YouTube URL format" in error:
                    return False, None, "The provided URL is not a valid YouTube video link. Please check the URL and try again."
                else:
                    return False, None, f"URL validation failed: {error}"
            
            # Generate embed code with error handling
            embed_success, embed_code, embed_error = cls.generate_embed_code(video_id, embed_options)
            if not embed_success:
                return False, None, f"Failed to generate video embed code: {embed_error}"
            
            # Extract metadata with error handling
            meta_success, metadata, meta_error = cls.extract_video_metadata(video_id)
            if not meta_success:
                # Metadata extraction failure shouldn't block the entire process
                # Create minimal metadata
                metadata = {
                    'video_id': video_id,
                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    'embed_url': f"https://www.youtube.com/embed/{video_id}"
                }
            
            # Combine all data
            video_data = {
                'video_id': video_id,
                'url': url,
                'embed_code': embed_code,
                'metadata': metadata
            }
            
            return True, video_data, None
            
        except Exception as e:
            return False, None, f"An unexpected error occurred while processing the YouTube URL: {str(e)}"
    
    @classmethod
    def validate_video_accessibility(cls, video_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a YouTube video is accessible (not private/deleted)
        This is a basic check using thumbnail availability
        
        Args:
            video_id: YouTube video ID to check
            
        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            import urllib.request
            import urllib.error
            
            # Try to access the video thumbnail - if it exists, video is likely accessible
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
            
            try:
                with urllib.request.urlopen(thumbnail_url, timeout=10) as response:
                    if response.status == 200:
                        return True, None
                    else:
                        return False, "Video may be private or unavailable"
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return False, "Video not found or is private"
                else:
                    return False, f"Video accessibility check failed (HTTP {e.code})"
            except urllib.error.URLError as e:
                return False, "Network error while checking video accessibility"
                
        except ImportError:
            # If urllib is not available, assume video is accessible
            return True, None
        except Exception as e:
            # Don't fail the entire process for accessibility check
            return True, f"Could not verify video accessibility: {str(e)}"