# Database Migration Guide

## Important: Never Reset Production Database!

**NEVER** run `reset_db.py` in production - it will delete all your users and data!

## Safe Migration Process

### For Adding New Columns (Like profile_picture)

1. **Run the migration script:**
   ```bash
   python migrate_add_profile_picture.py
   ```

2. **Verify the migration:**
   - The script will tell you if the column was added successfully
   - It checks if the column already exists before adding
   - Safe to run multiple times

3. **Restart your application:**
   ```bash
   # Stop the current server
   # Then start it again
   python run.py
   ```

## Migration Scripts

### Current Migrations
- `migrate_add_profile_picture.py` - Adds profile_picture column to user table

### Creating New Migrations

When you need to add new fields to the database:

1. **Create a migration script** (e.g., `migrate_add_new_field.py`):
   ```python
   import sqlite3
   
   conn = sqlite3.connect('src/instance/users.db')
   cursor = conn.cursor()
   
   try:
       # Check if column exists
       cursor.execute("PRAGMA table_info(user)")
       columns = [col[1] for col in cursor.fetchall()]
       
       if 'new_field' not in columns:
           cursor.execute("ALTER TABLE user ADD COLUMN new_field VARCHAR(255)")
           conn.commit()
           print("✓ Column added successfully!")
       else:
           print("✓ Column already exists")
   except Exception as e:
       print(f"✗ Error: {e}")
       conn.rollback()
   finally:
       conn.close()
   ```

2. **Test locally first**
3. **Run on production**
4. **Document the migration**

## Database Backup

### Before Any Migration

Always backup your database first:

```bash
# Windows
copy src\instance\users.db src\instance\users_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db

# Linux/Mac
cp src/instance/users.db src/instance/users_backup_$(date +%Y%m%d).db
```

### Restore from Backup

If something goes wrong:

```bash
# Windows
copy src\instance\users_backup_YYYYMMDD.db src\instance\users.db

# Linux/Mac
cp src/instance/users_backup_YYYYMMDD.db src/instance/users.db
```

## When to Use Each Script

### init_db.py
- **Use for:** First-time setup, development
- **Safe for:** New installations only
- **Effect:** Creates tables if they don't exist, adds admin user
- **Data loss:** None (doesn't drop tables)

### reset_db.py
- **Use for:** Development only, starting fresh
- **NEVER use in:** Production
- **Effect:** Drops all tables and recreates them
- **Data loss:** ALL DATA IS DELETED

### migrate_*.py
- **Use for:** Production updates, adding new features
- **Safe for:** Production with existing data
- **Effect:** Adds new columns/tables without deleting data
- **Data loss:** None

## Production Deployment Checklist

When deploying updates that change the database:

- [ ] Backup current database
- [ ] Test migration script locally
- [ ] Review migration script code
- [ ] Run migration script on production
- [ ] Verify migration success
- [ ] Test application functionality
- [ ] Keep backup for 30 days

## Common Migration Scenarios

### Adding a Column
```python
ALTER TABLE user ADD COLUMN new_column VARCHAR(255)
```

### Adding a Column with Default Value
```python
ALTER TABLE user ADD COLUMN new_column VARCHAR(255) DEFAULT 'default_value'
```

### Adding a NOT NULL Column (requires default)
```python
ALTER TABLE user ADD COLUMN new_column VARCHAR(255) NOT NULL DEFAULT ''
```

### Creating a New Table
```python
CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    data TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
)
```

## Troubleshooting

### "Column already exists" error
- This is actually good! It means the migration was already run
- No action needed

### "Database is locked" error
- Stop the Flask application
- Run the migration
- Restart the application

### Migration fails halfway
- Restore from backup
- Fix the migration script
- Try again

## PythonAnywhere Specific

When deploying to PythonAnywhere:

1. **Backup via Files tab:**
   - Download `users.db` before migration

2. **Run migration in Bash console:**
   ```bash
   cd ~/muscle_hustle
   source venv/bin/activate
   python migrate_add_profile_picture.py
   ```

3. **Reload web app:**
   - Go to Web tab
   - Click "Reload" button

## Best Practices

1. ✅ Always backup before migrations
2. ✅ Test migrations locally first
3. ✅ Use migration scripts, not manual SQL
4. ✅ Document all migrations
5. ✅ Keep migration scripts in version control
6. ❌ Never use reset_db.py in production
7. ❌ Never manually edit production database
8. ❌ Never skip backups

## Emergency Rollback

If you need to rollback a migration:

1. Stop the application
2. Restore database from backup
3. Revert code changes
4. Restart application

## Questions?

- Check if column exists: `PRAGMA table_info(table_name)`
- List all tables: `SELECT name FROM sqlite_master WHERE type='table'`
- Count users: `SELECT COUNT(*) FROM user`
