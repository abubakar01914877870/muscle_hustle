"""
Database initialization script
Run this to create the database tables if they don't exist
"""
from src.app import create_app
from src.models.user import db, User

def init_database():
    app = create_app()
    with app.app_context():
        # Create tables only if they don't exist (preserves existing data)
        db.create_all()
        print("Database tables created/verified successfully!")
        
        # Create default admin user only if it doesn't exist
        admin = User.query.filter_by(email='super@admin.com').first()
        if not admin:
            admin = User(email='super@admin.com', is_admin=True)
            admin.set_password('1234qa')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: super@admin.com / 1234qa")
        else:
            print("Admin user already exists: super@admin.com")

if __name__ == '__main__':
    init_database()
