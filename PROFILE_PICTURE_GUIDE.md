# Profile Picture Feature Guide

## Overview
Users can now upload, view, and remove their profile pictures in Muscle Hustle.

## Features

### 1. **Profile Picture Upload**
- Click on the profile image in the profile page to upload
- Supported formats: PNG, JPG, JPEG, GIF, WEBP
- Automatic file naming with timestamp
- Old pictures are automatically deleted when uploading new ones

### 2. **Profile Picture Display**
- Shows in header on all pages (top-right corner)
- Shows large in profile hero section
- Falls back to initials if no picture uploaded
- Initials based on full name or email

### 3. **Profile Picture Removal**
- "Remove Picture" button appears when picture is uploaded
- Confirmation dialog before removal
- Reverts to showing initials after removal

## Routes

### User Profile Routes
- `/profile` - View own profile (with upload functionality)
- `/profile/edit` - Edit profile information
- `/profile/upload-picture` - Upload profile picture (POST)
- `/profile/remove-picture` - Remove profile picture (POST)
- `/profile/change-password` - Change password

### Admin Routes (Simplified)
- `/admin/users` - List all users
- `/admin/users/<id>/edit` - Edit user account (email, password, admin status)
- `/admin/users/<id>/delete` - Delete user

**Note:** Admin duplicate profile routes have been removed. Admins manage user accounts, not profiles.

## Database Changes

### User Model
Added new field:
- `profile_picture` (String, 255) - Stores filename of uploaded picture

## File Storage
- **Location**: `src/static/uploads/profiles/`
- **Naming**: `{user_id}_{timestamp}_{original_filename}`
- **Example**: `1_20251113_182930_avatar.jpg`

## Usage

### For Users
1. Go to your profile page
2. Click on your profile image
3. Select an image file
4. Image uploads automatically
5. To remove: click "Remove Picture" button

### For Admins
- Admins can only edit user account details (email, password, admin status)
- Users manage their own profile pictures
- This maintains privacy and user control

## Security
- File type validation (only images allowed)
- Secure filename generation
- User-specific file naming
- Automatic cleanup of old files

## Technical Details

### Upload Process
1. User clicks profile image
2. File input dialog opens
3. User selects image
4. Form auto-submits
5. Server validates file type
6. Old picture deleted (if exists)
7. New picture saved with unique name
8. Database updated
9. User redirected to profile

### Display Logic
```python
if user.profile_picture:
    show image from uploads/profiles/
elif user.full_name:
    show initials from name
else:
    show first letter of email
```

## Future Enhancements
- Image cropping/resizing
- Multiple image sizes (thumbnail, full)
- Image compression
- Profile picture for admin view
- Drag and drop upload
