# Project Structure

## Directory Layout

```
muscle-hustle/
├── src/                          # Main application package
│   ├── app.py                    # Application factory and blueprint registration
│   ├── config.py                 # Configuration classes (Dev/Prod)
│   ├── database.py               # MongoDB connection and initialization
│   ├── models/                   # Data models
│   │   ├── user_mongo.py         # User model with Flask-Login integration
│   │   ├── exercise_mongo.py     # Exercise model
│   │   └── progress_mongo.py     # Progress tracking model
│   ├── routes/                   # Blueprint route handlers
│   │   ├── auth.py               # Authentication (signup, login, logout)
│   │   ├── main.py               # Main routes (home)
│   │   ├── admin.py              # Admin dashboard and user management
│   │   ├── profile.py            # User profile management
│   │   ├── progress.py           # Progress tracking
│   │   └── exercises.py          # Exercise library
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base template with navigation
│   │   ├── admin/                # Admin templates
│   │   ├── exercises/            # Exercise templates
│   │   ├── profile/              # Profile templates
│   │   └── progress/             # Progress templates
│   ├── static/                   # Static assets
│   │   ├── *.css                 # Stylesheets
│   │   └── uploads/              # User-uploaded files (legacy)
│   └── utils/                    # Utility modules
│       └── image_handler.py      # Image processing utilities
├── docs/                         # Documentation
├── init_db.py                    # Database initialization script
├── seed_exercises.py             # Exercise data seeding
├── run.py                        # Development server entry point
├── wsgi.py                       # Production WSGI entry point
└── requirements.txt              # Python dependencies
```

## Architecture Patterns

### Blueprint Organization

- Each feature area has its own blueprint (auth, admin, profile, progress, exercises)
- Blueprints registered in `src/app.py`
- Routes use relative imports from parent package

### Model Pattern

- Models are classes that wrap MongoDB documents
- Static methods for CRUD operations (find_by_id, create, update, delete)
- Instance methods for business logic (calculate_bmi, check_password)
- All models accept a dictionary from MongoDB and expose properties

### Database Access

- `get_db()` returns database instance from Flask's `g` object
- Connection pooling handled by PyMongo
- Database passed explicitly to model methods (no global state)

### Image Storage

- Images stored as base64 strings in MongoDB
- No filesystem dependencies for user uploads
- Data URLs generated on-demand: `data:{mime_type};base64,{data}`

### Template Structure

- `base.html` provides layout and navigation
- Feature templates extend base and use blocks
- Flash messages for user feedback

## Naming Conventions

- Files: snake_case (user_mongo.py, progress.py)
- Classes: PascalCase (User, Exercise)
- Functions/methods: snake_case (find_by_id, get_db)
- Routes: kebab-case URLs (/change-password)
- Templates: snake_case (edit_profile.html)
