"""
Planner Models for MongoDB
"""
from datetime import datetime, date
from bson import ObjectId

class ExerciseGroup:
    """Model for a group of exercises (e.g., 'Leg Day')"""
    
    def __init__(self, group_dict):
        self._id = group_dict.get('_id')
        self.user_id = group_dict.get('user_id')
        self.name = group_dict.get('name')
        self.exercise_ids = group_dict.get('exercise_ids', [])
        self.created_at = group_dict.get('created_at', datetime.utcnow())
        
    @property
    def id(self):
        return str(self._id)
        
    def to_dict(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'name': self.name,
            'exercise_ids': self.exercise_ids,
            'created_at': self.created_at
        }
        
    @staticmethod
    def create(db, user_id, name, exercise_ids):
        # Validation
        if not name or not name.strip():
            raise ValueError("Group name cannot be empty")
        
        if not exercise_ids or len(exercise_ids) == 0:
            raise ValueError("At least one exercise must be selected")
        
        group_dict = {
            'user_id': ObjectId(user_id),
            'name': name.strip(),
            'exercise_ids': [ObjectId(eid) for eid in exercise_ids],
            'created_at': datetime.utcnow()
        }
        result = db.exercise_groups.insert_one(group_dict)
        group_dict['_id'] = result.inserted_id
        return ExerciseGroup(group_dict)

    @staticmethod
    def find_by_user(db, user_id):
        groups = []
        for doc in db.exercise_groups.find({'user_id': ObjectId(user_id)}).sort('created_at', -1):
            groups.append(ExerciseGroup(doc))
        return groups

    @staticmethod
    def find_by_id(db, group_id):
        try:
            doc = db.exercise_groups.find_one({'_id': ObjectId(group_id)})
            if doc:
                return ExerciseGroup(doc)
        except:
            pass
        return None

    def update(self, db, name=None, exercise_ids=None):
        update_data = {}
        if name is not None:
            if not name.strip():
                raise ValueError("Group name cannot be empty")
            self.name = name.strip()
            update_data['name'] = self.name
        if exercise_ids is not None:
            if len(exercise_ids) == 0:
                raise ValueError("At least one exercise must be selected")
            self.exercise_ids = [ObjectId(eid) for eid in exercise_ids]
            update_data['exercise_ids'] = self.exercise_ids
            
        if update_data:
            db.exercise_groups.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
            return True
        return False
        
    def delete(self, db):
        # Remove all calendar assignments for this group
        db.calendar_assignments.delete_many({'exercise_group_id': self._id})
        # Delete the group itself
        db.exercise_groups.delete_one({'_id': self._id})
        return True


class CalendarAssignment:
    """Model for assigning an ExerciseGroup to a specific date"""
    
    def __init__(self, assign_dict):
        self._id = assign_dict.get('_id')
        self.user_id = assign_dict.get('user_id')
        self.date_str = assign_dict.get('date_str') # Format YYYY-MM-DD
        self.exercise_group_id = assign_dict.get('exercise_group_id')
        self.assignment_type = assign_dict.get('assignment_type', 'workout') # 'workout' or 'rest'
        self.series_id = assign_dict.get('series_id') # UUID string for recurring events
        self.created_at = assign_dict.get('created_at', datetime.utcnow())
        
        # Hydrated fields (optional)
        self.group_name = assign_dict.get('group_name') 

    @property
    def id(self):
        return str(self._id)
        
    def create(db, user_id, date_obj, group_id=None, assignment_type='workout', series_id=None):
        # Ensure unique assignment per group per day? Or allow multiple?
        # User requirement: "user can assign his group of exercize to a day."
        date_str = date_obj.strftime('%Y-%m-%d') if isinstance(date_obj, (datetime, date)) else date_obj
        
        assign_dict = {
            'user_id': ObjectId(user_id),
            'date_str': date_str,
            'assignment_type': assignment_type,
            'created_at': datetime.utcnow()
        }
        
        if series_id:
            assign_dict['series_id'] = series_id
        
        if group_id:
            assign_dict['exercise_group_id'] = ObjectId(group_id)
            
        result = db.calendar_assignments.insert_one(assign_dict)
        assign_dict['_id'] = result.inserted_id
        return CalendarAssignment(assign_dict)
        
    @staticmethod
    def find_by_user_and_date_range(db, user_id, start_date, end_date):
        # dates as YYYY-MM-DD strings
        query = {
            'user_id': ObjectId(user_id),
            'date_str': {'$gte': start_date, '$lte': end_date}
        }
        assignments = []
        # Join with exercise_groups to get names efficiently? 
        # MongoDB lookup or application level join. Application level is easier for this scale.
        
        docs = list(db.calendar_assignments.find(query))
        
        # Get unique group IDs to fetch names in one go
        group_ids = list(set(d.get('exercise_group_id') for d in docs if d.get('exercise_group_id')))
        
        group_map = {}
        if group_ids:
            groups = db.exercise_groups.find({'_id': {'$in': group_ids}})
            for g in groups:
                group_map[g['_id']] = g['name']
                
        for doc in docs:
            item = CalendarAssignment(doc)
            if item.exercise_group_id:
                item.group_name = group_map.get(doc['exercise_group_id'], "Unknown Group")
            assignments.append(item)
            
        return assignments

    @staticmethod
    def find_by_user_and_date(db, user_id, date_str):
        query = {
            'user_id': ObjectId(user_id),
            'date_str': date_str
        }
        assignments = []
        
        docs = list(db.calendar_assignments.find(query))
        group_ids = list(set(d.get('exercise_group_id') for d in docs if d.get('exercise_group_id')))
        
        group_map = {}
        if group_ids:
            groups = db.exercise_groups.find({'_id': {'$in': group_ids}})
            for g in groups:
                group_map[g['_id']] = g['name']
                
        for doc in docs:
            item = CalendarAssignment(doc)
            if item.exercise_group_id:
                item.group_name = group_map.get(doc['exercise_group_id'], "Unknown Group")
            assignments.append(item)
            
        return assignments

    @staticmethod
    def delete(db, assignment_id):
        db.calendar_assignments.delete_one({'_id': ObjectId(assignment_id)})
        return True
    
    @staticmethod
    def delete_by_date(db, user_id, date_obj):
        """Delete all assignments for a specific user and date"""
        date_str = date_obj.strftime('%Y-%m-%d') if isinstance(date_obj, (datetime, date)) else date_obj
        query = {
            'user_id': ObjectId(user_id),
            'date_str': date_str
        }
        result = db.calendar_assignments.delete_many(query)
        return result.deleted_count

    @staticmethod
    def delete_series(db, user_id, series_id, start_date_str):
        """Delete this assignment and all future ones in the series"""
        if not series_id:
            return False
            
        query = {
            'user_id': ObjectId(user_id),
            'series_id': series_id,
            'date_str': {'$gte': start_date_str}
        }
        result = db.calendar_assignments.delete_many(query)
        return result.deleted_count > 0


class WorkoutLog:
    """Model for tracking completion of specific exercises on a specific date"""
    
    def __init__(self, log_dict):
        self._id = log_dict.get('_id')
        self.user_id = log_dict.get('user_id')
        self.date_str = log_dict.get('date_str')
        self.exercise_id = log_dict.get('exercise_id')
        self.status = log_dict.get('status', 'completed')
        self.completed_at = log_dict.get('completed_at', datetime.utcnow())

    @staticmethod
    def mark_completed(db, user_id, date_str, exercise_id):
        # Upsert to avoid duplicates for the same day/exercise
        query = {
            'user_id': ObjectId(user_id),
            'date_str': date_str,
            'exercise_id': ObjectId(exercise_id)
        }
        update = {
            '$set': {
                'status': 'completed',
                'completed_at': datetime.utcnow()
            }
        }
        db.workout_logs.update_one(query, update, upsert=True)
        return True
        
    @staticmethod
    def mark_incomplete(db, user_id, date_str, exercise_id):
        query = {
            'user_id': ObjectId(user_id),
            'date_str': date_str,
            'exercise_id': ObjectId(exercise_id)
        }
        db.workout_logs.delete_one(query)
        return True

    @staticmethod
    def get_completed_exercise_ids(db, user_id, date_str):
        query = {
            'user_id': ObjectId(user_id),
            'date_str': date_str
        }
        docs = db.workout_logs.find(query)
        return [doc['exercise_id'] for doc in docs]


class DietAssignment:
    """Model for assigning a MealPlan to a specific date"""
    
    def __init__(self, assign_dict):
        self._id = assign_dict.get('_id')
        self.user_id = assign_dict.get('user_id')
        self.date_str = assign_dict.get('date_str') # Format YYYY-MM-DD
        self.meal_plan_id = assign_dict.get('meal_plan_id')
        self.created_at = assign_dict.get('created_at', datetime.utcnow())
        
        # Hydrated fields (optional)
        self.plan_name = assign_dict.get('plan_name') 

    @property
    def id(self):
        return str(self._id)
        
    @staticmethod
    def create(db, user_id, date_obj, plan_id):
        date_str = date_obj.strftime('%Y-%m-%d') if isinstance(date_obj, (datetime, date)) else date_obj
        
        # Check if assignment already exists for this day, if so replace it?
        # For now simple insert
        assign_dict = {
            'user_id': ObjectId(user_id),
            'date_str': date_str,
            'meal_plan_id': ObjectId(plan_id),
            'created_at': datetime.utcnow()
        }
        result = db.diet_assignments.insert_one(assign_dict)
        assign_dict['_id'] = result.inserted_id
        return DietAssignment(assign_dict)
        
    @staticmethod
    def find_by_user_and_date_range(db, user_id, start_date, end_date):
        query = {
            'user_id': ObjectId(user_id),
            'date_str': {'$gte': start_date, '$lte': end_date}
        }
        assignments = []
        docs = list(db.diet_assignments.find(query))
        
        # Get unique plan IDs
        plan_ids = list(set(d['meal_plan_id'] for d in docs))
        
        plan_map = {}
        if plan_ids:
            plans = db.meal_plans.find({'_id': {'$in': plan_ids}})
            for p in plans:
                plan_map[p['_id']] = p['name']
                
        for doc in docs:
            item = DietAssignment(doc)
            item.plan_name = plan_map.get(doc['meal_plan_id'], "Unknown Plan")
            assignments.append(item)
            
        return assignments

    @staticmethod
    def delete(db, assignment_id):
        db.diet_assignments.delete_one({'_id': ObjectId(assignment_id)})
        return True
