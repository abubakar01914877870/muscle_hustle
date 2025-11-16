# Quick Deployment Guide - 5 Steps

## Step 1: Set Environment Variables (2 minutes)

```bash
# Linux/Mac
export MONGO_URI="mongodb+srv://user:password@cluster.mongodb.net/"
export MONGO_DBNAME="muscle_hustle"
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Windows
set MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
set MONGO_DBNAME=muscle_hustle
set SECRET_KEY=your-generated-secret-key
```

## Step 2: Install Dependencies (2 minutes)

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

## Step 3: Initialize Database (1 minute)

```bash
python init_db.py
```

This creates:
- Database indexes
- Default admin user (super@admin.com / 1234qa)

## Step 4: Deploy Application (5-10 minutes)

### Option A: PythonAnywhere (Easiest)

1. Upload files to PythonAnywhere
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure WSGI file (see PRODUCTION_DEPLOYMENT.md)
4. Set virtualenv path in Web tab
5. Click "Reload"

### Option B: Heroku

```bash
# Add Procfile
echo "web: gunicorn wsgi:app" > Procfile

# Install gunicorn
pip install gunicorn
pip freeze > requirements.txt

# Deploy
heroku create muscle-hustle
heroku config:set MONGO_URI="your-uri"
heroku config:set MONGO_DBNAME="muscle_hustle"
heroku config:set SECRET_KEY="your-key"
git push heroku main
```

### Option C: VPS

```bash
# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx

# Setup app
cd /var/www
git clone your-repo
cd muscle-hustle
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Configure systemd and nginx (see PRODUCTION_DEPLOYMENT.md)
sudo systemctl start muscle-hustle
sudo systemctl restart nginx
```

## Step 5: Post-Deployment (2 minutes)

1. **Visit your site**: https://your-domain.com
2. **Login**: super@admin.com / 1234qa
3. **Change password**: Go to Profile → Change Password
4. **Test features**:
   - Upload profile picture
   - Add exercise with image
   - Add progress entry

## Done! 🎉

Your application is now live with:
- ✅ MongoDB database
- ✅ Image storage in database
- ✅ User authentication
- ✅ Admin panel
- ✅ Progress tracking
- ✅ Exercise database

## Important Notes

⚠️ **Security:**
- Change admin password immediately
- Use strong SECRET_KEY
- Enable HTTPS
- Restrict MongoDB network access

📊 **Monitoring:**
- Check logs regularly
- Monitor database size
- Set up backups

🔧 **Maintenance:**
- Update dependencies monthly
- Review user activity
- Clean up old data if needed

## Need Help?

See detailed guides:
- `docs/PRODUCTION_DEPLOYMENT.md` - Full deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Complete checklist
- `docs/IMAGE_STORAGE_IN_DB.md` - Image storage details

## Quick Commands

```bash
# Check status
python -c "from src.database import test_connection; print(test_connection())"

# View logs (VPS)
sudo journalctl -u muscle-hustle -f

# Restart (VPS)
sudo systemctl restart muscle-hustle

# Backup database
mongodump --uri="$MONGO_URI" --out=backup
```

---

**Total Time: ~15 minutes** ⏱️

Your Muscle Hustle app is production-ready!
