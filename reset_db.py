"""
Database reset script
WARNING: This will DELETE ALL DATA and recreate the database
Use this only when you need to completely reset the database
"""
from src.app import create_app
from src.models.user import db, User

def reset_database():
    app = create_app()
    with app.app_context():
        print("WARNING: This will delete all existing data!")
        confirm = input("Are you sure you want to reset the database? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Database reset cancelled.")
            return
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")
        
        # Create default admin user
        admin = User(email='super@admin.com', is_admin=True)
        admin.set_password('1234qa')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: super@admin.com / 1234qa")

if __name__ == '__main__':
    reset_database()
