# Production Deployment Guide - Muscle Hustle

## Overview

This guide covers deploying the Muscle Hustle application to production with MongoDB image storage.

## Pre-Deployment Checklist

### 1. Environment Variables

Set these environment variables in production:

```bash
# Required
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=muscle-hustle
MONGO_DBNAME=muscle_hustle
SECRET_KEY=your-super-secret-production-key-change-this

# Optional
FLASK_ENV=production
```

**Important:** Never use default values in production!

### 2. Dependencies

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Required packages:
- Flask
- Flask-Login
- Werkzeug
- pymongo
- dnspython
- Pillow

### 3. Database Setup

Initialize MongoDB with indexes and admin user:

```bash
python init_db.py
```

This will:
- Create required indexes
- Create default admin user (super@admin.com / 1234qa)
- Verify MongoDB connection

**⚠️ IMPORTANT:** Change the default admin password immediately after deployment!

## Deployment Steps

### Step 1: Prepare Production Environment

#### A. Set Environment Variables

**On Linux/Mac:**
```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
export MONGO_DBNAME="muscle_hustle"
export SECRET_KEY="your-random-secret-key-here"
export FLASK_ENV="production"
```

**On Windows:**
```cmd
set MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
set MONGO_DBNAME=muscle_hustle
set SECRET_KEY=your-random-secret-key-here
set FLASK_ENV=production
```

**Using .env file (recommended):**
```bash
# Create .env file
cat > .env << EOF
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DBNAME=muscle_hustle
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=production
EOF
```

#### B. Generate Secret Key

```python
import secrets
print(secrets.token_hex(32))
# Use this output as your SECRET_KEY
```

### Step 2: MongoDB Configuration

#### A. MongoDB Atlas Setup

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up or log in

2. **Create Cluster**
   - Choose free tier or paid plan
   - Select region closest to your users
   - Create cluster

3. **Configure Network Access**
   - Go to Network Access
   - Add IP Address
   - For production: Add your server's IP
   - For testing: Use 0.0.0.0/0 (allow all - not recommended for production)

4. **Create Database User**
   - Go to Database Access
   - Add New Database User
   - Set username and password
   - Grant read/write permissions

5. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your password

#### B. Database Indexes

The application automatically creates these indexes:
- `users.email` (unique)
- `progress_entries.user_id`
- `progress_entries.created_at`
- `exercises.name`
- `exercises.muscle`
- `exercises.equipment`

### Step 3: Deploy Application

#### Option A: Deploy to PythonAnywhere

1. **Upload Code**
   ```bash
   # Using Git
   git clone https://github.com/yourusername/muscle-hustle.git
   
   # Or upload files via web interface
   ```

2. **Create Virtual Environment**
   ```bash
   cd muscle-hustle
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure WSGI**
   
   Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   import os
   
   # Add your project directory
   project_home = '/home/yourusername/muscle-hustle'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   
   # Set environment variables
   os.environ['MONGO_URI'] = 'your-mongodb-uri'
   os.environ['MONGO_DBNAME'] = 'muscle_hustle'
   os.environ['SECRET_KEY'] = 'your-secret-key'
   
   # Import Flask app
   from src.app import app as application
   ```

4. **Set Virtual Environment Path**
   - Go to Web tab
   - Set virtualenv path: `/home/yourusername/muscle-hustle/venv`

5. **Reload Web App**
   - Click "Reload" button

#### Option B: Deploy to Heroku

1. **Create Procfile**
   ```
   web: gunicorn wsgi:app
   ```

2. **Install Gunicorn**
   ```bash
   pip install gunicorn
   pip freeze > requirements.txt
   ```

3. **Create Heroku App**
   ```bash
   heroku create muscle-hustle-app
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set MONGO_URI="your-mongodb-uri"
   heroku config:set MONGO_DBNAME="muscle_hustle"
   heroku config:set SECRET_KEY="your-secret-key"
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Initialize Database**
   ```bash
   heroku run python init_db.py
   ```

#### Option C: Deploy to VPS (Ubuntu)

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

2. **Clone Repository**
   ```bash
   cd /var/www
   git clone https://github.com/yourusername/muscle-hustle.git
   cd muscle-hustle
   ```

3. **Setup Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Create Systemd Service**
   
   Create `/etc/systemd/system/muscle-hustle.service`:
   ```ini
   [Unit]
   Description=Muscle Hustle Flask App
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/var/www/muscle-hustle
   Environment="MONGO_URI=your-mongodb-uri"
   Environment="MONGO_DBNAME=muscle_hustle"
   Environment="SECRET_KEY=your-secret-key"
   ExecStart=/var/www/muscle-hustle/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Configure Nginx**
   
   Create `/etc/nginx/sites-available/muscle-hustle`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
       
       location /static {
           alias /var/www/muscle-hustle/src/static;
       }
   }
   ```

6. **Enable and Start Services**
   ```bash
   sudo ln -s /etc/nginx/sites-available/muscle-hustle /etc/nginx/sites-enabled/
   sudo systemctl enable muscle-hustle
   sudo systemctl start muscle-hustle
   sudo systemctl restart nginx
   ```

### Step 4: Post-Deployment Tasks

#### A. Initialize Database
```bash
python init_db.py
```

#### B. Change Default Admin Password

1. Login with default credentials:
   - Email: super@admin.com
   - Password: 1234qa

2. Go to Profile → Change Password

3. Set a strong password

#### C. Test Application

1. **Test Authentication**
   - Login/Logout
   - Sign up new user

2. **Test Profile**
   - Upload profile picture
   - Update profile information

3. **Test Exercises**
   - Add exercise with image
   - Add exercise with YouTube video
   - Edit exercise
   - Delete exercise

4. **Test Progress Tracker**
   - Add progress entry with photo
   - View chart
   - Delete entry

#### D. Monitor Application

Check logs for errors:
```bash
# PythonAnywhere
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Heroku
heroku logs --tail

# VPS
sudo journalctl -u muscle-hustle -f
```

## Image Storage Considerations

### Database Size

With base64 encoding:
- Profile pictures: ~30-70 KB each
- Exercise images: ~70-200 KB each
- Progress photos: ~70-200 KB each

**Estimated storage:**
- 1,000 users with profile pics: ~50 MB
- 100 exercises with images: ~15 MB
- 10,000 progress entries with photos: ~1.5 GB

### MongoDB Limits

- **Document Size**: 16 MB max (plenty for images)
- **Database Size**: Depends on your plan
  - Free tier: 512 MB
  - Paid tiers: Unlimited

### Optimization Tips

1. **Resize images before upload** (already implemented)
2. **Use JPEG compression** (already implemented at 85%)
3. **Monitor database size** regularly
4. **Upgrade plan** if needed

## Security Checklist

### Before Going Live

- [ ] Change SECRET_KEY from default
- [ ] Change admin password from default
- [ ] Set FLASK_ENV=production
- [ ] Use HTTPS (SSL certificate)
- [ ] Restrict MongoDB network access
- [ ] Use strong database passwords
- [ ] Enable MongoDB authentication
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Disable debug mode
- [ ] Review error handling
- [ ] Set up monitoring/alerts

### MongoDB Security

1. **Enable Authentication**
   - Already enabled in Atlas
   - Required for production

2. **Network Access**
   - Whitelist specific IPs
   - Don't use 0.0.0.0/0 in production

3. **User Permissions**
   - Use read/write user, not admin
   - Separate users for different environments

4. **Connection String**
   - Never commit to Git
   - Use environment variables
   - Rotate passwords regularly

## Backup Strategy

### MongoDB Backups

#### Option 1: MongoDB Atlas Automated Backups
- Enabled by default on paid tiers
- Point-in-time recovery
- Automatic snapshots

#### Option 2: Manual Backups
```bash
# Export database
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/muscle_hustle" --out=backup

# Import database
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/muscle_hustle" backup/muscle_hustle
```

#### Option 3: Scheduled Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="$MONGO_URI" --out="backups/backup_$DATE"
# Upload to S3 or other storage
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup.sh
```

## Monitoring

### Application Monitoring

1. **Error Tracking**
   - Set up Sentry or similar
   - Monitor error logs

2. **Performance Monitoring**
   - Track response times
   - Monitor database queries

3. **Uptime Monitoring**
   - Use UptimeRobot or Pingdom
   - Set up alerts

### Database Monitoring

1. **MongoDB Atlas Monitoring**
   - View metrics in Atlas dashboard
   - Set up alerts for:
     - High CPU usage
     - High memory usage
     - Slow queries
     - Connection limits

2. **Storage Monitoring**
   - Track database size growth
   - Monitor collection sizes
   - Plan for scaling

## Scaling Considerations

### When to Scale

- Database size approaching plan limit
- Slow query performance
- High CPU/memory usage
- Many concurrent users

### Scaling Options

1. **Vertical Scaling**
   - Upgrade MongoDB plan
   - Increase server resources

2. **Horizontal Scaling**
   - MongoDB sharding (paid tiers)
   - Load balancing
   - CDN for static assets

3. **Optimization**
   - Add database indexes
   - Optimize queries
   - Cache frequently accessed data
   - Compress images more

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```
Error: MongoDB Connection FAILED!
```
**Solution:**
- Check MONGO_URI is correct
- Verify network access in Atlas
- Check database user credentials

#### 2. Images Not Displaying
```
Images show as broken
```
**Solution:**
- Check image_data exists in database
- Verify base64 encoding is correct
- Check browser console for errors

#### 3. Large Database Size
```
Database approaching size limit
```
**Solution:**
- Review image sizes
- Increase compression
- Upgrade MongoDB plan
- Archive old data

#### 4. Slow Performance
```
Pages loading slowly
```
**Solution:**
- Check database indexes
- Monitor query performance
- Optimize image sizes
- Add caching

## Rollback Plan

If deployment fails:

1. **Keep old version running**
2. **Test new version separately**
3. **Have database backup ready**
4. **Document rollback steps**

### Rollback Steps

1. **Stop new application**
   ```bash
   sudo systemctl stop muscle-hustle
   ```

2. **Restore database backup** (if needed)
   ```bash
   mongorestore --uri="$MONGO_URI" backup/
   ```

3. **Deploy previous version**
   ```bash
   git checkout previous-version
   sudo systemctl start muscle-hustle
   ```

## Support

### Getting Help

- Check error logs first
- Review documentation
- Check MongoDB Atlas status
- Contact support if needed

### Useful Commands

```bash
# Check application status
sudo systemctl status muscle-hustle

# View logs
sudo journalctl -u muscle-hustle -n 100

# Restart application
sudo systemctl restart muscle-hustle

# Check MongoDB connection
python -c "from src.database import test_connection; print(test_connection())"

# Check database size
mongo "$MONGO_URI" --eval "db.stats()"
```

## Summary

✅ **Set environment variables**
✅ **Configure MongoDB Atlas**
✅ **Deploy application**
✅ **Initialize database**
✅ **Change default passwords**
✅ **Test all features**
✅ **Set up monitoring**
✅ **Configure backups**
✅ **Enable security measures**

Your application is now ready for production with all images stored securely in MongoDB!
