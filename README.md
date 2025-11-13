# Muscle Hustle - Fitness Tracking Application

A comprehensive Flask-based fitness tracking application with user authentication, profile management, and admin features.

## Features

### Authentication
- User registration with email validation
- Secure password hashing using Werkzeug
- User login with "remember me" functionality
- Session management with Flask-Login
- Protected routes requiring authentication

### User Profile
- Comprehensive fitness profile with personal information
- Physical measurements (height, weight, target weight)
- BMI calculation
- Fitness goals and activity levels
- Health information and dietary restrictions
- Profile editing and password management

### Admin Features
- Role-based access control (Admin/User)
- User management dashboard
- Edit and delete users
- Promote/demote admin privileges

### UI/UX
- Responsive design with modern CSS
- Flash messages for user feedback
- Organized profile sections
- Easy navigation

## Setup Instructions

### First Time Setup (Development)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python init_db.py
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

### Production Deployment

⚠️ **IMPORTANT**: See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for safe deployment procedures.

**Quick steps:**
1. Backup database first!
2. Run migration: `python migrate_add_profile_picture.py`
3. Update code: `git pull`
4. Restart application

**Never use `reset_db.py` in production!**

## Database Management

### For Development
- **Initialize Database**: `python init_db.py` - Creates tables and admin user if needed (preserves existing data)
- **Reset Database**: `python reset_db.py` - ⚠️ WARNING: Deletes all data (development only!)

### For Production
- **Migrate Database**: `python migrate_add_profile_picture.py` - Safely adds new columns without data loss
- **Never use reset_db.py in production!** - See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

### Database Backup
```bash
# Always backup before changes
cp src/instance/users.db src/instance/users_backup_$(date +%Y%m%d).db
```

4. **Access the app:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

### Sign Up
- Navigate to `/signup` or click "Sign Up" in the navigation
- Enter username, email, and password (minimum 6 characters)
- Passwords are securely hashed before storage

### Login
- Navigate to `/login` or click "Login" in the navigation
- Enter your username and password
- Check "Remember me" to stay logged in across sessions

### Logout
- Click "Logout" in the navigation when authenticated

## Project Structure

```
flask-auth-app/
├── src/
│   ├── app.py              # Application factory
│   ├── models/
│   │   └── user.py         # User model with password hashing
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   └── main.py         # Main routes
│   ├── templates/
│   │   ├── base.html       # Base template
│   │   ├── login.html      # Login page
│   │   ├── register.html   # Registration page
│   │   └── home.html       # Home page
│   └── static/
│       └── styles.css      # Styling
├── instance/
│   └── users.db            # SQLite database (created automatically)
├── config.py               # Configuration settings
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
└── README.md
```

## Security Features

- Passwords are hashed using Werkzeug's security functions
- Session management with Flask-Login
- CSRF protection through Flask forms
- Secure session cookies
- Input validation on both client and server side

## Configuration

Set environment variables for production:
- `SECRET_KEY`: Secret key for session encryption
- `DATABASE_URL`: Database connection string (defaults to SQLite)

## License

MIT License


## Deployment

### PythonAnywhere Deployment

This app is ready to deploy on PythonAnywhere.

**📚 Deployment Guides:**
- **[PYTHONANYWHERE_GUIDE.md](PYTHONANYWHERE_GUIDE.md)** - Complete PythonAnywhere deployment guide
- **[PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md)** - Initial setup guide
- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - Safe update procedures
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Quick checklist

#### Quick Start
1. Create account at https://www.pythonanywhere.com/
2. Upload code or clone from Git
3. Set up virtual environment and install dependencies
4. Configure WSGI file (template provided in `wsgi.py`)
5. Set virtualenv path and static files
6. Reload and test

Your app will be live at: `https://yourusername.pythonanywhere.com`

#### Updating Production
```bash
# 1. Find database location
python find_database.py

# 2. Backup database
cp instance/users.db instance/users_backup_$(date +%Y%m%d).db

# 3. Run migration
python migrate_add_profile_picture.py

# 4. Reload web app from Web tab
```

### Default Admin Account
- Email: `super@admin.com`
- Password: `1234qa`
- **⚠️ CHANGE PASSWORD IMMEDIATELY AFTER DEPLOYMENT**

## Files Included

- `PYTHONANYWHERE_DEPLOYMENT.md` - Complete deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `wsgi.py` - WSGI configuration template for PythonAnywhere
- `ADMIN_GUIDE.md` - Admin features documentation
- `PROFILE_GUIDE.md` - User profile documentation

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For deployment issues, check:
- PythonAnywhere Help: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
