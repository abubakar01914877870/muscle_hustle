# Render.com Deployment Checklist

## Before You Start

- [ ] Code pushed to GitHub
- [ ] MongoDB Atlas account created
- [ ] Render.com account created

## Step 1: Prepare Files (2 minutes)

- [ ] `render.yaml` file created ✅ (already done)
- [ ] `gunicorn` added to requirements.txt ✅ (already done)
- [ ] `wsgi.py` exists in project root
- [ ] Push to GitHub:
  ```bash
  git add .
  git commit -m "Prepare for Render deployment"
  git push origin main
  ```

## Step 2: MongoDB Atlas Setup (3 minutes)

- [ ] Go to https://cloud.mongodb.com/
- [ ] Get connection string from "Connect" button
- [ ] Go to **Network Access**
- [ ] Click **"Add IP Address"**
- [ ] Select **"Allow Access from Anywhere"** (0.0.0.0/0)
- [ ] Click **"Confirm"**
- [ ] Wait 1-2 minutes for changes to apply

## Step 3: Create Render Service (5 minutes)

- [ ] Go to https://render.com/
- [ ] Sign up/Login with GitHub
- [ ] Click **"New +"** → **"Web Service"**
- [ ] Connect your GitHub repository
- [ ] Configure settings:
  - Name: `muscle-hustle`
  - Branch: `main`
  - Runtime: `Python 3`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn wsgi:app`
  - Instance Type: **Free**

## Step 4: Add Environment Variables (2 minutes)

Add these in the Environment section:

- [ ] `MONGO_URI` = `mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle`
- [ ] `MONGO_DBNAME` = `muscle_hustle`
- [ ] `SECRET_KEY` = Click "Generate" button
- [ ] `FLASK_ENV` = `production`
- [ ] `PYTHON_VERSION` = `3.11.0`

**Important:** Use YOUR actual MongoDB connection string!

## Step 5: Deploy (10 minutes)

- [ ] Click **"Create Web Service"**
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check logs for "Build successful!"
- [ ] Note your app URL (e.g., https://muscle-hustle.onrender.com)

## Step 6: Initialize Database (2 minutes)

- [ ] Go to your service dashboard
- [ ] Click **"Shell"** tab
- [ ] Run: `python init_db.py`
- [ ] Verify you see: "✅ MongoDB Connection SUCCESSFUL!"
- [ ] Verify you see: "✅ Admin user created"

## Step 7: Test Application (5 minutes)

- [ ] Visit your app URL
- [ ] Click "Login"
- [ ] Login with: super@admin.com / 1234qa
- [ ] Go to Profile → Change Password
- [ ] Set new strong password
- [ ] Test uploading profile picture
- [ ] Test adding exercise with image
- [ ] Test adding progress entry

## Step 8: Post-Deployment (Optional)

- [ ] Add custom domain (if you have one)
- [ ] Set up monitoring/alerts
- [ ] Configure database backups
- [ ] Update documentation with live URL

## Troubleshooting

### Build Failed?
- Check requirements.txt has all dependencies
- Check logs in Render dashboard
- Verify Python version compatibility

### MongoDB Connection Failed?
- Check Network Access in MongoDB Atlas
- Verify 0.0.0.0/0 is whitelisted
- Check MONGO_URI environment variable
- Verify MongoDB cluster is active

### App Not Loading?
- Check logs in Render dashboard
- Verify all environment variables are set
- Check wsgi.py exists
- Wait 30-60 seconds (free tier cold start)

## Important URLs

- **Your App**: https://[your-service-name].onrender.com
- **Render Dashboard**: https://dashboard.render.com/
- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Documentation**: See RENDER_DEPLOYMENT.md

## Quick Reference

### View Logs
Render Dashboard → Your Service → Logs tab

### Restart Service
Render Dashboard → Your Service → Manual Deploy → Deploy latest commit

### Update Environment Variables
Render Dashboard → Your Service → Environment tab

### Access Shell
Render Dashboard → Your Service → Shell tab

## Success Criteria

✅ Build completed successfully
✅ Service is running
✅ MongoDB connection working
✅ Can login to application
✅ Can upload images
✅ All features working

## Total Time: ~30 minutes

---

**Need Help?**
- See detailed guide: `RENDER_DEPLOYMENT.md`
- Render docs: https://render.com/docs
- MongoDB docs: https://docs.mongodb.com/

**Deployment Date:** _______________
**App URL:** _______________
**Admin Email:** super@admin.com
**Admin Password:** _______________ (changed from default)
