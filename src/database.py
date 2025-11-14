"""
MongoDB Database Connection
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
from flask import g
import os
import sys

# MongoDB URI
MONGO_URI = os.environ.get('MONGO_URI') or "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"
MONGO_DBNAME = os.environ.get('MONGO_DBNAME') or "muscle_hustle"

# Global client
_client = None

def get_mongo_client():
    """Get MongoDB client (singleton)"""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client

def get_db():
    """Get database instance"""
    if 'db' not in g:
        client = get_mongo_client()
        g.db = client[MONGO_DBNAME]
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        # MongoDB connections are pooled, no need to close
        pass

def test_connection():
    """Test MongoDB connection and return status"""
    try:
        client = get_mongo_client()
        # The ping command is cheap and does not require auth
        client.admin.command('ping')
        return True, None
    except ConnectionFailure as e:
        return False, f"Connection failed: {str(e)}"
    except ServerSelectionTimeoutError as e:
        return False, f"Server selection timeout: {str(e)}"
    except ConfigurationError as e:
        return False, f"Configuration error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def init_db(app):
    """Initialize database with app"""
    app.teardown_appcontext(close_db)
    
    # Test connection first
    print("\n" + "="*60)
    print("🔌 MONGODB CONNECTION TEST")
    print("="*60)
    
    success, error = test_connection()
    
    if not success:
        print("❌ MongoDB Connection FAILED!")
        print(f"   Error: {error}")
        print(f"   URI: {MONGO_URI.split('@')[1] if '@' in MONGO_URI else MONGO_URI}")
        print(f"   Database: {MONGO_DBNAME}")
        print("\n⚠️  Please check:")
        print("   1. MongoDB connection string is correct")
        print("   2. Network connectivity")
        print("   3. MongoDB cluster is running")
        print("   4. Credentials are valid")
        print("="*60 + "\n")
        sys.exit(1)
    
    print("✅ MongoDB Connection SUCCESSFUL!")
    print(f"   URI: {MONGO_URI.split('@')[1] if '@' in MONGO_URI else MONGO_URI}")
    print(f"   Database: {MONGO_DBNAME}")
    
    # Create indexes
    try:
        with app.app_context():
            db = get_db()
            
            # Users collection indexes
            db.users.create_index('email', unique=True)
            
            # Progress entries collection indexes
            db.progress_entries.create_index('user_id')
            db.progress_entries.create_index('created_at')
            
            # Exercises collection indexes
            db.exercises.create_index('name')
            db.exercises.create_index('muscle')
            db.exercises.create_index('equipment')
            
            print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not create indexes: {str(e)}")
    
    print("="*60 + "\n")
