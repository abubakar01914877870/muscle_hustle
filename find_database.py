"""
Script to find the database location
Run this to locate your database file
"""
import os
from pathlib import Path

def find_database():
    print("=" * 70)
    print("  Database Location Finder")
    print("=" * 70)
    print()
    
    # Possible database locations
    possible_paths = [
        'src/instance/users.db',
        'instance/users.db',
        'users.db',
        'src/users.db',
        '../instance/users.db',
    ]
    
    print("Checking possible locations...")
    print()
    
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            print(f"✓ FOUND: {path}")
            print(f"  Absolute path: {abs_path}")
            print(f"  Size: {size} bytes")
            print()
            found = True
    
    if not found:
        print("✗ Database not found in common locations.")
        print()
        print("Searching in current directory and subdirectories...")
        print()
        
        # Search for any .db files
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.db'):
                    full_path = os.path.join(root, file)
                    abs_path = os.path.abspath(full_path)
                    size = os.path.getsize(full_path)
                    print(f"Found: {full_path}")
                    print(f"  Absolute path: {abs_path}")
                    print(f"  Size: {size} bytes")
                    print()
    
    print("=" * 70)
    print()
    print("Current working directory:")
    print(f"  {os.getcwd()}")
    print()
    print("To create database if it doesn't exist:")
    print("  python init_db.py")
    print("=" * 70)

if __name__ == '__main__':
    find_database()
