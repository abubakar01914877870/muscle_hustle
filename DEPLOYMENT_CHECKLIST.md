# PythonAnywhere Deployment Checklist

## Pre-Deployment
- [ ] Create PythonAnywhere account
- [ ] Push code to Git repository (or prepare for manual upload)
- [ ] Generate a strong SECRET_KEY

## Deployment Steps

### 1. Upload Code
- [ ] Clone repository or upload files to PythonAnywhere
- [ ] Navigate to project directory

### 2. Setup Environment
```bash
cd muscle_hustle
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

### 3. Configure Web App
- [ ] Go to Web tab
- [ ] Add new web app (Manual configuration, Python 3.10)
- [ ] Configure WSGI file (use content from `wsgi.py`)
- [ ] Update username in WSGI file: `/home/YOURUSERNAME/muscle_hustle`
- [ ] Set SECRET_KEY in WSGI file
- [ ] Set virtualenv path: `/home/YOURUSERNAME/muscle_hustle/venv`
- [ ] Add static files mapping:
  - URL: `/static/`
  - Directory: `/home/YOURUSERNAME/muscle_hustle/src/static/`

### 4. Test & Launch
- [ ] Click "Reload" button
- [ ] Visit your site: `https://yourusername.pythonanywhere.com`
- [ ] Test login with admin account
- [ ] Change admin password immediately
- [ ] Test user registration
- [ ] Test profile features
- [ ] Test admin features

## Post-Deployment
- [ ] Change default admin password
- [ ] Create regular database backups
- [ ] Monitor error logs
- [ ] Test all features thoroughly

## Quick Commands

### Access Bash Console
```bash
cd muscle_hustle
source venv/bin/activate
```

### Update App
```bash
git pull origin main
# Reload web app from Web tab
```

### Backup Database
```bash
cp users.db users_backup_$(date +%Y%m%d).db
```

### View Logs
Check the error log link in the Web tab

## Important URLs
- Your app: `https://yourusername.pythonanywhere.com`
- Admin login: `https://yourusername.pythonanywhere.com/login`
- PythonAnywhere dashboard: `https://www.pythonanywhere.com/user/yourusername/`

## Default Admin Credentials
**⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN**
- Email: super@admin.com
- Password: 1234qa

## Need Help?
- Read: `PYTHONANYWHERE_DEPLOYMENT.md`
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Forums: https://www.pythonanywhere.com/forums/
