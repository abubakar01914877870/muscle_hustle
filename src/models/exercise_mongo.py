"""
Exercise Model for MongoDB
"""
from datetime import datetime
from bson import ObjectId

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
        self.image_filename = exercise_dict.get('image_filename')
        self.video_url = exercise_dict.get('video_url')
        self.images = exercise_dict.get('images', [])
        self.created_by = exercise_dict.get('created_by')
        self.created_at = exercise_dict.get('created_at', datetime.utcnow())
        self.updated_at = exercise_dict.get('updated_at', datetime.utcnow())
    
    @property
    def id(self):
        """Return exercise ID"""
        return str(self._id)
    
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
            'image_filename': self.image_filename,
            'video_url': self.video_url,
            'images': self.images,
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
        """Create new exercise"""
        exercise_dict = {
            'name': kwargs.get('name'),
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
            'image_filename': kwargs.get('image_filename'),
            'video_url': kwargs.get('video_url'),
            'images': kwargs.get('images', []),
            'created_by': kwargs.get('created_by'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.exercises.insert_one(exercise_dict)
        exercise_dict['_id'] = result.inserted_id
        return Exercise(exercise_dict)
    
    @staticmethod
    def update(db, exercise_id, update_data):
        """Update exercise by ID"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            db.exercises.update_one(
                {'_id': ObjectId(exercise_id)},
                {'$set': update_data}
            )
            return True
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
    
    def __repr__(self):
        return f'<Exercise {self.name}>'
