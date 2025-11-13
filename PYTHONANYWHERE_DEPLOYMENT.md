# Deploying Muscle Hustle to PythonAnywhere

## Prerequisites
- A PythonAnywhere account (free tier works fine)
- Your code ready to deploy

## Step-by-Step Deployment Guide

### 1. Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Sign up for a free account
3. Verify your email

### 2. Upload Your Code

#### Option A: Using Git (Recommended)
1. Push your code to GitHub/GitLab/Bitbucket
2. In PythonAnywhere, open a Bash console
3. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/muscle_hustle.git
   cd muscle_hustle
   ```

#### Option B: Upload Files Manually
1. Go to the "Files" tab in PythonAnywhere
2. Create a new directory: `muscle_hustle`
3. Upload all your project files

### 3. Set Up Virtual Environment
In a Bash console:
```bash
cd muscle_hustle
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Configure Web App

1. Go to the "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10

### 6. Configure WSGI File

1. In the Web tab, click on the WSGI configuration file link
2. Delete all content and replace with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/muscle_hustle'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-production-secret-key-here'

# Import the Flask app
from src.app import app as application
```

**Important:** Replace `yourusername` with your actual PythonAnywhere username

### 7. Configure Virtual Environment

1. In the Web tab, find the "Virtualenv" section
2. Enter the path to your virtual environment:
   ```
   /home/yourusername/muscle_hustle/venv
   ```

### 8. Configure Static Files

In the Web tab, add static files mapping:
- URL: `/static/`
- Directory: `/home/yourusername/muscle_hustle/src/static/`

### 9. Set Environment Variables (Optional but Recommended)

Create a `.env` file in your project root:
```bash
SECRET_KEY=your-super-secret-production-key-change-this
```

Or set them in the WSGI file as shown in step 6.

### 10. Reload Web App

1. Go to the Web tab
2. Click the green "Reload" button
3. Your app should now be live at: `yourusername.pythonanywhere.com`

## Important Configuration Changes for Production

### Update src/app.py for Production

The app is already configured, but ensure these settings:

```python
# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

### Security Checklist

1. **Change Secret Key**: Set a strong SECRET_KEY environment variable
2. **Change Admin Password**: Log in as admin and change the default password
3. **Database Location**: The SQLite database will be created in your project directory
4. **HTTPS**: PythonAnywhere provides HTTPS by default

## Troubleshooting

### Error: "No module named 'src'"
- Check that your WSGI file has the correct project path
- Ensure the path is added to sys.path

### Error: "Application object must be callable"
- Make sure you're importing `app` correctly in WSGI file
- The line should be: `from src.app import app as application`

### Database Errors
- Run `python init_db.py` in the Bash console
- Check file permissions: `chmod 644 users.db`

### Static Files Not Loading
- Verify static files path in Web tab configuration
- Check that the path is absolute: `/home/yourusername/muscle_hustle/src/static/`

### 500 Internal Server Error
- Check error logs in the Web tab
- Look at the error log file for detailed error messages

## Updating Your App

When you make changes:

1. **If using Git:**
   ```bash
   cd muscle_hustle
   git pull origin main
   ```

2. **If uploading manually:**
   - Upload changed files via Files tab

3. **If database schema changed:**
   ```bash
   python reset_db.py  # WARNING: Deletes all data
   # OR
   python init_db.py   # Safe, preserves data
   ```

4. **Reload the web app:**
   - Go to Web tab and click "Reload"

## Database Backup

Regularly backup your database:
```bash
cp users.db users_backup_$(date +%Y%m%d).db
```

Download backups via the Files tab.

## Free Tier Limitations

- Your app will sleep after inactivity
- Limited CPU time per day
- One web app per account
- Custom domains require paid plan

## Upgrading to Paid Plan

For production use, consider upgrading for:
- Always-on apps (no sleeping)
- More CPU time
- Custom domains
- More storage
- SSH access

## Support

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Help: https://help.pythonanywhere.com/

## Your App URLs

After deployment:
- Main site: `https://yourusername.pythonanywhere.com`
- Admin login: `https://yourusername.pythonanywhere.com/login`
  - Email: super@admin.com
  - Password: 1234qa (CHANGE THIS IMMEDIATELY!)

## Post-Deployment Tasks

1. ✅ Test all functionality
2. ✅ Change admin password
3. ✅ Set strong SECRET_KEY
4. ✅ Test user registration
5. ✅ Test profile editing
6. ✅ Test admin features
7. ✅ Backup database
