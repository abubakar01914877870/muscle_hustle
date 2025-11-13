# PythonAnywhere Deployment Guide

## Finding Your Database

The database location on PythonAnywhere is different from local development.

### Step 1: Find Your Database

In a **Bash console**, run:

```bash
cd ~/muscle_hustle
python find_database.py
```

This will show you where your database is located.

### Common Database Locations on PythonAnywhere

1. **If using default Flask config:**
   ```
   ~/muscle_hustle/instance/users.db
   ```

2. **If database was created in src:**
   ```
   ~/muscle_hustle/src/instance/users.db
   ```

3. **Check your app.py config:**
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
   ```
   - `sqlite:///users.db` → Creates in instance folder
   - `sqlite:////absolute/path/users.db` → Absolute path

## Deployment Steps

### 1. Backup Database

Once you know the location:

```bash
cd ~/muscle_hustle

# If database is in instance/
cp instance/users.db instance/users_backup_$(date +%Y%m%d).db

# OR if database is in src/instance/
cp src/instance/users.db src/instance/users_backup_$(date +%Y%m%d).db

# Verify backup
ls -lh instance/users_backup_* 
# OR
ls -lh src/instance/users_backup_*
```

### 2. Update Code

```bash
cd ~/muscle_hustle
git pull origin main
```

### 3. Install Dependencies (if requirements.txt changed)

```bash
cd ~/muscle_hustle
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Migration

```bash
cd ~/muscle_hustle
source venv/bin/activate
python migrate_add_profile_picture.py
```

Expected output:
```
======================================================================
  Database Migration: Add profile_picture column
  SAFE FOR PRODUCTION - No data will be lost
======================================================================

Found database at: instance/users.db
Absolute path: /home/yourusername/muscle_hustle/instance/users.db

Current columns in user table: 20
Columns: id, email, password_hash, is_admin, full_name, ...

Adding 'profile_picture' column to user table...
✓ Successfully added 'profile_picture' column!
✓ Migration completed successfully!
  Total columns now: 21
  Existing users preserved: 5

======================================================================
  ✓ Migration completed successfully!
  You can now restart your application.
======================================================================
```

### 5. Reload Web App

1. Go to **Web** tab
2. Click green **"Reload yourusername.pythonanywhere.com"** button
3. Wait for reload to complete

### 6. Verify

1. Visit your site: `https://yourusername.pythonanywhere.com`
2. Log in with existing account
3. Go to Profile page
4. Try uploading a profile picture
5. Check if picture shows in header

## Troubleshooting

### "Database not found" Error

**Solution 1: Find the database**
```bash
cd ~/muscle_hustle
python find_database.py
```

**Solution 2: Check if database exists**
```bash
cd ~/muscle_hustle
ls -la instance/
ls -la src/instance/
```

**Solution 3: Create database if missing**
```bash
cd ~/muscle_hustle
source venv/bin/activate
python init_db.py
```

### "Column already exists" Error

This is actually good! It means migration already ran.

```
✓ Column 'profile_picture' already exists.
  No migration needed!
```

Just reload your web app.

### "Database is locked" Error

**Cause:** Web app is accessing the database

**Solution:**
1. Stop web app (Web tab → Disable button)
2. Run migration
3. Enable web app
4. Reload

### "Permission denied" Error

**Solution:**
```bash
cd ~/muscle_hustle
chmod 644 instance/users.db
# OR
chmod 644 src/instance/users.db
```

### Web App Shows Error After Migration

**Check error log:**
1. Go to **Web** tab
2. Click on error log link
3. Look for the actual error

**Common issues:**
- Missing dependency: `pip install -r requirements.txt`
- Wrong Python version: Check Web tab → Python version
- Code not updated: `git pull origin main`

## File Permissions

Ensure correct permissions:

```bash
cd ~/muscle_hustle

# Database file
chmod 644 instance/users.db

# Upload directories
chmod 755 src/static/uploads
chmod 755 src/static/uploads/profiles
chmod 755 src/static/uploads/progress

# Make sure you own the files
ls -la instance/users.db
```

## Checking Migration Status

To verify migration worked:

```bash
cd ~/muscle_hustle
source venv/bin/activate

python -c "
from src.app import app
from src.models.user import User, db

with app.app_context():
    # Check if column exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    if 'profile_picture' in columns:
        print('✓ profile_picture column exists')
    else:
        print('✗ profile_picture column missing')
    
    # Count users
    user_count = User.query.count()
    print(f'✓ Total users: {user_count}')
"
```

## Rollback Procedure

If something goes wrong:

### 1. Stop Web App
- Web tab → Disable button

### 2. Restore Database
```bash
cd ~/muscle_hustle

# Restore from backup
cp instance/users_backup_YYYYMMDD.db instance/users.db
# OR
cp src/instance/users_backup_YYYYMMDD.db src/instance/users.db
```

### 3. Revert Code (if needed)
```bash
cd ~/muscle_hustle
git log --oneline  # Find previous commit
git checkout COMMIT_HASH
```

### 4. Reload Web App
- Web tab → Reload button

## Complete Deployment Checklist

- [ ] Backup database
- [ ] Update code (`git pull`)
- [ ] Install dependencies (if needed)
- [ ] Run migration script
- [ ] Check migration output for success
- [ ] Reload web app
- [ ] Test login with existing account
- [ ] Test profile picture upload
- [ ] Check error logs
- [ ] Verify all features work

## Quick Reference Commands

```bash
# Navigate to project
cd ~/muscle_hustle

# Activate virtual environment
source venv/bin/activate

# Find database
python find_database.py

# Backup database (adjust path as needed)
cp instance/users.db instance/users_backup_$(date +%Y%m%d).db

# Update code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migration
python migrate_add_profile_picture.py

# Check users count
python -c "from src.app import app; from src.models.user import User; app.app_context().push(); print(f'Users: {User.query.count()}')"
```

Then reload web app from Web tab.

## Support

If you need help:

1. **Check error logs** (Web tab → error log link)
2. **Run find_database.py** to locate files
3. **Check file permissions** with `ls -la`
4. **Verify Python version** (Web tab)
5. **Check virtual environment** is activated

## Important Notes

- ⚠️ Always backup before changes
- ✅ Migration is safe - preserves all data
- ✅ Safe to run migration multiple times
- ❌ Never use reset_db.py in production
- 📝 Keep backups for at least 30 days

## After Successful Deployment

Your users will now be able to:
- Upload profile pictures
- See profile pictures in header on all pages
- Remove profile pictures
- All existing accounts and data remain intact

## Database Location Reference

| Environment | Typical Location |
|-------------|-----------------|
| Local Dev (Windows) | `src\instance\users.db` |
| Local Dev (Linux/Mac) | `src/instance/users.db` |
| PythonAnywhere | `~/muscle_hustle/instance/users.db` |
| PythonAnywhere (alt) | `~/muscle_hustle/src/instance/users.db` |

Use `find_database.py` to confirm your specific location.
