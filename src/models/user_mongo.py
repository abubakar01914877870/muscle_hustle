"""
User Model for MongoDB
"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
from flask_login import UserMixin
import re

def slugify(text):
    """Simple slugify implementation"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

class User(UserMixin):
    """User model for MongoDB"""
    
    def __init__(self, user_dict):
        """Initialize user from MongoDB document"""
        self._id = user_dict.get('_id')
        self.email = user_dict.get('email')
        self.password_hash = user_dict.get('password_hash')
        self.is_admin = user_dict.get('is_admin', False)
        self.profile_picture = user_dict.get('profile_picture')  # Now stores base64 image data
        self.profile_picture_type = user_dict.get('profile_picture_type', 'image/jpeg')
        self.full_name = user_dict.get('full_name')
        self.date_of_birth = user_dict.get('date_of_birth')
        self.gender = user_dict.get('gender')
        self.phone = user_dict.get('phone')
        self.height = user_dict.get('height')
        self.weight = user_dict.get('weight')
        self.target_weight = user_dict.get('target_weight')
        self.fitness_level = user_dict.get('fitness_level')
        self.fitness_goal = user_dict.get('fitness_goal')
        self.activity_level = user_dict.get('activity_level')
        self.medical_conditions = user_dict.get('medical_conditions')
        self.dietary_restrictions = user_dict.get('dietary_restrictions')
        self.preferred_workout_time = user_dict.get('preferred_workout_time')
        self.workout_frequency = user_dict.get('workout_frequency')
        self.created_at = user_dict.get('created_at', datetime.utcnow())
        self.updated_at = user_dict.get('updated_at', datetime.utcnow())
        
        # Slug for trainers
        self.slug = user_dict.get('slug')
        if not self.slug and user_dict.get('is_trainer'):
            self.slug = slugify(self.full_name or self.email.split('@')[0])
        
        # Trainer fields
        self.is_trainer = user_dict.get('is_trainer', False)
        self.trainer_profile = user_dict.get('trainer_profile', {})
    
    def get_id(self):
        """Return user ID for Flask-Login"""
        return str(self._id)
    
    @property
    def id(self):
        """Return user ID"""
        return str(self._id)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def calculate_bmi(self):
        """Calculate BMI"""
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None
    
    def calculate_age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            if isinstance(self.date_of_birth, str):
                dob = datetime.fromisoformat(self.date_of_birth.replace('Z', '+00:00'))
            else:
                dob = self.date_of_birth
            
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None
    
    def get_profile_picture_url(self):
        """Get data URL for profile picture"""
        if self.profile_picture:
            return f"data:{self.profile_picture_type};base64,{self.profile_picture}"
        return None
    
    def get_trainer_specializations(self):
        """Get list of trainer specializations"""
        if self.is_trainer and self.trainer_profile:
            return self.trainer_profile.get('specializations', [])
        return []
    
    def get_trainer_certifications(self):
        """Get list of trainer certifications"""
        if self.is_trainer and self.trainer_profile:
            return self.trainer_profile.get('certifications', [])
        return []
    
    def is_trainer_profile_published(self):
        """Check if trainer profile is published"""
        if self.is_trainer and self.trainer_profile:
            return self.trainer_profile.get('is_published', False)
        return False
    
    def update_trainer_profile(self, db, profile_data):
        """Update trainer profile data"""
        if not self.is_trainer:
            return False
        
        self.trainer_profile = profile_data
        self.updated_at = datetime.utcnow()
        
        try:
            db.users.update_one(
                {'_id': self._id},
                {'$set': {
                    'trainer_profile': self.trainer_profile,
                    'updated_at': self.updated_at
                }}
            )
            return True
        except Exception as e:
            print(f"Error updating trainer profile: {e}")
            return False
    
    @staticmethod
    def find_all_trainers(db, published_only=True):
        """Find all trainers"""
        query = {'is_trainer': True}
        if published_only:
            query['trainer_profile.is_published'] = True
        
        trainers = []
        for user_dict in db.users.find(query):
            trainers.append(User(user_dict))
        return trainers
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            '_id': self._id,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'profile_picture': self.profile_picture,
            'profile_picture_type': self.profile_picture_type,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'phone': self.phone,
            'height': self.height,
            'weight': self.weight,
            'target_weight': self.target_weight,
            'fitness_level': self.fitness_level,
            'fitness_goal': self.fitness_goal,
            'activity_level': self.activity_level,
            'medical_conditions': self.medical_conditions,
            'dietary_restrictions': self.dietary_restrictions,
            'preferred_workout_time': self.preferred_workout_time,
            'workout_frequency': self.workout_frequency,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_trainer': self.is_trainer,
            'trainer_profile': self.trainer_profile,
            'slug': self.slug
        }
    
    @staticmethod
    def find_by_email(db, email):
        """Find user by email"""
        user_dict = db.users.find_one({'email': email})
        if user_dict:
            return User(user_dict)
        return None
    
    @staticmethod
    def find_by_id(db, user_id):
        """Find user by ID"""
        try:
            user_dict = db.users.find_one({'_id': ObjectId(user_id)})
            if user_dict:
                return User(user_dict)
        except:
            pass
        return None
    
    @staticmethod
    def find_by_slug(db, slug):
        """Find user by slug"""
        user_dict = db.users.find_one({'slug': slug})
        if user_dict:
            return User(user_dict)
        return None

    @staticmethod
    def find_all(db):
        """Find all users"""
        users = []
        for user_dict in db.users.find():
            users.append(User(user_dict))
        return users
    
    @staticmethod
    def create(db, email, password, is_admin=False):
        """Create new user"""
        user_dict = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'is_admin': is_admin,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.users.insert_one(user_dict)
        user_dict['_id'] = result.inserted_id
        return User(user_dict)
    
    def save(self, db):
        """Save user to database"""
        self.updated_at = datetime.utcnow()
        # Ensure slug exists for trainers
        if self.is_trainer and not self.slug:
            self.slug = slugify(self.full_name or self.email.split('@')[0])
            
        user_dict = self.to_dict()
        db.users.update_one(
            {'_id': self._id},
            {'$set': user_dict}
        )
    
    @staticmethod
    def update(db, user_id, update_data):
        """Update user by ID"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def delete(db, user_id):
        """Delete user by ID"""
        try:
            db.users.delete_one({'_id': ObjectId(user_id)})
            return True
        except:
            return False
    
    def __repr__(self):
        return f'<User {self.email}>'
