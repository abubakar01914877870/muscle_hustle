#!/usr/bin/env python3
"""
Script to cleanup all exercises and add unique index on exercise names
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from src.config import Config

def cleanup_and_add_index():
    """Delete all exercises and create unique index on name field"""
    # Connect directly to MongoDB (disable SSL verification for standalone script)
    client = MongoClient(Config.MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client[Config.MONGO_DBNAME]
    
    # Count existing exercises
    count = db.exercises.count_documents({})
    print(f"Found {count} exercises in database")
    
    if count > 0:
        # Delete all exercises
        result = db.exercises.delete_many({})
        print(f"Deleted {result.deleted_count} exercises")
    else:
        print("No exercises to delete")
    
    # Drop existing indexes (except _id)
    print("\nDropping existing indexes...")
    try:
        db.exercises.drop_indexes()
    except Exception as e:
        print(f"Note: {e}")
    
    # Create unique index on name field (case-insensitive)
    print("Creating unique index on 'name' field (case-insensitive)...")
    db.exercises.create_index(
        [('name', 1)],
        unique=True,
        collation={'locale': 'en', 'strength': 2}
    )
    
    print("✓ Unique index created successfully!")
    print("\nExercise names are now unique (case-insensitive)")
    print("You can now import exercises without worrying about duplicates")
    
    client.close()

if __name__ == '__main__':
    cleanup_and_add_index()

