# PythonAnywhere WSGI Configuration
# This file configures how PythonAnywhere serves your Flask app

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/PDF-Editor'  # CHANGE THIS to your actual path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'CHANGE-THIS-TO-A-STRONG-SECRET-KEY'  # IMPORTANT: Change this!

# Import Flask app
from app import app as application  # noqa

# Optional: Configure logging
import logging
logging.basicConfig(level=logging.INFO)

# The application object is used by PythonAnywhere
# Make sure it's named 'application' not 'app'
