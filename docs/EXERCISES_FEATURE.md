# Exercise Database Feature

## Overview

The Exercise Database feature allows users to browse, search, and filter exercises. Admin users can add, edit, and delete exercises.

## Features

### For All Users
- **Browse Exercises**: View all exercises in a grid layout
- **Search**: Search exercises by name
- **Filter**: Filter by muscle group and equipment
- **View Details**: Click on any exercise to see full details including:
  - Description
  - Instructions
  - Tips & Safety
  - Common Mistakes
  - Target reps/sets
  - Video tutorial (if available)

### For Admin Users
- **Add Exercise**: Create new exercises with comprehensive information
- **Edit Exercise**: Update existing exercise details
- **Delete Exercise**: Remove exercises from the database
- **Image Upload**: Upload multiple images for exercises

## Database Schema

### Exercise Collection

```javascript
{
  _id: ObjectId,
  name: String,
  muscle: String,  // Primary muscle group
  secondary_muscles: [String],
  equipment: String,
  difficulty: String,  // Beginner, Intermediate, Advanced
  type: String,  // Strength, Cardio, Flexibility, Balance, Plyometric
  description: String,
  instructions: String,
  reps_sets: String,
  tips: String,
  common_mistakes: String,
  video_url: String,
  images: [String],
  created_by: String,  // User ID
  created_at: DateTime,
  updated_at: DateTime
}
```

## Routes

### Public Routes
- `GET /exercises/` - List all exercises with filters
- `GET /exercises/<exercise_id>` - View exercise details

### Admin Routes (Login Required)
- `GET /exercises/add` - Show add exercise form
- `POST /exercises/add` - Create new exercise
- `GET /exercises/<exercise_id>/edit` - Show edit form
- `POST /exercises/<exercise_id>/edit` - Update exercise
- `POST /exercises/<exercise_id>/delete` - Delete exercise

## Muscle Groups

- Abs
- Back
- Biceps
- Cardio
- Chest
- Forearms
- Glutes
- Shoulders
- Triceps
- Upper Legs
- Lower Legs

## Equipment Types

- Body Weight
- Bands
- Barbell
- Bench
- Dumbbell
- Exercise Ball
- EZ Curl Bar
- Kettlebell
- Cardio Machine
- Strength Machine
- Pullup Bar
- Weight Plate

## Usage

### Browsing Exercises

1. Navigate to "All Exercises" from the main menu
2. Browse the exercise grid
3. Use filters to narrow down by muscle group or equipment
4. Use the search bar to find specific exercises
5. Click on any exercise card to view full details

### Adding an Exercise (Admin Only)

1. Click the floating "+" button on the exercises page
2. Fill in the required fields:
   - Exercise Name *
   - Primary Muscle Group *
   - Equipment *
   - Difficulty *
   - Type *
3. Optionally add:
   - Description
   - Instructions
   - Secondary muscle groups
   - Target reps/sets
   - Tips & safety
   - Common mistakes
   - Video URL
   - Images
4. Click "Add Exercise"

### Editing an Exercise (Admin Only)

1. Navigate to the exercise detail page
2. Click "Edit Exercise"
3. Update the fields
4. Click "Save Changes"

### Deleting an Exercise (Admin Only)

1. Navigate to the exercise detail page
2. Click "Delete Exercise"
3. Confirm the deletion

## Seeding Initial Data

To populate the database with initial exercises:

```bash
python seed_exercises.py
```

This will add 8 sample exercises covering different muscle groups and equipment types.

## Design System

The exercises feature follows the Muscle Hustle design system with:
- Orange gradient headers
- Card-based layout
- Responsive grid
- Filter buttons with active states
- Floating action button for admins
- Consistent typography and spacing

## File Structure

```
src/
├── models/
│   └── exercise_mongo.py       # Exercise model
├── routes/
│   └── exercises.py            # Exercise routes
├── templates/
│   └── exercises/
│       ├── index.html          # Exercise list
│       ├── detail.html         # Exercise details
│       └── add.html            # Add/edit form
└── static/
    └── uploads/
        └── exercises/          # Exercise images

seed_exercises.py               # Seed script
```

## Future Enhancements

- Workout builder using exercises
- Exercise favorites
- Exercise ratings and reviews
- Exercise variations
- Video upload (currently URL only)
- Exercise categories/tags
- Advanced search with multiple filters
- Exercise history tracking
- Personal exercise notes

## Testing

1. Start the application: `python run.py`
2. Navigate to http://127.0.0.1:5000/exercises/
3. Test filtering and searching
4. Click on an exercise to view details
5. Login as admin (super@admin.com / 1234qa)
6. Test adding, editing, and deleting exercises

## Security

- Only authenticated admin users can add, edit, or delete exercises
- File uploads are validated for allowed extensions
- User input is sanitized
- MongoDB injection protection through PyMongo

## Performance

- Indexes on name, muscle, and equipment fields
- Efficient MongoDB queries
- Lazy loading of images
- Pagination ready (can be added if needed)
