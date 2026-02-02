# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (Free or Paid tier)
- Git repository or file upload capability

## Step 1: Upload Files to PythonAnywhere

### Option A: Using Git (Recommended)
```bash
cd ~
git clone <your-repository-url> PDF-Editor
cd PDF-Editor
```

### Option B: Manual Upload
1. Go to PythonAnywhere Dashboard → Files
2. Create directory: `/home/yourusername/PDF-Editor`
3. Upload all project files via the file browser

## Step 2: Create Virtual Environment

```bash
cd ~/PDF-Editor
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: PythonAnywhere supports Python 3.10 by default. If you need 3.13, check their current Python version availability.

## Step 3: Create Instance Directories

```bash
mkdir -p ~/PDF-Editor/instance/uploads
chmod 755 ~/PDF-Editor/instance
```

## Step 4: Configure WSGI File

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration** → **Python 3.10**
4. Click on the **WSGI configuration file** link

Replace the contents with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/PDF-Editor'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from app import app as application
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username!

## Step 5: Configure Static Files

In the **Web** tab:

1. Scroll to **Static files** section
2. Add new mapping:
   - URL: `/static`
   - Directory: `/home/yourusername/PDF-Editor/static`

## Step 6: Set Environment Variables (Optional)

If you want to set a custom secret key:

1. Go to **Web** tab
2. Scroll to **Environment variables**
3. Add:
   - Name: `SECRET_KEY`
   - Value: `<generate-a-random-string>`

## Step 7: Configure Session Settings

Edit `app.py` and ensure these settings are present:

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload
```

## Step 8: Set Up Cleanup Scheduled Task

1. Go to **Tasks** tab in PythonAnywhere dashboard
2. Create a new **Scheduled Task**
3. Set frequency: **Hourly**
4. Command:
   ```bash
   /home/yourusername/PDF-Editor/venv/bin/python /home/yourusername/PDF-Editor/cleanup.py
   ```

This will automatically delete temporary files older than 2 hours.

## Step 9: Reload Web App

1. Go back to **Web** tab
2. Click the green **Reload** button at the top

Your app should now be live at: `https://yourusername.pythonanywhere.com`

## Troubleshooting

### Error Log Location
Check error logs at:
- **Web** tab → **Log files** section
- Server log: `/var/log/yourusername.pythonanywhere.com.server.log`
- Error log: `/var/log/yourusername.pythonanywhere.com.error.log`

### Common Issues

#### 1. Import Errors
```bash
source ~/PDF-Editor/venv/bin/activate
pip list  # Verify all dependencies are installed
```

#### 2. Permission Errors
```bash
chmod -R 755 ~/PDF-Editor/instance
```

#### 3. PyMuPDF Installation Issues
If PyMuPDF fails to install:
```bash
pip install --upgrade pip setuptools wheel
pip install PyMuPDF --no-cache-dir
```

#### 4. Session Storage Issues
Ensure Flask-Session is properly configured:
```bash
pip install Flask-Session
```

And in `app.py`:
```python
from flask_session import Session
Session(app)
```

### Testing Upload Size Limits

Free PythonAnywhere accounts have limitations:
- Web app timeout: 5 minutes
- File storage: Limited by account tier

For large PDFs (50+ pages), consider:
1. Upgrading to a paid account
2. Implementing pagination in the editor view
3. Lazy-loading thumbnails

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Verify MAX_CONTENT_LENGTH is set
- [ ] Test file extension validation
- [ ] Confirm cleanup task is running
- [ ] Test session isolation between users
- [ ] Enable HTTPS (automatic on PythonAnywhere)

## Maintenance

### Monitor Disk Usage
```bash
du -sh ~/PDF-Editor/instance/uploads/*
```

### Manual Cleanup (if needed)
```bash
find ~/PDF-Editor/instance/uploads/* -mmin +120 -type d -exec rm -rf {} +
```

### Update Dependencies
```bash
cd ~/PDF-Editor
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

Then reload the web app from the dashboard.

## Performance Optimization

### For Large PDFs
1. **Lazy Loading**: Modify `editor.js` to load thumbnails on scroll
2. **Thumbnail Resolution**: Adjust DPI in `pdf_viewer_web.py` (currently 150)
3. **Caching**: Consider Redis for session storage on paid accounts

### Database Alternative
For production use with many concurrent users, consider:
- Storing session data in SQLite or PostgreSQL
- Using Celery for background thumbnail generation
- Implementing a queue system for merge operations

## Monitoring

### Check Scheduled Task Status
```bash
cat /var/log/pythonanywhere.scheduled.tasks.log
```

### Check Cleanup Script Execution
```bash
ls -la ~/PDF-Editor/instance/uploads/
```

Directories older than 2 hours should be automatically removed.

## Support Resources

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

## Backup Strategy

Regular backups (if needed):
```bash
cd ~
tar -czf PDF-Editor-backup-$(date +%Y%m%d).tar.gz PDF-Editor
```

Download via **Files** tab or use SCP if you have SSH access.
