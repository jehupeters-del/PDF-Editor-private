# PythonAnywhere WSGI Configuration for Python 3.13
# This file configures how PythonAnywhere serves your Flask app
# 
# INSTRUCTIONS:
# 1. Replace 'yourusername' with your actual PythonAnywhere username (likely 'jpeters')
# 2. Replace 'your-super-secret-random-key' with a strong random key
# 3. Update 'PDF-Editor-private' to your actual project folder name

import sys
import os
import logging

# Configure logging FIRST (before any imports that might log)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Add your project directory to the sys.path
# IMPORTANT: Change 'yourusername' and 'PDF-Editor-private' to match your setup
project_home = '/home/jpeters/PDF-Editor-private'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

logging.info(f'Adding project to path: {project_home}')
logging.info(f'Python version: {sys.version}')

# Set environment variables
# IMPORTANT: Generate a strong random secret key with: python -c "import secrets; print(secrets.token_hex(32))"
# DO NOT use 'testing-super-secret-random-key' in production!
os.environ['SECRET_KEY'] = 'testing-super-secret-random-key'

# Change working directory to project directory
# This is CRITICAL for relative paths to work correctly
os.chdir(project_home)
logging.info(f'Changed working directory to: {os.getcwd()}')

# Create required directories if they don't exist
uploads_dir = os.path.join(project_home, 'uploads')
static_temp_dir = os.path.join(project_home, 'static', 'temp')
flask_session_dir = os.path.join(project_home, 'flask_session')

try:
    for directory in [uploads_dir, static_temp_dir, flask_session_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755, exist_ok=True)
            logging.info(f'Created directory: {directory}')
        else:
            logging.info(f'Directory exists: {directory}')
except Exception as e:
    logging.error(f'Error creating directories: {e}')

# Import Flask app (this must come AFTER path setup)
try:
    from app import app as application
    logging.info('Successfully imported Flask app')
except ImportError as e:
    logging.error(f'Failed to import app: {e}')
    logging.error('Make sure Flask-Session is installed: pip install Flask-Session')
    raise

# The application object is used by PythonAnywhere
# Make sure it's named 'application' not 'app'
