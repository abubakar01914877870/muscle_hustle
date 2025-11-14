"""
Seed initial exercises into MongoDB
"""
from src.database import get_mongo_client
from src.models.exercise_mongo import Exercise
import os

def seed_exercises():
    """Seed initial exercises"""
    
    mongo_uri = os.environ.get('MONGO_URI') or "mongodb+srv://admin:1234qa@muscle-hustle-developme.ekctotl.mongodb.net/?appName=muscle-hustle-development"
    dbname = os.environ.get('MONGO_DBNAME') or "muscle_hustle"
    
    client = get_mongo_client()
    db = client[dbname]
    
    print("\n" + "="*60)
    print("🏋️ SEEDING EXERCISES")
    print("="*60)
    
    # Check if exercises already exist
    existing_count = db.exercises.count_documents({})
    if existing_count > 0:
        print(f"✓ Database already has {existing_count} exercises")
        response = input("Do you want to add more exercises? (y/n): ")
        if response.lower() != 'y':
            print("Seeding cancelled")
            return
    
    exercises_data = [
        {
            'name': 'Barbell Bench Press',
            'muscle': 'Chest',
            'secondary_muscles': ['Shoulders', 'Triceps'],
            'equipment': 'Barbell',
            'difficulty': 'Beginner',
            'type': 'Strength',
            'description': 'The barbell chest press is a fundamental exercise for building upper body strength, targeting the pectoral muscles, triceps, and shoulders.',
            'instructions': '1. Load barbell with weight\n2. Lie on bench with feet flat\n3. Grip barbell slightly wider than shoulder-width\n4. Lower to mid-chest\n5. Press back up',
            'reps_sets': '3-4 sets of 8-12 reps',
            'tips': 'Keep feet flat, maintain slight arch in lower back',
            'common_mistakes': 'Bouncing bar, flaring elbows too wide, lifting hips'
        },
        {
            'name': 'Pull-Up',
            'muscle': 'Back',
            'secondary_muscles': ['Biceps', 'Forearms'],
            'equipment': 'Pullup Bar',
            'difficulty': 'Intermediate',
            'type': 'Strength',
            'description': 'Classic bodyweight exercise for building back and arm strength. One of the most effective upper body exercises.',
            'instructions': '1. Grab bar with overhand grip, shoulder-width apart\n2. Lift yourself until chin is above bar\n3. Pause for a second\n4. Lower yourself slowly\n5. Repeat',
            'reps_sets': '3-4 sets to failure',
            'tips': 'Maintain control, avoid swinging, activate lats',
            'common_mistakes': 'Using momentum, not going full range, stopping too early'
        },
        {
            'name': 'Barbell Squat',
            'muscle': 'Upper Legs',
            'secondary_muscles': ['Glutes', 'Lower Legs'],
            'equipment': 'Barbell',
            'difficulty': 'Intermediate',
            'type': 'Strength',
            'description': 'Fundamental exercise for building lower body strength. Targets quads, hamstrings, glutes, and core.',
            'instructions': '1. Position barbell on upper back\n2. Stand with feet shoulder-width apart\n3. Lower by pushing hips back and bending knees\n4. Go until thighs parallel to ground\n5. Push through heels to stand',
            'reps_sets': '3-5 sets of 6-10 reps',
            'tips': 'Keep chest up, back straight, weight in heels',
            'common_mistakes': 'Knees caving inward, leaning too far forward, not going deep enough'
        },
        {
            'name': 'Dumbbell Shoulder Press',
            'muscle': 'Shoulders',
            'secondary_muscles': ['Triceps'],
            'equipment': 'Dumbbell',
            'difficulty': 'Beginner',
            'type': 'Strength',
            'description': 'Builds strength in shoulders, deltoids, triceps, and upper chest.',
            'instructions': '1. Sit on bench with dumbbells at shoulder height\n2. Press upward until arms extended\n3. Keep core tight\n4. Lower to shoulder height\n5. Repeat',
            'reps_sets': '3-4 sets of 8-12 reps',
            'tips': 'Keep dumbbells overhead, maintain control',
            'common_mistakes': 'Arching too much, uneven pressing, going too heavy'
        },
        {
            'name': 'Dumbbell Bicep Curl',
            'muscle': 'Biceps',
            'secondary_muscles': ['Forearms'],
            'equipment': 'Dumbbell',
            'difficulty': 'Beginner',
            'type': 'Strength',
            'description': 'Isolation exercise for building bicep strength and size.',
            'instructions': '1. Stand with feet shoulder-width apart\n2. Hold dumbbells at sides with palms facing forward\n3. Curl dumbbells up\n4. Control the descent\n5. Repeat',
            'reps_sets': '3 sets of 10-12 reps',
            'tips': 'Keep elbows stationary, control the negative',
            'common_mistakes': 'Swinging weight, moving elbows, too heavy'
        },
        {
            'name': 'Plank',
            'muscle': 'Abs',
            'secondary_muscles': [],
            'equipment': 'Body Weight',
            'difficulty': 'Beginner',
            'type': 'Strength',
            'description': 'Core strengthening exercise that builds stability and endurance.',
            'instructions': '1. Start in push-up position\n2. Lower to forearms\n3. Keep body straight from head to heels\n4. Hold position\n5. Breathe steadily',
            'reps_sets': '3 sets of 30-60 seconds',
            'tips': 'Keep core tight, don\'t let hips sag',
            'common_mistakes': 'Sagging hips, raising hips too high, holding breath'
        },
        {
            'name': 'Deadlift',
            'muscle': 'Back',
            'secondary_muscles': ['Glutes', 'Upper Legs'],
            'equipment': 'Barbell',
            'difficulty': 'Advanced',
            'type': 'Strength',
            'description': 'Compound exercise that works the entire posterior chain. One of the best exercises for overall strength.',
            'instructions': '1. Stand with feet hip-width apart, bar over mid-foot\n2. Bend and grip bar\n3. Keep back straight, chest up\n4. Drive through heels to stand\n5. Lower with control',
            'reps_sets': '3-5 sets of 5-8 reps',
            'tips': 'Keep bar close to body, engage lats, neutral spine',
            'common_mistakes': 'Rounding back, bar too far from body, jerking the weight'
        },
        {
            'name': 'Running',
            'muscle': 'Cardio',
            'secondary_muscles': ['Upper Legs', 'Lower Legs'],
            'equipment': 'Cardio Machine',
            'difficulty': 'Beginner',
            'type': 'Cardio',
            'description': 'Cardiovascular exercise that improves endurance and burns calories.',
            'instructions': '1. Start at comfortable pace\n2. Maintain steady breathing\n3. Keep posture upright\n4. Land mid-foot\n5. Continue for desired duration',
            'reps_sets': '20-45 minutes',
            'tips': 'Start slow, build up gradually, stay hydrated',
            'common_mistakes': 'Going too fast too soon, poor posture, overstriding'
        }
    ]
    
    added_count = 0
    for exercise_data in exercises_data:
        # Check if exercise already exists
        existing = db.exercises.find_one({'name': exercise_data['name']})
        if existing:
            print(f"⏭️  Skipping '{exercise_data['name']}' (already exists)")
            continue
        
        Exercise.create(db=db, **exercise_data)
        print(f"✅ Added: {exercise_data['name']}")
        added_count += 1
    
    print("\n" + "="*60)
    print(f"✅ SEEDING COMPLETE! Added {added_count} exercises")
    print(f"📊 Total exercises in database: {db.exercises.count_documents({})}")
    print("="*60 + "\n")

if __name__ == '__main__':
    seed_exercises()
