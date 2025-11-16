"""
WSGI Entry Point for Production Deployment
"""
from src.app import app

# For gunicorn
if __name__ == "__main__":
    app.run()
