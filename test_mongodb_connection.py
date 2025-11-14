"""
Test MongoDB connection
"""
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"

print("=" * 70)
print("Testing MongoDB Connection")
print("=" * 70)
print()

try:
    # Create a new client and connect to the server
    print("Connecting to MongoDB...")
    client = MongoClient(uri)
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("✓ Successfully connected to MongoDB!")
    print()
    
    # Get database info
    print("Database Information:")
    db_names = client.list_database_names()
    print(f"  Available databases: {db_names}")
    print()
    
    # Test accessing the muscle_hustle database
    db = client['muscle_hustle']
    print(f"✓ Connected to 'muscle_hustle' database")
    
    # List collections
    collections = db.list_collection_names()
    print(f"  Collections: {collections if collections else 'None (empty database)'}")
    print()
    
    # Test write operation
    print("Testing write operation...")
    test_collection = db['test']
    result = test_collection.insert_one({"test": "connection", "status": "success"})
    print(f"✓ Write test successful! Inserted ID: {result.inserted_id}")
    
    # Test read operation
    print("Testing read operation...")
    doc = test_collection.find_one({"test": "connection"})
    print(f"✓ Read test successful! Document: {doc}")
    
    # Clean up test
    test_collection.delete_one({"test": "connection"})
    print("✓ Cleanup successful!")
    print()
    
    print("=" * 70)
    print("✓ All tests passed! MongoDB is ready to use.")
    print("=" * 70)
    
    client.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    print()
    print("=" * 70)
    print("✗ Connection failed!")
    print("=" * 70)
