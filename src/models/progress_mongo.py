"""
Progress Entry Model for MongoDB
"""
from datetime import datetime
from bson import ObjectId

class ProgressEntry:
    """Progress Entry model for MongoDB"""
    
    def __init__(self, entry_dict):
        """Initialize from MongoDB document"""
        self._id = entry_dict.get('_id')
        self.user_id = entry_dict.get('user_id')
        self.weight = entry_dict.get('weight')
        self.body_fat = entry_dict.get('body_fat')
        self.water_intake = entry_dict.get('water_intake')
        self.chest = entry_dict.get('chest')
        self.waist = entry_dict.get('waist')
        self.hips = entry_dict.get('hips')
        self.arms = entry_dict.get('arms')
        self.thighs = entry_dict.get('thighs')
        self.notes = entry_dict.get('notes')
        self.photo_data = entry_dict.get('photo_data')  # Base64 encoded photo
        self.photo_type = entry_dict.get('photo_type', 'image/jpeg')
        self.created_at = entry_dict.get('created_at', datetime.utcnow())
    
    @property
    def id(self):
        """Return entry ID"""
        return str(self._id)
    
    def get_photo_url(self):
        """Get data URL for photo"""
        if self.photo_data:
            return f"data:{self.photo_type};base64,{self.photo_data}"
        return None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self._id),
            'weight': self.weight,
            'body_fat': self.body_fat,
            'water_intake': self.water_intake,
            'chest': self.chest,
            'waist': self.waist,
            'hips': self.hips,
            'arms': self.arms,
            'thighs': self.thighs,
            'notes': self.notes,
            'photo_url': self.get_photo_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def find_by_user(db, user_id):
        """Find all entries for a user"""
        entries = []
        # user_id is stored as string in the database
        for entry_dict in db.progress_entries.find({'user_id': user_id}).sort('created_at', -1):
            entries.append(ProgressEntry(entry_dict))
        return entries
    
    @staticmethod
    def find_by_user_since(db, user_id, since_date):
        """Find entries for a user since a specific date"""
        entries = []
        query = {
            'user_id': user_id,
            'created_at': {'$gte': since_date}
        }
        for entry_dict in db.progress_entries.find(query).sort('created_at', 1):
            entries.append(ProgressEntry(entry_dict))
        return entries
    
    @staticmethod
    def find_by_id(db, entry_id):
        """Find entry by ID"""
        try:
            entry_dict = db.progress_entries.find_one({'_id': ObjectId(entry_id)})
            if entry_dict:
                return ProgressEntry(entry_dict)
        except:
            pass
        return None
    
    @staticmethod
    def create(db, user_id, weight, **kwargs):
        """Create new progress entry"""
        entry_dict = {
            'user_id': user_id,  # Store as string, not ObjectId
            'weight': weight,
            'body_fat': kwargs.get('body_fat'),
            'water_intake': kwargs.get('water_intake'),
            'chest': kwargs.get('chest'),
            'waist': kwargs.get('waist'),
            'hips': kwargs.get('hips'),
            'arms': kwargs.get('arms'),
            'thighs': kwargs.get('thighs'),
            'notes': kwargs.get('notes'),
            'photo_data': kwargs.get('photo_data'),
            'photo_type': kwargs.get('photo_type', 'image/jpeg'),
            'created_at': datetime.utcnow()
        }
        result = db.progress_entries.insert_one(entry_dict)
        entry_dict['_id'] = result.inserted_id
        return ProgressEntry(entry_dict)
    
    @staticmethod
    def delete(db, entry_id):
        """Delete entry by ID"""
        try:
            db.progress_entries.delete_one({'_id': ObjectId(entry_id)})
            return True
        except:
            return False
    
    def __repr__(self):
        return f'<ProgressEntry {self.id} - {self.weight}kg>'
