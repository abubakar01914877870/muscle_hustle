"""
Wger Exercise Adapter

Adapter to integrate Wger API exercises with existing Exercise model interface.
This allows seamless integration without breaking existing code.
"""

from typing import List, Dict, Optional
from src.services.wger_service import WgerService
from bson import ObjectId


class WgerExerciseAdapter:
    """
    Adapter class that wraps Wger API exercise data to match
    the existing Exercise model interface
    """
    
    def __init__(self, wger_data: Dict, exercise_info: Optional[Dict] = None):
        """
        Initialize from Wger API data
        
        Args:
            wger_data: Basic exercise data from /exercise/ endpoint
            exercise_info: Detailed info from /exerciseinfo/ endpoint (optional)
        """
        # Store Wger ID as string to match MongoDB ObjectId behavior
        self._id = str(wger_data.get('id'))
        self.wger_id = wger_data.get('id')
        self.uuid = wger_data.get('uuid')
        
        # Get detailed info if not provided
        if not exercise_info:
            exercise_info = WgerService.get_exercise_info(self.wger_id) or {}
        
        # Extract name from translations array (Wger API structure)
        translations = exercise_info.get('translations', [])
        if translations and len(translations) > 0:
            # Get first translation (usually English)
            self.name = translations[0].get('name', f"Exercise {self.wger_id}")
            self.description = translations[0].get('description', '')
        else:
            self.name = f"Exercise {self.wger_id}"
            self.description = ''
        
        # Extract instructions from description (Wger combines them)
        self.instructions = self.description
        
        # Map category to muscle group
        category_data = exercise_info.get('category', {})
        if isinstance(category_data, dict):
            category_id = category_data.get('id')
            self.muscle = category_data.get('name', self._map_category_to_muscle(category_id))
        else:
            category_id = wger_data.get('category')
            self.muscle = self._map_category_to_muscle(category_id)
        
        self.muscle_group = self.muscle  # Alias for compatibility
        
        # Map muscles from detailed info
        muscles_data = exercise_info.get('muscles', [])
        if muscles_data:
            self.muscles = [m.get('id') for m in muscles_data if isinstance(m, dict)]
        else:
            self.muscles = wger_data.get('muscles', [])
        
        muscles_secondary_data = exercise_info.get('muscles_secondary', [])
        if muscles_secondary_data:
            self.secondary_muscles = [m.get('id') for m in muscles_secondary_data if isinstance(m, dict)]
        else:
            self.secondary_muscles = wger_data.get('muscles_secondary', [])
        
        # Map equipment from detailed info
        equipment_data = exercise_info.get('equipment', [])
        if equipment_data:
            equipment_names = [e.get('name') for e in equipment_data if isinstance(e, dict)]
            self.equipment = equipment_names[0] if equipment_names else 'Bodyweight'
        else:
            equipment_ids = wger_data.get('equipment', [])
            self.equipment = self._map_equipment(equipment_ids)
        
        # Default values for fields not in Wger
        self.difficulty = 'Intermediate'
        self.type = 'Strength'
        self.reps_sets = '3 sets x 8-12 reps'
        self.tips = ''
        self.common_mistakes = ''
        
        # Media
        self.media_type = 'image'
        self.image_data = None
        self.image_type = 'image/jpeg'
        self.video_url = None
        
        # Images from Wger
        images = exercise_info.get('images', [])
        if images:
            self.image_url = images[0].get('image')
        else:
            self.image_url = None
        
        # Metadata
        self.created_by = 'wger'
        self.created_at = wger_data.get('created')
        self.updated_at = wger_data.get('last_update')
        self.variations = wger_data.get('variations')
        self.license_author = exercise_info.get('license_author', wger_data.get('license_author'))
    
    @property
    def id(self):
        """Return exercise ID as string"""
        return self._id
    
    def get_image_url(self):
        """Get image URL"""
        return self.image_url
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            '_id': self._id,
            'wger_id': self.wger_id,
            'name': self.name,
            'muscle': self.muscle,
            'muscle_group': self.muscle_group,
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
            'image_url': self.image_url,
            'video_url': self.video_url,
            'created_by': self.created_by,
            'variations': self.variations
        }
    
    @staticmethod
    def _map_category_to_muscle(category_id: int) -> str:
        """Map Wger category ID to muscle group name"""
        category_map = {
            8: 'Arms',
            9: 'Legs',
            10: 'Abs',
            11: 'Chest',
            12: 'Back',
            13: 'Shoulders',
            14: 'Calves',
            15: 'Cardio'
        }
        return category_map.get(category_id, 'Other')
    
    @staticmethod
    def _map_equipment(equipment_ids: List[int]) -> str:
        """Map Wger equipment IDs to equipment name"""
        equipment_map = {
            1: 'Barbell',
            2: 'SZ-Bar',
            3: 'Dumbbell',
            4: 'Gym mat',
            5: 'Swiss Ball',
            6: 'Pull-up bar',
            7: 'Bodyweight',
            8: 'Bench',
            9: 'Incline bench',
            10: 'Kettlebell'
        }
        
        if not equipment_ids:
            return 'Bodyweight'
        
        # Return first equipment
        return equipment_map.get(equipment_ids[0], 'Other')
    
    @staticmethod
    def find_by_id(db, exercise_id: str):
        """
        Find exercise by ID - checks both MongoDB and Wger API
        
        Args:
            db: MongoDB database instance
            exercise_id: Exercise ID (can be MongoDB ObjectId or Wger ID)
            
        Returns:
            Exercise object or None
        """
        # First try MongoDB for custom exercises
        try:
            from src.models.exercise_mongo import Exercise
            mongo_exercise = Exercise.find_by_id(db, exercise_id)
            if mongo_exercise:
                return mongo_exercise
        except:
            pass
        
        # Try Wger API
        try:
            wger_id = int(exercise_id)
            exercise_info = WgerService.get_exercise_info(wger_id)
            if exercise_info:
                # Get basic exercise data
                exercises_data = WgerService.get_exercises(limit=1000)
                for ex in exercises_data.get('results', []):
                    if ex['id'] == wger_id:
                        return WgerExerciseAdapter(ex, exercise_info)
        except:
            pass
        
        return None
    
    @staticmethod
    def find_all(db=None, filters=None, search=None, limit=100, offset=0):
        """
        Find all exercises - combines MongoDB and Wger API
        
        Args:
            db: MongoDB database instance (optional)
            filters: Filter dict (optional)
            search: Search query (optional)
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of Exercise objects
        """
        exercises = []
        
        # Get Wger exercises
        wger_data = WgerService.get_exercises(limit=limit, offset=offset)
        
        for ex_data in wger_data.get('results', []):
            # Get detailed info for each exercise
            exercise_info = WgerService.get_exercise_info(ex_data['id'])
            if exercise_info:
                adapter = WgerExerciseAdapter(ex_data, exercise_info)
                
                # Apply filters if provided
                if filters:
                    if filters.get('muscle') and adapter.muscle not in filters['muscle']:
                        continue
                    if filters.get('equipment') and adapter.equipment not in filters['equipment']:
                        continue
                
                # Apply search if provided
                if search and search.lower() not in adapter.name.lower():
                    continue
                
                exercises.append(adapter)
        
        # Optionally add MongoDB exercises (for custom user exercises)
        if db is not None:
            try:
                from src.models.exercise_mongo import Exercise
                mongo_exercises = Exercise.find_all(db, filters, search)
                exercises.extend(mongo_exercises)
            except:
                pass
        
        return exercises
    
    def __repr__(self):
        return f'<WgerExercise {self.name}>'
