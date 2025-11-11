# Admin User Guide

## Default Admin Account

A default admin account has been created:
- **Email:** super@admin.com
- **Password:** 1234qa

## Admin Features

### User Management
Admin users have access to a User Management panel where they can:

1. **View All Users**
   - Navigate to `/admin/users` or click "User Management" in the navigation
   - See a list of all registered users with their roles

2. **Edit User Information**
   - Click "Edit" next to any user
   - Update email address
   - Change password (leave blank to keep current password)
   - Toggle admin privileges

3. **Delete Users**
   - Click "Delete" next to any user
   - Admins cannot delete their own account

## User Roles

### Normal User
- Can sign up and log in
- Access to home page
- Cannot access admin features

### Admin User
- All normal user features
- Access to User Management panel
- Can view, edit, and delete other users
- Can promote users to admin or demote them to normal users

## Security Notes

- Change the default admin password immediately after first login
- Admin privileges are required to access `/admin/*` routes
- Non-admin users attempting to access admin routes will be redirected
