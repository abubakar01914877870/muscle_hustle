# Image Storage in MongoDB - Complete Implementation

## Overview

All images are now stored directly in MongoDB as base64-encoded strings instead of the filesystem. This provides:
- **Portability**: Database contains everything
- **Backup**: Single backup includes all data
- **Scalability**: No filesystem dependencies
- **Simplicity**: No file management needed

## What Changed

### Before (Filesystem Storage)
```
Images stored in: src/static/uploads/
- profiles/user_id_timestamp_image.jpg
- exercises/timestamp_image.jpg
- progress/user_id_timestamp_image.jpg
```

### After (Database Storage)
```
Images stored in MongoDB as base64 strings:
- users.profile_picture (base64 string)
- exercises.image_data (base64 string)
- progress_entries.photo_data (base64 string)
```

## Implementation Details

### 1. Image Handler Utility (`src/utils/image_handler.py`)

**Functions:**
- `encode_image(file)` - Converts uploaded file to base64
- `decode_image(image_data)` - Converts base64 back to bytes
- `resize_image(file, max_width, max_height)` - Resizes and optimizes images
- `get_image_data_url(image_data, content_type)` - Creates data URL for HTML

**Image Processing:**
- Automatic resizing to max dimensions
- RGBA to RGB conversion
- JPEG compression (85% quality)
- Optimization for web

### 2. Database Schema Updates

#### User Model
```javascript
{
  profile_picture: String,      // base64 encoded image
  profile_picture_type: String, // MIME type (e.g., "image/jpeg")
  // ... other fields
}
```

#### Exercise Model
```javascript
{
  media_type: String,    // 'image' or 'video'
  image_data: String,    // base64 encoded image
  image_type: String,    // MIME type
  video_url: String,     // YouTube embed URL
  // ... other fields
}
```

#### Progress Entry Model
```javascript
{
  photo_data: String,    // base64 encoded photo
  photo_type: String,    // MIME type
  // ... other fields
}
```

### 3. Model Methods Added

**User Model:**
```python
def get_profile_picture_url(self):
    """Get data URL for profile picture"""
    if self.profile_picture:
        return f"data:{self.profile_picture_type};base64,{self.profile_picture}"
    return None
```

**Exercise Model:**
```python
def get_image_url(self):
    """Get data URL for image"""
    if self.image_data:
        return f"data:{self.image_type};base64,{self.image_data}"
    return None
```

**Progress Entry Model:**
```python
def get_photo_url(self):
    """Get data URL for photo"""
    if self.photo_data:
        return f"data:{self.photo_type};base64,{self.photo_data}"
    return None
```

### 4. Route Updates

#### Profile Routes
- **Upload**: Resizes to 400x400, stores base64 in DB
- **Remove**: Sets profile_picture to None
- **No file operations**: All data in MongoDB

#### Exercise Routes
- **Add**: Resizes to 800x800, stores base64 in DB
- **Edit**: Updates image_data field
- **Delete**: No file cleanup needed

#### Progress Routes
- **Add**: Resizes to 800x800, stores base64 in DB
- **Delete**: No file cleanup needed

### 5. Template Updates

All templates now use data URLs:

**Before:**
```html
<img src="{{ url_for('static', filename='uploads/profiles/' + user.profile_picture) }}">
```

**After:**
```html
<img src="{{ user.get_profile_picture_url() }}">
```

## Image Sizes

### Profile Pictures
- **Max Dimensions**: 400x400 pixels
- **Format**: JPEG
- **Quality**: 85%
- **Typical Size**: 20-50 KB

### Exercise Images
- **Max Dimensions**: 800x800 pixels
- **Format**: JPEG
- **Quality**: 85%
- **Typical Size**: 50-150 KB

### Progress Photos
- **Max Dimensions**: 800x800 pixels
- **Format**: JPEG
- **Quality**: 85%
- **Typical Size**: 50-150 KB

## Data URLs

Images are embedded in HTML using data URLs:
```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...
```

**Advantages:**
- No separate HTTP requests
- Works offline
- Portable HTML

**Considerations:**
- Larger HTML size
- Not cached separately
- Base64 encoding adds ~33% size overhead

## Migration from Filesystem

### For Existing Images

If you have existing images in the filesystem, you can migrate them:

```python
from src.utils.image_handler import encode_image
from src.models.user_mongo import User
from src.database import get_mongo_client
import os

client = get_mongo_client()
db = client['muscle_hustle']

# Migrate profile pictures
for user_dict in db.users.find({'profile_picture': {'$exists': True, '$ne': None}}):
    old_filename = user_dict['profile_picture']
    file_path = f"src/static/uploads/profiles/{old_filename}"
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            # Read and encode
            file_data = f.read()
            encoded = base64.b64encode(file_data).decode('utf-8')
            
            # Update database
            db.users.update_one(
                {'_id': user_dict['_id']},
                {'$set': {
                    'profile_picture': encoded,
                    'profile_picture_type': 'image/jpeg'
                }}
            )
            print(f"Migrated: {old_filename}")
```

### Cleanup Old Files

After migration, you can safely delete:
```bash
rm -rf src/static/uploads/profiles/*
rm -rf src/static/uploads/exercises/*
rm -rf src/static/uploads/progress/*
```

## Performance Considerations

### Database Size
- Base64 encoding adds ~33% overhead
- 1000 profile pictures (50KB each) = ~66MB
- MongoDB handles this efficiently

### Query Performance
- Images stored as strings
- Indexed fields not affected
- No performance impact on queries

### Loading Speed
- Data URLs load with HTML
- No separate image requests
- Faster for small images
- May be slower for very large images

## Best Practices

### 1. Always Resize Images
```python
image_result = resize_image(file, max_width=800, max_height=800)
```

### 2. Use Appropriate Sizes
- Profile pictures: 400x400
- Thumbnails: 200x200
- Full images: 800x800

### 3. Optimize Quality
- Use 85% JPEG quality
- Convert RGBA to RGB
- Enable optimization

### 4. Handle Errors
```python
if image_result:
    # Success
    image_data = image_result['image_data']
else:
    # Error handling
    flash('Error processing image', 'error')
```

## Testing

### Upload Profile Picture
1. Login
2. Go to profile
3. Click profile image
4. Select image file
5. Verify image displays
6. Check database contains base64 string

### Upload Exercise Image
1. Login as admin
2. Add new exercise
3. Select "Image" option
4. Upload image
5. Verify image shows in list and detail pages

### Upload Progress Photo
1. Go to progress tracker
2. Add entry with photo
3. Submit
4. Verify photo shows in timeline

## Troubleshooting

### Image Not Displaying
- Check browser console for errors
- Verify base64 string exists in database
- Check data URL format

### Image Too Large
- Increase max dimensions in resize_image()
- Reduce JPEG quality
- Use smaller source images

### Upload Fails
- Check Pillow is installed: `pip install Pillow`
- Verify file is valid image
- Check file size limits

## Dependencies

```
Pillow==12.0.0  # Image processing library
```

Install with:
```bash
pip install Pillow
```

## Summary

✅ **All images stored in MongoDB**
✅ **Automatic resizing and optimization**
✅ **No filesystem dependencies**
✅ **Data URLs for display**
✅ **Simplified backup and deployment**
✅ **Profile pictures: 400x400**
✅ **Exercise/Progress images: 800x800**
✅ **JPEG format, 85% quality**

The application now stores all image data directly in the database, making it fully portable and easier to manage!
