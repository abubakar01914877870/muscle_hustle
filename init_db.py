"""
Initialize MongoDB Database with Default Admin User
"""
from src.database import get_mongo_client, test_connection
from src.models.user_mongo import User
import os
import sys

def init_database():
    """Initialize MongoDB with indexes and default admin user"""
    
    # Get MongoDB connection
    mongo_uri = os.environ.get('MONGO_URI') or "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"
    dbname = os.environ.get('MONGO_DBNAME') or "muscle_hustle"
    
    print("\n" + "="*60)
    print("🔧 MONGODB DATABASE INITIALIZATION")
    print("="*60)
    
    # Test connection first
    print("\n🔌 Testing MongoDB connection...")
    success, error = test_connection()
    
    if not success:
        print("❌ MongoDB Connection FAILED!")
        print(f"   Error: {error}")
        print(f"   URI: {mongo_uri.split('@')[1] if '@' in mongo_uri else mongo_uri}")
        print(f"   Database: {dbname}")
        print("\n⚠️  Please check:")
        print("   1. MongoDB connection string is correct")
        print("   2. Network connectivity")
        print("   3. MongoDB cluster is running")
        print("   4. Credentials are valid")
        print("="*60 + "\n")
        sys.exit(1)
    
    print("✅ MongoDB Connection SUCCESSFUL!")
    print(f"   URI: {mongo_uri.split('@')[1] if '@' in mongo_uri else mongo_uri}")
    print(f"   Database: {dbname}")
    
    try:
        client = get_mongo_client()
        db = client[dbname]
        
        # Create indexes
        print("\n📑 Creating database indexes...")
        db.users.create_index('email', unique=True)
        db.progress_entries.create_index('user_id')
        db.progress_entries.create_index('created_at')
        print("✅ Indexes created successfully")
        
        # Check if admin user exists
        admin_email = 'super@admin.com'
        print(f"\n👤 Checking for admin user ({admin_email})...")
        existing_admin = User.find_by_email(db, admin_email)
        
        if existing_admin:
            print(f"✅ Admin user already exists: {admin_email}")
        else:
            # Create default admin user
            print("📝 Creating default admin user...")
            User.create(
                db=db,
                email=admin_email,
                password='1234qa',
                is_admin=True
            )
            print(f"✅ Admin user created successfully!")
            print(f"   Email: {admin_email}")
            print(f"   Password: 1234qa")
            print(f"   ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")
        
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Initialization FAILED!")
        print(f"   Error: {str(e)}")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == '__main__':
    init_database()
