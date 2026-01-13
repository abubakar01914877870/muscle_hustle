#!/usr/bin/env python3
"""
Cleanup script to delete all existing exercises from MongoDB
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from src.config import Config

def cleanup_exercises():
    """Delete all exercises from MongoDB"""
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.MONGO_DBNAME]
        
        # Get exercises collection
        exercises_collection = db['exercises']
        
        # Count before deletion
        count_before = exercises_collection.count_documents({})
        print(f"Found {count_before} exercises in database")
        
        if count_before == 0:
            print("No exercises to delete")
            return
        
        # Ask for confirmation
        confirm = input(f"Are you sure you want to delete all {count_before} exercises? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Cleanup cancelled")
            return
        
        # Delete all exercises
        result = exercises_collection.delete_many({})
        print(f"✅ Deleted {result.deleted_count} exercises")
        
        # Verify deletion
        count_after = exercises_collection.count_documents({})
        print(f"Remaining exercises: {count_after}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 50)
    print("Exercise Database Cleanup Script")
    print("=" * 50)
    cleanup_exercises()
    print("=" * 50)
    print("Cleanup complete!")
