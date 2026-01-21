import re
from datetime import datetime
from bson import ObjectId

def slugify(text):
    """Simple slugify implementation"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

class Gym:
    def __init__(self, name, description, phone, google_map_link, address, admin_note=None, images=None, slug=None, _id=None, created_at=None, updated_at=None):
        self.id = _id if _id else ObjectId()
        self.name = name
        self.slug = slug if slug else slugify(name)
        self.description = description
        self.phone = phone
        self.google_map_link = google_map_link
        self.address = address
        self.admin_note = admin_note
        self.images = images if images else []
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        return {
            '_id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'phone': self.phone,
            'google_map_link': self.google_map_link,
            'address': self.address,
            'admin_note': self.admin_note,
            'images': self.images,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return Gym(
            _id=data.get('_id'),
            name=data.get('name'),
            slug=data.get('slug'),
            description=data.get('description'),
            phone=data.get('phone'),
            google_map_link=data.get('google_map_link'),
            address=data.get('address'),
            admin_note=data.get('admin_note'),
            images=data.get('images'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @staticmethod
    def save(db, gym):
        gym.updated_at = datetime.utcnow()
        # Regenerate slug if it's missing (for legacy data handling)
        if not gym.slug:
            gym.slug = slugify(gym.name)
        db.gyms.replace_one({'_id': gym.id}, gym.to_dict(), upsert=True)
        return gym

    @staticmethod
    def find_all(db):
        gyms_data = db.gyms.find().sort('created_at', -1)
        return [Gym.from_dict(g) for g in gyms_data]

    @staticmethod
    def find_by_id(db, gym_id):
        try:
            gym_data = db.gyms.find_one({'_id': ObjectId(gym_id)})
            return Gym.from_dict(gym_data)
        except:
            return None

    @staticmethod
    def find_by_slug(db, slug):
        gym_data = db.gyms.find_one({'slug': slug})
        return Gym.from_dict(gym_data)

    @staticmethod
    def delete(db, gym_id):
        db.gyms.delete_one({'_id': ObjectId(gym_id)})
