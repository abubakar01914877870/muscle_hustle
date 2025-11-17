# Technology Stack

## Backend

- **Framework**: Flask (Python web framework)
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Database**: MongoDB with PyMongo driver
- **Image Processing**: Pillow (PIL)
- **Production Server**: Gunicorn

## Frontend

- HTML templates with Jinja2
- Custom CSS (design-system.css, styles.css, progress.css)
- Responsive design

## Database

- **MongoDB Atlas** (cloud-hosted)
- Collections: users, progress_entries, exercises
- Images stored as base64 in database (no filesystem storage)
- Connection via `MONGO_URI` environment variable

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (creates indexes and admin user)
python init_db.py

# Run development server
python run.py

# Seed exercise data
python seed_exercises.py

# Test MongoDB connection
python test_mongodb_connection.py
```

### Production

```bash
# Set environment variables
export MONGO_URI="your_mongodb_connection_string"
export SECRET_KEY="your_secret_key"

# Initialize database
python init_db.py

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Environment Variables

- `MONGO_URI`: MongoDB connection string (required for production)
- `MONGO_DBNAME`: Database name (defaults to "muscle_hustle")
- `SECRET_KEY`: Flask session encryption key (required for production)

## Deployment Targets

- PythonAnywhere (documented)
- Render (documented)
- Any WSGI-compatible platform
