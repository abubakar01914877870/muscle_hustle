# MongoDB Connection Protocol

## Overview

The application implements a robust MongoDB connection protocol with proper error handling and status reporting.

## Connection Testing

### On Application Startup

When you start the application with `python run.py`, you'll see:

**Successful Connection:**
```
============================================================
🔌 MONGODB CONNECTION TEST
============================================================
✅ MongoDB Connection SUCCESSFUL!
   URI: your-cluster.mongodb.net/?appName=your-app
   Database: muscle_hustle
✅ Database indexes created successfully
============================================================
```

**Failed Connection:**
```
============================================================
🔌 MONGODB CONNECTION TEST
============================================================
❌ MongoDB Connection FAILED!
   Error: [detailed error message]
   URI: your-cluster.mongodb.net
   Database: muscle_hustle

⚠️  Please check:
   1. MongoDB connection string is correct
   2. Network connectivity
   3. MongoDB cluster is running
   4. Credentials are valid
============================================================
```

The application will **exit immediately** if the connection fails, preventing startup with a broken database connection.

### Database Initialization

When you run `python init_db.py`, you'll see:

**Successful Initialization:**
```
============================================================
🔧 MONGODB DATABASE INITIALIZATION
============================================================

🔌 Testing MongoDB connection...
✅ MongoDB Connection SUCCESSFUL!
   URI: your-cluster.mongodb.net
   Database: muscle_hustle

📑 Creating database indexes...
✅ Indexes created successfully

👤 Checking for admin user (super@admin.com)...
✅ Admin user already exists: super@admin.com

============================================================
✅ DATABASE INITIALIZATION COMPLETE!
============================================================
```

**Failed Initialization:**
```
============================================================
🔧 MONGODB DATABASE INITIALIZATION
============================================================

🔌 Testing MongoDB connection...
❌ MongoDB Connection FAILED!
   Error: [detailed error message]
   URI: your-cluster.mongodb.net
   Database: muscle_hustle

⚠️  Please check:
   1. MongoDB connection string is correct
   2. Network connectivity
   3. MongoDB cluster is running
   4. Credentials are valid
============================================================
```

## Error Types

The connection protocol handles these error types:

### 1. ConnectionFailure
- **Cause**: Cannot establish connection to MongoDB server
- **Common reasons**: Wrong host, port, or network issues
- **Example**: `Connection failed: invalid:27017: [Errno 11001] getaddrinfo failed`

### 2. ServerSelectionTimeoutError
- **Cause**: Server selection timeout (default: 5 seconds)
- **Common reasons**: Server is down, firewall blocking, slow network
- **Example**: `Server selection timeout: No servers found`

### 3. ConfigurationError
- **Cause**: Invalid connection string or configuration
- **Common reasons**: Malformed URI, invalid options
- **Example**: `Configuration error: Invalid URI scheme`

### 4. Authentication Errors
- **Cause**: Invalid credentials
- **Common reasons**: Wrong username/password, insufficient permissions
- **Example**: `Authentication failed`

## Configuration

### Environment Variables

```bash
# Required
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=app-name

# Optional (defaults to "muscle_hustle")
MONGO_DBNAME=your_database_name

# Flask secret key
SECRET_KEY=your-secret-key
```

### Connection String Format

```
mongodb+srv://[username]:[password]@[cluster-url]/[?options]
```

**Example:**
```
mongodb+srv://admin:mypassword@cluster0.mongodb.net/?retryWrites=true&w=majority
```

## Timeout Settings

- **Server Selection Timeout**: 5 seconds
- **Socket Timeout**: 20 seconds (default)
- **Connect Timeout**: 20 seconds (default)

These can be adjusted in `src/database.py`:
```python
MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
```

## Best Practices

### 1. Always Test Connection First
```python
from src.database import test_connection

success, error = test_connection()
if not success:
    print(f"Connection failed: {error}")
```

### 2. Use Environment Variables
Never hardcode credentials in your code:
```bash
# .env file
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

### 3. Handle Errors Gracefully
The application exits on connection failure to prevent running with a broken database.

### 4. Monitor Connection Status
Check application logs for connection status on startup.

## Troubleshooting

### Problem: "getaddrinfo failed"
**Solution**: Check DNS resolution and network connectivity

### Problem: "Authentication failed"
**Solution**: Verify username and password in connection string

### Problem: "Server selection timeout"
**Solution**: 
- Check if MongoDB cluster is running
- Verify firewall settings
- Check IP whitelist in MongoDB Atlas

### Problem: "SSL/TLS error"
**Solution**: Ensure using `mongodb+srv://` for Atlas clusters

## Testing Connection

### Manual Test
```bash
python test_mongodb_connection.py
```

### From Python
```python
from src.database import test_connection

success, error = test_connection()
if success:
    print("✅ Connected!")
else:
    print(f"❌ Failed: {error}")
```

## Production Deployment

1. **Set environment variables** on your production server
2. **Test connection** before deploying: `python init_db.py`
3. **Monitor logs** for connection status
4. **Set up alerts** for connection failures
5. **Use connection pooling** (handled automatically by PyMongo)

## Security Notes

- Never commit connection strings to version control
- Use environment variables or secret management systems
- Rotate credentials regularly
- Use IP whitelisting in MongoDB Atlas
- Enable authentication on MongoDB instances
- Use TLS/SSL for connections (automatic with `mongodb+srv://`)

## Support

For connection issues:
1. Check MongoDB Atlas dashboard
2. Review application logs
3. Test connection with MongoDB Compass
4. Verify network connectivity
5. Check MongoDB server status
