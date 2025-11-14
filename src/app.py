import os
from flask import Flask
from flask_login import LoginManager
from .database import init_db, get_db
from .models.user_mongo import User
from .routes.auth import auth
from .routes.main import main
from .routes.admin import admin
from .routes.profile import profile
from .routes.progress import progress_bp
from .routes.exercises import exercises_bp

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI') or "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"
app.config['MONGO_DBNAME'] = "muscle_hustle"

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

if __name__ == '__main__':
    app.run(debug=True)