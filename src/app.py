import os
from flask import Flask, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from .database import init_db, get_db
from .models.user_mongo import User
from .routes.auth import auth
from .routes.main import main
from .routes.admin import admin
from .routes.profile import profile
from .routes.progress import progress_bp
from .routes.exercises import exercises_bp
from .routes.blog import blog
from .routes.admin_blog import admin_blog

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI') or "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"
app.config['MONGO_DBNAME'] = "muscle_hustle"

# Custom Filters
from markupsafe import Markup, escape

@app.template_filter('nl2br')
def nl2br_filter(s):
    if not s:
        return ""
    return Markup(str(escape(s)).replace('\n', '<br>\n'))

# CSRF Protection
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable CSRF by default
csrf = CSRFProtect(app)

# Enable CSRF only for non-API routes
@app.before_request
def enable_csrf_for_web():
    if not request.path.startswith('/api/'):
        csrf.protect()

# CORS Configuration for Mobile API
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Configure specific origins in production
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize MongoDB
init_db(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    return User.find_by_id(db, user_id)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(admin)
app.register_blueprint(profile)
app.register_blueprint(progress_bp)
app.register_blueprint(exercises_bp)
app.register_blueprint(blog)
app.register_blueprint(admin_blog)
from .routes.admin_gym import admin_gym
app.register_blueprint(admin_gym)
from .routes.gym import gym_bp
app.register_blueprint(gym_bp)
from .routes.trainer import trainer
app.register_blueprint(trainer)
from .routes.admin_trainer import admin_trainer
app.register_blueprint(admin_trainer)

from .routes.planner import planner_bp
app.register_blueprint(planner_bp)

from .routes.admin_import import admin_import_bp
app.register_blueprint(admin_import_bp)

from .routes.mobile import mobile_bp
app.register_blueprint(mobile_bp)

# Register API blueprints
from .routes.api.api_auth import bp as api_auth_bp
from .routes.api.api_workouts import bp as api_workouts_bp
from .routes.api.api_exercises import bp as api_exercises_bp
from .routes.api.api_progress import bp as api_progress_bp
from .routes.api.api_diet import bp as api_diet_bp
from .routes.api.api_plans import bp as api_plans_bp

app.register_blueprint(api_auth_bp)
app.register_blueprint(api_workouts_bp)
app.register_blueprint(api_exercises_bp)
app.register_blueprint(api_progress_bp)
app.register_blueprint(api_diet_bp)
app.register_blueprint(api_plans_bp)

if __name__ == '__main__':
    app.run(debug=True)