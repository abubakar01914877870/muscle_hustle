"""
Diet/Meal Plan Models for MongoDB
"""
from datetime import datetime
from bson import ObjectId

class MealPlan:
    """Model for a daily meal plan"""
    
    def __init__(self, plan_dict):
        self._id = plan_dict.get('_id')
        self.user_id = plan_dict.get('user_id')
        self.name = plan_dict.get('name')
        # meals is a list of objects: {'type': 'breakfast', 'description': 'eggs...', 'calories': 300}
        self.meals = plan_dict.get('meals', [])
        self.created_at = plan_dict.get('created_at', datetime.utcnow())
        
    @property
    def id(self):
        return str(self._id)
        
    def to_dict(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'name': self.name,
            'meals': self.meals,
            'created_at': self.created_at
        }
        
    @staticmethod
    def create(db, user_id, name, meals):
        """
        meals example: [
            {'type': 'Breakfast', 'items': 'Oatmeal, 2 Eggs', 'calories': 400},
            {'type': 'Lunch', 'items': 'Chicken Breast, Rice', 'calories': 600}
        ]
        """
        plan_dict = {
            'user_id': ObjectId(user_id),
            'name': name,
            'meals': meals,
            'created_at': datetime.utcnow()
        }
        result = db.meal_plans.insert_one(plan_dict)
        plan_dict['_id'] = result.inserted_id
        return MealPlan(plan_dict)

    @staticmethod
    def find_by_user(db, user_id):
        plans = []
        for doc in db.meal_plans.find({'user_id': ObjectId(user_id)}).sort('created_at', -1):
            plans.append(MealPlan(doc))
        return plans

    @staticmethod
    def find_by_id(db, plan_id):
        try:
            doc = db.meal_plans.find_one({'_id': ObjectId(plan_id)})
            if doc:
                return MealPlan(doc)
        except:
            pass
        return None

    def update(self, db, name=None, meals=None):
        update_data = {}
        if name:
            self.name = name
            update_data['name'] = name
        if meals is not None:
            self.meals = meals
            update_data['meals'] = meals
            
        if update_data:
            db.meal_plans.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
            return True
        return False
        
    def delete(self, db):
        db.meal_plans.delete_one({'_id': self._id})
        return True
