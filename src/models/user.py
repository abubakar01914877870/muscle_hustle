from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Personal Information
    full_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    
    # Physical Measurements
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    target_weight = db.Column(db.Float)  # in kg
    
    # Fitness Information
    fitness_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    fitness_goal = db.Column(db.String(50))  # weight_loss, muscle_gain, maintenance, endurance
    activity_level = db.Column(db.String(20))  # sedentary, lightly_active, moderately_active, very_active, extremely_active
    
    # Health Information
    medical_conditions = db.Column(db.Text)
    dietary_restrictions = db.Column(db.Text)
    
    # Preferences
    preferred_workout_time = db.Column(db.String(20))  # morning, afternoon, evening
    workout_frequency = db.Column(db.Integer)  # days per week
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def calculate_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None
    
    def calculate_age(self):
        if self.date_of_birth:
            today = datetime.today().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __repr__(self):
        return f'<User {self.email}>'