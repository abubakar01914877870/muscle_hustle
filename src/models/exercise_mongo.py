"""
Exercise Model for MongoDB
"""
from datetime import datetime
from bson import ObjectId
import re

class Exercise:
    """Exercise model for MongoDB"""
    
    def __init__(self, exercise_dict):
        """Initialize exercise from MongoDB document"""
        self._id = exercise_dict.get('_id')
        self.name = exercise_dict.get('name')
        self.muscle = exercise_dict.get('muscle')
        self.secondary_muscles = exercise_dict.get('secondary_muscles', [])
        self.equipment = exercise_dict.get('equipment')
        self.difficulty = exercise_dict.get('difficulty')
        self.type = exercise_dict.get('type')
        self.description = exercise_dict.get('description')
        self.instructions = exercise_dict.get('instructions')
        self.reps_sets = exercise_dict.get('reps_sets')
        self.tips = exercise_dict.get('tips')
        self.common_mistakes = exercise_dict.get('common_mistakes')
        self.media_type = exercise_dict.get('media_type', 'image')
        self.image_data = exercise_dict.get('image_data')  # Base64 encoded image
        self.image_type = exercise_dict.get('image_type', 'image/jpeg')
        self.video_url = exercise_dict.get('video_url')
        self.created_by = exercise_dict.get('created_by')
        self.created_at = exercise_dict.get('created_at', datetime.utcnow())
        self.updated_at = exercise_dict.get('updated_at', datetime.utcnow())
    
    @property
    def id(self):
        """Return exercise ID"""
        return str(self._id)
    
    def get_image_url(self):
        """Get data URL for image"""
        if self.image_data:
            return f"data:{self.image_type};base64,{self.image_data}"
        return None
    
    def to_dict(self):
        """Convert exercise to dictionary"""
        return {
            '_id': self._id,
            'name': self.name,
            'muscle': self.muscle,
            'secondary_muscles': self.secondary_muscles,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'type': self.type,
            'description': self.description,
            'instructions': self.instructions,
            'reps_sets': self.reps_sets,
            'tips': self.tips,
            'common_mistakes': self.common_mistakes,
            'media_type': self.media_type,
            'image_data': self.image_data,
            'image_type': self.image_type,
            'video_url': self.video_url,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def find_by_id(db, exercise_id):
        """Find exercise by ID"""
        try:
            exercise_dict = db.exercises.find_one({'_id': ObjectId(exercise_id)})
            if exercise_dict:
                return Exercise(exercise_dict)
        except:
            pass
        return None
    
    @staticmethod
    def find_by_name(db, name, exclude_id=None):
        """Find exercise by name (case-insensitive)
        
        Args:
            db: MongoDB database instance
            name: Exercise name to search for
            exclude_id: Optional exercise ID to exclude from search (for updates)
            
        Returns:
            Exercise document or None
        """
        query = {'name': {'$regex': f'^{re.escape(name.strip())}$', '$options': 'i'}}
        if exclude_id:
            query['_id'] = {'$ne': ObjectId(exclude_id)}
        return db.exercises.find_one(query)
    
    @staticmethod
    def find_all(db, filters=None, search=None):
        """Find all exercises with optional filters"""
        query = {}
        
        if filters:
            if filters.get('muscle'):
                query['muscle'] = {'$in': filters['muscle']}
            if filters.get('equipment'):
                query['equipment'] = {'$in': filters['equipment']}
            if filters.get('difficulty'):
                query['difficulty'] = {'$in': filters['difficulty']}
        
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        
        exercises = []
        for exercise_dict in db.exercises.find(query).sort('name', 1):
            exercises.append(Exercise(exercise_dict))
        return exercises
    
    @staticmethod
    def create(db, **kwargs):
        """Create new exercise
        
        Raises:
            ValueError: If an exercise with the same name already exists
        """
        name = kwargs.get('name', '').strip()
        
        # Check for duplicate name
        if Exercise.find_by_name(db, name):
            raise ValueError(f'An exercise with the name "{name}" already exists. Please use a different name.')
        
        exercise_dict = {
            'name': name,
            'muscle': kwargs.get('muscle'),
            'secondary_muscles': kwargs.get('secondary_muscles', []),
            'equipment': kwargs.get('equipment'),
            'difficulty': kwargs.get('difficulty'),
            'type': kwargs.get('type'),
            'description': kwargs.get('description', ''),
            'instructions': kwargs.get('instructions', ''),
            'reps_sets': kwargs.get('reps_sets', ''),
            'tips': kwargs.get('tips', ''),
            'common_mistakes': kwargs.get('common_mistakes', ''),
            'media_type': kwargs.get('media_type', 'image'),
            'image_data': kwargs.get('image_data'),
            'image_type': kwargs.get('image_type', 'image/jpeg'),
            'video_url': kwargs.get('video_url'),
            'created_by': kwargs.get('created_by'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.exercises.insert_one(exercise_dict)
        exercise_dict['_id'] = result.inserted_id
        return Exercise(exercise_dict)
    
    @staticmethod
    def update(db, exercise_id, update_data):
        """Update exercise by ID
        
        Raises:
            ValueError: If updating to a name that already exists
        """
        try:
            # Check for duplicate name if name is being updated
            if 'name' in update_data:
                name = update_data['name'].strip()
                existing = Exercise.find_by_name(db, name, exclude_id=exercise_id)
                if existing:
                    raise ValueError(f'An exercise with the name "{name}" already exists. Please use a different name.')
                update_data['name'] = name
            
            update_data['updated_at'] = datetime.utcnow()
            db.exercises.update_one(
                {'_id': ObjectId(exercise_id)},
                {'$set': update_data}
            )
            return True
        except ValueError:
            raise
        except Exception as e:
            print(f"Error updating exercise: {e}")
            return False
    
    @staticmethod
    def delete(db, exercise_id):
        """Delete exercise by ID"""
        try:
            db.exercises.delete_one({'_id': ObjectId(exercise_id)})
            return True
        except:
            return False
    
    @staticmethod
    def import_from_wger(db, wger_data: dict, exercise_info: dict):
        """
        Import exercise from Wger API data
        
        Args:
            db: MongoDB database instance
            wger_data: Basic exercise data from /exercise/ endpoint
            exercise_info: Detailed info from /exerciseinfo/ endpoint
            
        Returns:
            Exercise object or None
        """
        try:
            wger_id = wger_data.get('id')
            
            # Check if already imported
            existing = db.exercises.find_one({'wger_id': wger_id})
            if existing:
                return None  # Already imported
            
            # Extract name from translations array
            translations = exercise_info.get('translations', [])
            if translations and len(translations) > 0:
                name = translations[0].get('name', f"Exercise {wger_id}")
                description = translations[0].get('description', '')
            else:
                name = f"Exercise {wger_id}"
                description = ''
            
            # Map category to muscle group
            category_data = exercise_info.get('category', {})
            if isinstance(category_data, dict):
                muscle = category_data.get('name', 'Other')
            else:
                muscle = 'Other'
            
            # Map equipment
            equipment_data = exercise_info.get('equipment', [])
            if equipment_data and isinstance(equipment_data[0], dict):
                equipment = equipment_data[0].get('name', 'Bodyweight')
            else:
                equipment = 'Bodyweight'
            
            # Create exercise document
            exercise_dict = {
                'wger_id': wger_id,  # Store Wger ID for duplicate prevention
                'name': name,
                'muscle': muscle,
                'secondary_muscles': [],
                'equipment': equipment,
                'difficulty': 'Intermediate',  # Default
                'type': 'Strength',  # Default
                'description': description,
                'instructions': description,  # Same as description for Wger
                'reps_sets': '3 sets x 8-12 reps',  # Default
                'tips': '',
                'common_mistakes': '',
                'media_type': 'image',
                'image_data': None,
                'image_type': 'image/jpeg',
                'video_url': None,
                'created_by': 'wger_import',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = db.exercises.insert_one(exercise_dict)
            exercise_dict['_id'] = result.inserted_id
            return Exercise(exercise_dict)
            
        except Exception as e:
            print(f"Error importing exercise from Wger: {e}")
            return None
    
    def __repr__(self):
        return f'<Exercise {self.name}>'
