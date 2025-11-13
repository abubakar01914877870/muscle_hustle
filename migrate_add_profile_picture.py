"""
Database migration script to add profile_picture column
This script safely adds the new column without losing existing data

IMPORTANT: This is safe to run in production - it will NOT delete any data!
"""
import sqlite3
import os

def migrate_database():
    db_path = 'src/instance/users.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"✗ Database not found at {db_path}")
        print("  Run init_db.py to create the database first.")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in user table: {len(columns)}")
        print(f"Columns: {', '.join(columns)}")
        print()
        
        # Check if column already exists
        if 'profile_picture' in columns:
            print("✓ Column 'profile_picture' already exists.")
            print("  No migration needed!")
            return True
        
        # Add the new column
        print("Adding 'profile_picture' column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN profile_picture VARCHAR(255)")
        conn.commit()
        print("✓ Successfully added 'profile_picture' column!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(user)")
        new_columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_picture' in new_columns:
            print("✓ Migration completed successfully!")
            print(f"  Total columns now: {len(new_columns)}")
            
            # Count existing users
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]
            print(f"  Existing users preserved: {user_count}")
            return True
        else:
            print("✗ Migration failed - column not found after adding")
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 70)
    print("  Database Migration: Add profile_picture column")
    print("  SAFE FOR PRODUCTION - No data will be lost")
    print("=" * 70)
    print()
    
    success = migrate_database()
    
    print()
    print("=" * 70)
    if success:
        print("  ✓ Migration completed successfully!")
        print("  You can now restart your application.")
    else:
        print("  ✗ Migration failed. Please check the error messages above.")
    print("=" * 70)
