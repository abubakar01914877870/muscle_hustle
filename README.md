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

## Environment Setup

It is recommended to use a virtual environment to manage dependencies.

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the virtual environment:**
    - On Linux/macOS:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

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

**Quick steps:**
1. Set MongoDB connection string via environment variable
2. Initialize database: `python init_db.py`
3. Update code: `git pull`
4. Restart application

## Database Management

### MongoDB Configuration
The application uses MongoDB for data storage. Configure via environment variables:
- `MONGO_URI`: MongoDB connection string (defaults to development cluster)
- `MONGO_DBNAME`: Database name (defaults to "muscle_hustle")

### Connection Protocol
The application tests the MongoDB connection on startup and displays:
- ✅ Success message with connection details
- ❌ Error message with troubleshooting steps (exits if connection fails)

See [docs/DATABASE_CONNECTION.md](docs/DATABASE_CONNECTION.md) for detailed connection protocol.

### Initialize Database
```bash
python init_db.py
```
This creates indexes and a default admin user if needed.

### Database Collections
- **users**: User accounts with authentication and profiles
- **progress_entries**: Fitness progress tracking with photos and measurements

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
muscle-hustle/
├── src/
│   ├── app.py              # Application factory
│   ├── database.py         # MongoDB connection
│   ├── config.py           # Configuration settings
│   ├── models/
│   │   ├── user_mongo.py   # User model with MongoDB
│   │   └── progress_mongo.py # Progress tracking model
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   ├── main.py         # Main routes
│   │   ├── admin.py        # Admin routes
│   │   ├── profile.py      # Profile routes
│   │   └── progress.py     # Progress tracking routes
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, uploads
├── docs/                   # Documentation
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
- `MONGO_URI`: MongoDB connection string
- `MONGO_DBNAME`: MongoDB database name (defaults to "muscle_hustle")

## License

MIT License


## Deployment

### PythonAnywhere Deployment

This app is ready to deploy on PythonAnywhere.

**📚 Documentation:**
- See [docs/](docs/) folder for all guides and documentation
- MongoDB migration guide available in docs/

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
# 1. Set MongoDB connection
export MONGO_URI="your_mongodb_connection_string"

# 2. Initialize database (creates indexes and admin user)
python init_db.py

# 3. Reload web app from Web tab
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


## Mobile APP 

When app open it will opean a screen day wise. 7 day 7 screen. it will show that day excerise, that day diate food and other information that need to care off. 

When diatecian plan a diate he will plan for 7 days  diffrently. 