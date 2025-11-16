# Deploy Muscle Hustle to Render.com - Step by Step

## Prerequisites

- GitHub account
- Render.com account (free tier available)
- MongoDB Atlas account
- Your code pushed to GitHub

## Step 1: Prepare Your Repository (5 minutes)

### 1.1 Create Required Files

#### A. Create `render.yaml` (Render Blueprint)

Create a file named `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: muscle-hustle
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: MONGO_URI
        sync: false
      - key: MONGO_DBNAME
        value: muscle_hustle
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
```

#### B. Update `requirements.txt`

Add `gunicorn` to your requirements.txt:

```bash
echo "gunicorn" >> requirements.txt
```

Your requirements.txt should now have:
```
Flask
Flask-Login
Werkzeug
pymongo
dnspython
Pillow
gunicorn
```

#### C. Verify `wsgi.py` exists

Make sure you have `wsgi.py` in your project root:

```python
from src.app import app

if __name__ == "__main__":
    app.run()
```

### 1.2 Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Configure MongoDB Atlas (5 minutes)

### 2.1 Get Your MongoDB Connection String

1. Go to https://cloud.mongodb.com/
2. Click on your cluster
3. Click "Connect"
4. Choose "Connect your application"
5. Copy the connection string
6. It looks like: `mongodb+srv://username:password@cluster.mongodb.net/`

### 2.2 Configure Network Access

1. In MongoDB Atlas, go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"**
4. Enter: `0.0.0.0/0`
5. Description: "Render.com servers"
6. Click **"Confirm"**

**Note:** Render uses dynamic IPs, so you need to allow all IPs. This is safe because MongoDB still requires authentication.

### 2.3 Verify Database User

1. Go to **Database Access**
2. Make sure you have a user with:
   - Username: (e.g., `admin`)
   - Password: (e.g., `1234qa`)
   - Role: **Atlas admin** or **Read and write to any database**

## Step 3: Deploy to Render.com (10 minutes)

### 3.1 Create Render Account

1. Go to https://render.com/
2. Click **"Get Started"**
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### 3.2 Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - If first time: Click "Configure account" and select repositories
   - Find your `muscle-hustle` repository
   - Click **"Connect"**

### 3.3 Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `muscle-hustle` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`

**Instance Type:**
- Select **"Free"** (or paid plan if you prefer)

### 3.4 Add Environment Variables

Scroll down to **Environment Variables** section and add:

| Key | Value |
|-----|-------|
| `MONGO_URI` | `mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle` |
| `MONGO_DBNAME` | `muscle_hustle` |
| `SECRET_KEY` | Click "Generate" button |
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.11.0` |

**Important:** Replace the MongoDB URI with your actual connection string!

### 3.5 Deploy

1. Click **"Create Web Service"** button at the bottom
2. Render will start building your application
3. Wait 5-10 minutes for the build to complete

You'll see logs like:
```
==> Cloning from https://github.com/yourusername/muscle-hustle...
==> Installing dependencies...
==> Build successful!
==> Starting service...
```

## Step 4: Initialize Database (2 minutes)

### 4.1 Access Render Shell

1. Once deployed, go to your service dashboard
2. Click **"Shell"** tab (top menu)
3. This opens a terminal in your deployed app

### 4.2 Run Database Initialization

In the Render shell, run:

```bash
python init_db.py
```

You should see:
```
============================================================
🔧 MONGODB DATABASE INITIALIZATION
============================================================
✅ MongoDB Connection SUCCESSFUL!
✅ Indexes created successfully
✅ Admin user created: super@admin.com / 1234qa
============================================================
```

If you see connection errors, check your MongoDB Network Access settings.

## Step 5: Test Your Application (5 minutes)

### 5.1 Access Your Site

1. Go to your Render dashboard
2. Find your service URL (e.g., `https://muscle-hustle.onrender.com`)
3. Click the URL to open your site

### 5.2 Test Login

1. Click **"Login"**
2. Use default credentials:
   - Email: `super@admin.com`
   - Password: `1234qa`
3. Should successfully log in

### 5.3 Change Admin Password

1. Go to **Profile**
2. Click **"Change Password"**
3. Set a strong password
4. Save changes

### 5.4 Test Features

Test each feature:
- ✅ Upload profile picture
- ✅ Add exercise with image
- ✅ Add exercise with YouTube video
- ✅ Add progress entry with photo
- ✅ View progress chart
- ✅ Admin user management

## Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain

1. In Render dashboard, go to **Settings**
2. Scroll to **Custom Domain**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `musclehustle.com`)

### 6.2 Update DNS

Add these DNS records at your domain registrar:

**For root domain (musclehustle.com):**
```
Type: A
Name: @
Value: [Render's IP - shown in dashboard]
```

**For www subdomain:**
```
Type: CNAME
Name: www
Value: muscle-hustle.onrender.com
```

### 6.3 Enable HTTPS

Render automatically provides free SSL certificates. Just wait a few minutes after adding your domain.

## Troubleshooting

### Issue 1: Build Failed

**Error:** `Could not find a version that satisfies the requirement`

**Solution:**
```bash
# Update requirements.txt with specific versions
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Issue 2: MongoDB Connection Failed

**Error:** `Connection refused` or `Timeout`

**Solution:**
1. Check MongoDB Atlas Network Access
2. Make sure `0.0.0.0/0` is whitelisted
3. Verify MONGO_URI environment variable is correct
4. Check MongoDB cluster is active (not paused)

### Issue 3: Application Crashes

**Error:** `Application failed to start`

**Solution:**
1. Check logs in Render dashboard
2. Verify all environment variables are set
3. Make sure `wsgi.py` exists
4. Check `gunicorn` is in requirements.txt

### Issue 4: Images Not Displaying

**Error:** Images show as broken

**Solution:**
1. Images are stored in MongoDB, not filesystem
2. Check browser console for errors
3. Verify image data exists in database
4. Clear browser cache

### Issue 5: Slow First Load

**Note:** Free tier apps sleep after 15 minutes of inactivity

**Solution:**
- First request after sleep takes 30-60 seconds
- Upgrade to paid plan for always-on service
- Or use a service like UptimeRobot to ping your app every 10 minutes

## Render.com Features

### Auto-Deploy

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys!
```

### View Logs

1. Go to Render dashboard
2. Click **"Logs"** tab
3. See real-time application logs

### Environment Variables

Update environment variables:
1. Go to **Environment** tab
2. Edit or add variables
3. Click **"Save Changes"**
4. Service automatically restarts

### Manual Deploy

Force a new deployment:
1. Go to **Manual Deploy** section
2. Click **"Deploy latest commit"**

## Monitoring

### Check Application Health

Render provides:
- **Metrics**: CPU, Memory, Request count
- **Logs**: Real-time application logs
- **Events**: Deployment history

Access from your service dashboard.

### Set Up Alerts

1. Go to **Settings**
2. Scroll to **Health Check Path**
3. Set to `/` (home page)
4. Render will monitor and alert if down

## Backup Strategy

### Database Backups

MongoDB Atlas provides automatic backups:
1. Go to MongoDB Atlas
2. Click **"Backup"** tab
3. Enable **"Continuous Backup"** (paid tiers)
4. Or use **"Scheduled Snapshots"**

### Manual Backup

```bash
# From your local machine
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/muscle_hustle" --out=backup

# Restore if needed
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/muscle_hustle" backup/muscle_hustle
```

## Scaling

### Upgrade Instance

1. Go to **Settings**
2. Scroll to **Instance Type**
3. Choose larger instance:
   - **Starter**: $7/month (512 MB RAM)
   - **Standard**: $25/month (2 GB RAM)
   - **Pro**: $85/month (4 GB RAM)

### Database Scaling

Upgrade MongoDB Atlas plan:
1. Go to MongoDB Atlas
2. Click cluster name
3. Click **"Edit Configuration"**
4. Choose larger tier

## Cost Estimate

### Free Tier
- **Render**: Free (with limitations)
- **MongoDB Atlas**: Free (512 MB)
- **Total**: $0/month

**Limitations:**
- App sleeps after 15 min inactivity
- 750 hours/month free
- Slower performance

### Paid Tier (Recommended for Production)
- **Render Starter**: $7/month
- **MongoDB M10**: $10/month
- **Total**: $17/month

**Benefits:**
- Always-on
- Better performance
- Automatic backups
- More storage

## Security Checklist

- ✅ Change default admin password
- ✅ Use strong SECRET_KEY (auto-generated by Render)
- ✅ HTTPS enabled (automatic)
- ✅ MongoDB authentication enabled
- ✅ Environment variables secured
- ✅ Regular backups configured

## Maintenance

### Update Dependencies

```bash
pip install --upgrade flask flask-login pymongo pillow
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Monitor Database Size

1. Go to MongoDB Atlas
2. Check **Metrics** tab
3. Monitor storage usage
4. Upgrade plan if needed

### Review Logs

Check Render logs weekly:
1. Look for errors
2. Monitor performance
3. Check for security issues

## Support

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com/
- Status: https://status.render.com/

### MongoDB Support
- Documentation: https://docs.mongodb.com/
- Support: https://support.mongodb.com/

## Quick Commands

### View Logs
```bash
# In Render dashboard, click "Logs" tab
```

### Restart Service
```bash
# In Render dashboard, click "Manual Deploy" → "Clear build cache & deploy"
```

### Access Shell
```bash
# In Render dashboard, click "Shell" tab
```

### Check Database
```bash
# In Render shell
python -c "from src.database import test_connection; print(test_connection())"
```

## Summary

✅ **Deployment Complete!**

Your Muscle Hustle app is now live at:
- **URL**: https://muscle-hustle.onrender.com
- **Admin**: super@admin.com / [your-new-password]
- **Database**: MongoDB Atlas
- **Images**: Stored in MongoDB

**Next Steps:**
1. Change admin password
2. Test all features
3. Add custom domain (optional)
4. Set up monitoring
5. Configure backups

**Total Time:** ~30 minutes
**Cost:** Free (or $17/month for production)

🎉 **Your app is live!**
