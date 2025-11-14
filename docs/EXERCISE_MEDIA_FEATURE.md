# Exercise Media Feature - Images & YouTube Videos

## Overview

Exercises now support both images and YouTube videos. Users can choose to upload an image or link a YouTube video for each exercise.

## Features Implemented

### ✅ Media Type Selection
- **Image Upload**: Upload exercise demonstration images
- **YouTube Video**: Embed YouTube videos directly

### ✅ Image Upload
- Single image per exercise
- Supported formats: PNG, JPG, JPEG, GIF, WEBP
- Automatic unique filename generation
- Image preview in edit mode
- Displays on exercise list and detail pages

### ✅ YouTube Video Integration
- Accepts YouTube URLs in multiple formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
- Automatically extracts video ID
- Converts to embed URL for display
- Shows video preview in edit mode
- Embeds video on exercise list and detail pages

## Database Schema Updates

### New Fields in Exercise Collection

```javascript
{
  // ... existing fields ...
  media_type: String,        // 'image' or 'video'
  image_filename: String,    // Filename if image uploaded
  video_url: String,         // YouTube embed URL if video selected
  // ... other fields ...
}
```

## How It Works

### Adding Exercise with Media

1. **Login as Admin**
   - Email: super@admin.com
   - Password: 1234qa

2. **Navigate to Add Exercise**
   - Go to "All Exercises"
   - Click the floating "+" button

3. **Select Media Type**
   - Choose "Image" or "YouTube Video"
   - Form dynamically shows relevant input

4. **Upload Image (if selected)**
   - Click "Choose File"
   - Select image from computer
   - Image is uploaded and saved with unique filename

5. **Add YouTube Video (if selected)**
   - Paste YouTube URL
   - System extracts video ID
   - Converts to embed URL
   - Validates URL format

6. **Submit Form**
   - Media is saved to database
   - Image stored in `src/static/uploads/exercises/`
   - Video URL stored as embed link

### Editing Exercise Media

1. **Navigate to Exercise Detail**
   - Click any exercise from list

2. **Click "Edit Exercise"**
   - Current media is displayed
   - Image shows thumbnail
   - Video shows embedded player

3. **Change Media Type**
   - Switch between Image and Video
   - Form updates dynamically

4. **Update Media**
   - **For Image**: Upload new image (old one is deleted)
   - **For Video**: Update YouTube URL

5. **Save Changes**
   - Old media is replaced
   - Database is updated

## Display Locations

### 1. Exercise List Page (`/exercises/`)
- Shows image or video in card thumbnail
- 200px height
- Maintains aspect ratio
- Falls back to 💪 emoji if no media

### 2. Exercise Detail Page (`/exercises/<id>`)
- Large media display at top
- **Image**: Full width, auto height
- **Video**: 16:9 aspect ratio, 450px height
- Fully responsive

### 3. Edit Page (`/exercises/<id>/edit`)
- Shows current media as preview
- Image: 200px thumbnail
- Video: 300x169 embedded player
- Option to replace with new media

## File Management

### Image Storage
- **Location**: `src/static/uploads/exercises/`
- **Naming**: `YYYYMMDD_HHMMSS_originalname.ext`
- **Example**: `20241114_153045_bench_press.jpg`

### Image Deletion
- Old images are automatically deleted when:
  - Uploading new image
  - Switching to video
  - Deleting exercise

### YouTube URL Processing
```python
# Accepted formats:
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/embed/dQw4w9WgXcQ

# Converted to:
https://www.youtube.com/embed/dQw4w9WgXcQ
```

## Validation

### Image Upload
- ✅ File type validation (PNG, JPG, JPEG, GIF, WEBP)
- ✅ Secure filename generation
- ✅ Unique naming to prevent conflicts

### YouTube URL
- ✅ URL format validation
- ✅ Video ID extraction
- ✅ Embed URL conversion
- ❌ Invalid URLs show error message

## User Interface

### Media Type Toggle
```html
○ Image    ○ YouTube Video
```

### Image Upload Section
```
Upload Image
[Choose File] No file chosen
Recommended: 800x600px or larger
```

### Video URL Section
```
YouTube Video URL
[https://www.youtube.com/watch?v=...]
Paste YouTube video URL
```

## API Endpoints

### Create Exercise with Media
```
POST /exercises/add
Content-Type: multipart/form-data

Fields:
- media_type: 'image' or 'video'
- exercise_image: File (if image)
- video_url: String (if video)
- ... other exercise fields
```

### Update Exercise Media
```
POST /exercises/<id>/edit
Content-Type: multipart/form-data

Fields:
- media_type: 'image' or 'video'
- exercise_image: File (if image)
- video_url: String (if video)
- ... other exercise fields
```

## Testing

### Test Image Upload
1. Start server: `python run.py`
2. Login as admin
3. Add new exercise
4. Select "Image"
5. Upload image file
6. Submit
7. Verify image shows on list and detail pages

### Test YouTube Video
1. Login as admin
2. Add new exercise
3. Select "YouTube Video"
4. Paste URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
5. Submit
6. Verify video embeds on list and detail pages

### Test Media Update
1. Edit existing exercise
2. Change from image to video (or vice versa)
3. Upload/paste new media
4. Save
5. Verify old media is replaced

## Security

- ✅ File type validation
- ✅ Secure filename generation
- ✅ Admin-only upload access
- ✅ YouTube URL validation
- ✅ No arbitrary URL embedding (YouTube only)

## Responsive Design

### Mobile
- Images scale to container width
- Videos maintain 16:9 aspect ratio
- Touch-friendly controls

### Desktop
- Optimal viewing size
- Hover effects on cards
- Full-screen video capability

## Future Enhancements

- Multiple images per exercise
- Video thumbnail extraction
- Image compression/optimization
- Vimeo support
- Direct video upload
- Image cropping tool
- Gallery view

## Troubleshooting

### Image Not Showing
- Check file was uploaded successfully
- Verify file is in `src/static/uploads/exercises/`
- Check filename in database matches file

### Video Not Embedding
- Verify YouTube URL format
- Check video is not private/restricted
- Ensure video ID was extracted correctly
- Check embed URL in database

### Upload Fails
- Check file size (max 16MB)
- Verify file type is allowed
- Ensure uploads directory exists
- Check disk space

## Summary

✅ **Image Upload**: Working - stores in filesystem, displays everywhere
✅ **YouTube Videos**: Working - validates URL, embeds properly
✅ **Media Toggle**: Working - dynamic form switching
✅ **Database Storage**: Working - saves media_type, image_filename, video_url
✅ **Display**: Working - shows on list, detail, and edit pages
✅ **Update**: Working - replaces old media, deletes old files
✅ **Validation**: Working - file types and YouTube URLs validated

All media features are fully functional and integrated with MongoDB!
