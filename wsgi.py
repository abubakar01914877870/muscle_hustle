"""
WSGI configuration for PythonAnywhere deployment
Copy this content to your WSGI configuration file on PythonAnywhere
"""
import sys
import os

# ============================================
# IMPORTANT: Update this path with your PythonAnywhere username
# ============================================
project_home = '/home/yourusername/muscle_hustle'

# Add your project directory to the sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================
# IMPORTANT: Set a strong secret key for production
# ============================================
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this-to-something-random-and-secure'

# Import the Flask app
from src.app import app as application

# Optional: Enable debug mode (disable in production)
# application.debug = False
