# Quick Start: Production Update

## For PythonAnywhere Users

### Step 1: Find Your Database
```bash
cd ~/muscle_hustle
python find_database.py
```

This will show you where your database is located (e.g., `instance/users.db` or `src/instance/users.db`)

### Step 2: Backup
```bash
# Use the path from Step 1
cp instance/users.db instance/users_backup_$(date +%Y%m%d).db
```

### Step 3: Update Code
```bash
git pull origin main
```

### Step 4: Run Migration
```bash
source venv/bin/activate
python migrate_add_profile_picture.py
```

You should see:
```
✓ Successfully added 'profile_picture' column!
✓ Migration completed successfully!
  Existing users preserved: X
```

### Step 5: Reload Web App
- Go to **Web** tab
- Click **"Reload"** button

### Step 6: Test
- Visit your site
- Log in
- Go to Profile
- Click profile image to upload picture

## Troubleshooting

### "Database not found"
Run: `python find_database.py`

### "Column already exists"
✓ This is good! Migration already done. Just reload web app.

### "Database is locked"
1. Disable web app (Web tab)
2. Run migration
3. Enable and reload web app

## Need Help?

See detailed guides:
- [PYTHONANYWHERE_GUIDE.md](PYTHONANYWHERE_GUIDE.md) - Complete guide
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Deployment procedures
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migration details

## Important

- ✅ Migration is SAFE - preserves all data
- ✅ Can run multiple times safely
- ⚠️ Always backup first
- ❌ Never use reset_db.py in production
