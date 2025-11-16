"""
Image Handler for MongoDB Storage
Stores images as base64 encoded strings in MongoDB
"""
import base64
from io import BytesIO
from PIL import Image

def encode_image(file):
    """
    Encode uploaded file to base64 string
    Args:
        file: FileStorage object from Flask
    Returns:
        dict with image_data (base64 string) and content_type
    """
    try:
        # Read file data
        file_data = file.read()
        
        # Get content type
        content_type = file.content_type or 'image/jpeg'
        
        # Encode to base64
        encoded = base64.b64encode(file_data).decode('utf-8')
        
        return {
            'image_data': encoded,
            'content_type': content_type,
            'filename': file.filename
        }
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def decode_image(image_data, content_type='image/jpeg'):
    """
    Decode base64 string to image bytes
    Args:
        image_data: base64 encoded string
        content_type: MIME type of image
    Returns:
        bytes of image data
    """
    try:
        return base64.b64decode(image_data)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def resize_image(file, max_width=800, max_height=800):
    """
    Resize image to maximum dimensions while maintaining aspect ratio
    Args:
        file: FileStorage object
        max_width: maximum width in pixels
        max_height: maximum height in pixels
    Returns:
        dict with resized image data
    """
    try:
        # Open image
        img = Image.open(file.stream)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Calculate new dimensions
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Encode to base64
        encoded = base64.b64encode(output.read()).decode('utf-8')
        
        return {
            'image_data': encoded,
            'content_type': 'image/jpeg',
            'filename': file.filename,
            'width': img.width,
            'height': img.height
        }
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def get_image_data_url(image_data, content_type='image/jpeg'):
    """
    Create data URL for embedding in HTML
    Args:
        image_data: base64 encoded string
        content_type: MIME type
    Returns:
        data URL string
    """
    if not image_data:
        return None
    return f"data:{content_type};base64,{image_data}"
