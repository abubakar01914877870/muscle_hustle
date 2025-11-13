from datetime import datetime
from .user import db

class ProgressEntry(db.Model):
    __tablename__ = 'progress_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Measurements
    weight = db.Column(db.Float, nullable=False)
    body_fat = db.Column(db.Float)
    water_intake = db.Column(db.Float)
    
    # Additional metrics
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    hips = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
    
    # Notes and photo
    notes = db.Column(db.Text)
    photo_filename = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('progress_entries', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<ProgressEntry {self.id} - User {self.user_id} - {self.weight}kg>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight,
            'body_fat': self.body_fat,
            'water_intake': self.water_intake,
            'chest': self.chest,
            'waist': self.waist,
            'hips': self.hips,
            'arms': self.arms,
            'thighs': self.thighs,
            'notes': self.notes,
            'photo_filename': self.photo_filename,
            'created_at': self.created_at.isoformat()
        }
