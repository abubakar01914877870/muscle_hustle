# YouTube Video Troubleshooting Guide

## Issue Fixed: YouTube Videos Not Saving

### Problem
YouTube video URLs were not being saved to the database when adding or editing exercises.

### Root Cause
There were **duplicate video_url input fields** in both add.html and edit.html templates:
1. One old field from the original template
2. One new field in the media selection section

This caused form submission confusion where the wrong (empty) field was being submitted.

### Solution Applied

1. **Removed duplicate fields** from both templates
2. **Added debug logging** to track video URL processing
3. **Improved JavaScript** to properly toggle between image and video inputs
4. **Added validation** to ensure YouTube URL is provided when video option is selected

## How to Test YouTube Video Feature

### Test 1: Add Exercise with YouTube Video

1. **Start the server:**
   ```bash
   python run.py
   ```

2. **Login as admin:**
   - Email: super@admin.com
   - Password: 1234qa

3. **Navigate to Add Exercise:**
   - Go to http://127.0.0.1:5000/exercises/
   - Click the floating "+" button

4. **Fill in the form:**
   - Exercise Name: "Test Push-Up"
   - Primary Muscle: "Chest"
   - Equipment: "Body Weight"
   - Difficulty: Select "Beginner"
   - Type: "Strength"

5. **Select Video Option:**
   - Click "YouTube Video" radio button
   - The form should hide image upload and show video URL field

6. **Paste YouTube URL:**
   - Use test URL: `https://www.youtube.com/watch?v=IODxDxX7oi4`
   - Or any valid YouTube URL

7. **Submit the form**

8. **Verify:**
   - You should see success message
   - Exercise appears in list with embedded video
   - Click exercise to see detail page with video

### Test 2: Edit Exercise to Change Video

1. **Click on an exercise** with a video
2. **Click "Edit Exercise"**
3. **Verify current video** is shown in preview
4. **Paste new YouTube URL**
5. **Save changes**
6. **Verify** new video is displayed

### Test 3: Switch from Image to Video

1. **Edit an exercise** that has an image
2. **Select "YouTube Video"** radio button
3. **Paste YouTube URL**
4. **Save changes**
5. **Verify** video replaces image

## Supported YouTube URL Formats

The system accepts these YouTube URL formats:

```
✅ https://www.youtube.com/watch?v=VIDEO_ID
✅ https://youtu.be/VIDEO_ID
✅ https://www.youtube.com/embed/VIDEO_ID
✅ https://www.youtube.com/watch?v=VIDEO_ID&feature=share
```

All formats are automatically converted to:
```
https://www.youtube.com/embed/VIDEO_ID
```

## Debug Mode

The application now includes debug logging. Check the console output when adding/editing exercises:

```
DEBUG: Video URL from form: 'https://www.youtube.com/watch?v=...'
DEBUG: Extracted YouTube ID: 'VIDEO_ID'
DEBUG: Final embed URL: 'https://www.youtube.com/embed/VIDEO_ID'
DEBUG: Creating exercise with media_type='video', image_filename='None', video_url='https://...'
```

## Common Issues & Solutions

### Issue 1: "Invalid YouTube URL" Error

**Cause:** URL format not recognized

**Solution:**
- Use one of the supported formats above
- Make sure URL contains video ID
- Don't use playlist URLs
- Don't use channel URLs

**Example of valid URL:**
```
https://www.youtube.com/watch?v=IODxDxX7oi4
```

### Issue 2: Video Not Showing on List Page

**Cause:** Video URL not saved to database

**Solution:**
1. Check server console for debug messages
2. Verify you selected "YouTube Video" radio button
3. Ensure you pasted URL in the correct field
4. Check database to confirm video_url is saved:
   ```python
   from src.database import get_mongo_client
   client = get_mongo_client()
   db = client['muscle_hustle']
   exercise = db.exercises.find_one({'name': 'Your Exercise Name'})
   print(exercise.get('video_url'))
   print(exercise.get('media_type'))
   ```

### Issue 3: Video Shows on Detail Page but Not List Page

**Cause:** Template rendering issue

**Solution:**
- Clear browser cache
- Check browser console for errors
- Verify iframe is not blocked by browser

### Issue 4: "Please provide a YouTube URL" Error

**Cause:** Video option selected but no URL provided

**Solution:**
- Make sure to paste a YouTube URL before submitting
- Check that the URL field is visible (not hidden)

## Verification Checklist

After adding/editing an exercise with video:

- [ ] Success message appears
- [ ] Exercise appears in list
- [ ] Video thumbnail/embed shows in list card
- [ ] Clicking exercise opens detail page
- [ ] Video plays on detail page
- [ ] Edit page shows video preview
- [ ] Database contains correct video_url
- [ ] Database contains media_type='video'

## Database Structure

When a video is saved, the database document looks like:

```javascript
{
  _id: ObjectId("..."),
  name: "Exercise Name",
  media_type: "video",
  image_filename: null,
  video_url: "https://www.youtube.com/embed/VIDEO_ID",
  // ... other fields
}
```

## Testing with MongoDB

To verify video is saved correctly:

```python
from src.database import get_mongo_client
from src.models.exercise_mongo import Exercise

client = get_mongo_client()
db = client['muscle_hustle']

# Find all exercises with videos
video_exercises = db.exercises.find({'media_type': 'video'})
for ex in video_exercises:
    print(f"Name: {ex['name']}")
    print(f"Video URL: {ex.get('video_url')}")
    print(f"Media Type: {ex.get('media_type')}")
    print("---")
```

## Browser Compatibility

YouTube embeds work in:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## Security Notes

- Only YouTube URLs are accepted (no arbitrary video URLs)
- Video IDs are extracted and validated
- Embed URLs use YouTube's official embed format
- No XSS vulnerabilities from user input

## Next Steps if Still Not Working

1. **Check server logs** for error messages
2. **Verify MongoDB connection** is working
3. **Test with simple exercise** (minimal fields)
4. **Check browser console** for JavaScript errors
5. **Verify form submission** using browser dev tools (Network tab)
6. **Contact support** with:
   - Server console output
   - Browser console errors
   - Screenshot of form
   - YouTube URL you're trying to use

## Summary

✅ **Fixed:** Duplicate video_url fields removed
✅ **Added:** Debug logging for troubleshooting
✅ **Improved:** Form validation and error messages
✅ **Tested:** Backend video saving works correctly
✅ **Verified:** Videos display on all pages

The YouTube video feature is now fully functional!
