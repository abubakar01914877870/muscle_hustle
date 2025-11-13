# Production Deployment Quick Reference

## ⚠️ CRITICAL: Never Reset Production Database!

**NEVER run `reset_db.py` in production!** It will delete all your users and data.

## Safe Deployment Process

### 1. Backup First (Always!)
```bash
# Create backup with timestamp
cp src/instance/users.db src/instance/users_backup_$(date +%Y%m%d_%H%M%S).db

# Verify backup was created
ls -lh src/instance/users_backup_*
```

### 2. Run Migration (If Database Schema Changed)
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate.bat  # Windows

# Run migration script
python migrate_add_profile_picture.py

# Check for success message
```

### 3. Update Code
```bash
# Pull latest code
git pull origin main

# Install any new dependencies
pip install -r requirements.txt
```

### 4. Restart Application
```bash
# Stop current process
# Then start again
python run.py
```

## PythonAnywhere Deployment

### 1. Backup Database
1. Go to **Files** tab
2. Navigate to `muscle_hustle/src/instance/`
3. Download `users.db` to your computer

### 2. Update Code
```bash
# In Bash console
cd ~/muscle_hustle
git pull origin main
```

### 3. Run Migration
```bash
# In Bash console
cd ~/muscle_hustle
source venv/bin/activate
python migrate_add_profile_picture.py
```

### 4. Reload Web App
1. Go to **Web** tab
2. Click green **"Reload"** button
3. Check error log if issues occur

## Verification Checklist

After deployment, verify:

- [ ] Application starts without errors
- [ ] Can log in with existing account
- [ ] Can view profile page
- [ ] Can upload profile picture
- [ ] Profile picture shows in header
- [ ] All existing users still present
- [ ] Admin functions work

## Rollback Procedure

If something goes wrong:

### 1. Stop Application
```bash
# Stop the running process
```

### 2. Restore Database
```bash
# Restore from backup
cp src/instance/users_backup_YYYYMMDD_HHMMSS.db src/instance/users.db
```

### 3. Revert Code (if needed)
```bash
git revert HEAD
# OR
git checkout previous_commit_hash
```

### 4. Restart Application
```bash
python run.py
```

## Common Issues

### "Column already exists" Error
- **Cause**: Migration already run
- **Solution**: This is fine! No action needed.

### "Database is locked" Error
- **Cause**: Application is running
- **Solution**: Stop application, run migration, restart

### "No such table" Error
- **Cause**: Database not initialized
- **Solution**: Run `python init_db.py` first

### Users Can't Log In After Update
- **Cause**: Database not migrated
- **Solution**: Run migration script

## File Locations

### Local Development
- Database: `src/instance/users.db`
- Uploads: `src/static/uploads/`
- Logs: Check terminal output

### PythonAnywhere
- Database: `/home/yourusername/muscle_hustle/src/instance/users.db`
- Uploads: `/home/yourusername/muscle_hustle/src/static/uploads/`
- Logs: Web tab → Error log link

## Scripts Reference

| Script | Purpose | Safe for Production? |
|--------|---------|---------------------|
| `init_db.py` | Initialize database | ✅ Yes (doesn't drop tables) |
| `reset_db.py` | Reset database | ❌ NO! (deletes all data) |
| `migrate_*.py` | Add new columns | ✅ Yes (preserves data) |
| `run.py` | Start application | ✅ Yes |

## Emergency Contacts

If you need help:
1. Check error logs
2. Review [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
3. Restore from backup
4. Check GitHub issues

## Best Practices

1. ✅ Always backup before changes
2. ✅ Test in development first
3. ✅ Use migration scripts
4. ✅ Keep backups for 30 days
5. ✅ Document all changes
6. ❌ Never use reset_db.py in production
7. ❌ Never manually edit database
8. ❌ Never skip backups

## Quick Commands

```bash
# Backup
cp src/instance/users.db src/instance/backup_$(date +%Y%m%d).db

# Migrate
python migrate_add_profile_picture.py

# Check users count
python -c "from src.app import app; from src.models.user import User; app.app_context().push(); print(f'Users: {User.query.count()}')"

# Restart (PythonAnywhere)
# Go to Web tab → Click Reload button
```

## Success Indicators

After successful deployment:
- ✓ No errors in logs
- ✓ Application loads
- ✓ Users can log in
- ✓ New features work
- ✓ Old data intact
- ✓ Profile pictures upload/display

## Remember

**The golden rule of production databases:**
> If you're not 100% sure, backup first and test in development!
