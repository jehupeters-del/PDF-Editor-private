# Flask Web Application - Deployment Guide (Python 3.13)

## Test Locally First

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   - Go to http://localhost:5000
   - Test upload, view, merge, extract, validate features

4. **Stop the server:**
   - Press Ctrl+C in terminal

## Deploy to PythonAnywhere (Python 3.13)

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com/
2. Sign up for free account
3. Confirm email

### Step 2: Upload Files
Option A - Via Web Interface:
1. Go to "Files" tab
2. Create directory: `/home/jpeters/PDF-Editor-private`
3. Upload all project files

Option B - Via Git (recommended):
1. Go to "Consoles" tab
2. Start a Bash console
3. Run:
   ```bash
   git clone https://github.com/jehupeters-del/PDF-Editor-private.git PDF-Editor-private
   cd PDF-Editor-private
   ```

### Step 3: Create Virtual Environment (Python 3.13)
In the Bash console:
```bash
cd /home/jpeters/PDF-Editor-private
mkvirtualenv venv --python=python3.13
workon venv
```

### Step 4: Install Dependencies
Still in the virtual environment:
```bash
pip install -r requirements.txt
```

**IMPORTANT**: Verify Flask-Session is installed:
```bash
python -c "from flask_session import Session; print('Flask-Session OK')"
```

### Step 5: Create Required Directories
```bash
mkdir -p uploads
mkdir -p static/temp
mkdir -p flask_session
chmod 755 uploads static/temp flask_session
```

### Step 6: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. **Select Python 3.13** (critical!)
5. Click through to create app

### Step 7: Set Virtual Environment
In Web tab, find "Virtualenv" section:
1. Enter: `/home/jpeters/.virtualenvs/venv`
2. This links your web app to the virtual environment with all dependencies

### Step 8: Edit WSGI Configuration
1. In Web tab, click on WSGI configuration file link
2. Delete all content
3. Copy content from `pythonanywhere_wsgi.py` in your project
4. **IMPORTANT**: Update these lines:
   ```python
   project_home = '/home/jpeters/PDF-Editor-private'  # Change to your username
   os.environ['SECRET_KEY'] = 'your-random-secret-key-here'  # Change to random string
   ```
5. Save file (Ctrl+S or click Save button)

### Step 9: Set Static Files
Still in Web tab, scroll to "Static files" section:
1. Click "Enter URL" under a new static file mapping
2. Add mapping:
   - URL: `/static/`
   - Directory: `/home/jpeters/PDF-Editor-private/static/`

### Step 10: Reload Web App
1. Scroll to top of Web tab
2. Click green "Reload" button
3. Wait for reload to complete (~10 seconds)

### Step 11: Check for Errors
1. Click "Error log" link in Web tab
2. Look for any import errors or issues
3. If you see errors about Flask-Session:
   ```bash
   workon venv
   pip install Flask-Session
   # Then reload web app
   ```

### Step 12: Test Your App
1. Click the link at top of Web tab: `jpeters.pythonanywhere.com`
2. Test all features:
   - Upload PDFs
   - View pages
   - Merge PDFs
   - Extract questions
   - Validate questions

## Troubleshooting

### "Import Error: flask_session"
This is the most common issue. Fix it:
```bash
cd /home/jpeters/PDF-Editor-private
workon venv
pip install Flask-Session cachelib
# Reload web app in Web tab
```

### "FileNotFoundError" when downloading files
- Issue: Working directory is not set correctly
- Solution: The updated WSGI file includes `os.chdir(project_home)` which fixes this
- Make sure you copied the entire `pythonanywhere_wsgi.py` file

### "OSError: write error"
- **Cause**: Disk quota exceeded or insufficient permissions
- **Solutions**:
  1. Check disk usage: `du -sh /home/jpeters/PDF-Editor-private/*`
  2. Clean up old files:
     ```bash
     find /home/jpeters/PDF-Editor-private/uploads -type f -mtime +1 -delete
     find /home/jpeters/PDF-Editor-private/static/temp -type f -mtime +1 -delete
     ```
  3. Free tier limit is 512MB total. Consider upgrading if needed.
  4. Check permissions: `ls -la uploads/`

### App shows "Something went wrong"
- Check Error log (link in Web tab)
- Common issues:
  - Wrong path in WSGI file
  - Missing Flask-Session dependency
  - Directory permissions
  - Wrong Python version selected

### "Import Error: No module named 'flask'"
- Dependencies not installed in virtual environment
- Run:
   ```bash
   workon venv
   pip install -r requirements.txt
   ```
- Make sure you're in the right directory

### Uploads not working
- Check directory exists: `/home/jpeters/PDF-Editor-private/uploads/`
- Check permissions: `chmod 755 uploads`
- Check disk quota: `quota`

### Sessions not persisting
- Check flask_session directory exists and is writable
- Try clearing browser cookies
- Verify Flask-Session is installed: `pip list | grep Flask-Session`

### Static files (CSS/thumbnails) not loading
- Check Static files mapping in Web tab
- URL should be `/static/`
- Directory should be full path: `/home/jpeters/PDF-Editor-private/static/`

## Maintenance

### Clean Up Old Files (Critical for Free Tier)
Create a scheduled task (in Tasks tab) to run daily:
```bash
#!/bin/bash
# Clean files older than 2 hours (120 minutes)
find /home/jpeters/PDF-Editor-private/uploads/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/jpeters/PDF-Editor-private/static/temp/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/jpeters/PDF-Editor-private/flask_session/* -type f -mmin +120 -delete 2>/dev/null
```

**Or run manually when disk space is low:**
```bash
cd /home/jpeters/PDF-Editor-private
find uploads -type f -delete
find static/temp -type f -delete
find flask_session -type f -delete
```

### Monitor Disk Usage
```bash
du -sh /home/jpeters/PDF-Editor-private/*
quota  # Check your overall quota
```

### View Logs
- Error log: Shows Python errors and exceptions
- Server log: Shows HTTP requests
- Access log: Shows all page visits
- All available in Web tab

### Update App
If using Git:
```bash
cd /home/jpeters/PDF-Editor-private
git pull
workon venv
pip install -r requirements.txt  # In case dependencies changed
# Reload web app in Web tab
```

If uploading manually:
- Upload changed files via Files tab
- Reload web app in Web tab

## Security Notes

1. **Change SECRET_KEY**: Never use default key in production
   ```python
   # Generate a strong key:
   import secrets
   print(secrets.token_hex(32))
   ```

2. **File Size Limits**: Default is 50MB, adjust in app.py if needed
3. **Rate Limiting**: Consider adding for production use
4. **Authentication**: Current version has no authentication (public access)
5. **Keep Dependencies Updated**: Run `pip list --outdated` periodically

## Performance Tips

1. **Free Tier Limits**:
   - 300-second request timeout
   - 512MB disk space
   - Limited CPU time per day
   - Avoid processing very large PDFs

2. **Optimization**:
   - Batch operations may timeout on free tier
   - Single-file operations work best
   - Keep uploaded files under 10MB for best performance
   - Regular cleanup is essential

3. **Session Management**:
   - Sessions expire after 2 hours
   - Regular cleanup prevents disk space issues
   - Each user gets their own session folder

## Python 3.13 Specific Notes

- **Compatibility**: All dependencies are Python 3.13 compatible
- **Performance**: Python 3.13 offers improved performance over 3.10
- **Virtual Environment**: Must use `mkvirtualenv` with `--python=python3.13`
- **If 3.13 not available**: You can use Python 3.10+ (update WSGI config and virtual environment commands)

## Common Error Messages and Solutions

### "working directory not found"
- Solution: WSGI file now includes `os.chdir(project_home)`
- Make sure you updated the WSGI configuration

### "flask_session module not found"
- Solution: `workon venv && pip install Flask-Session`
- Verify in WSGI config that virtualenv path is correct

### "Permission denied" errors
- Solution: `chmod 755 uploads static/temp flask_session`
- May need to contact support if persistent

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Set up cleanup scheduled task (critical!)
3. Monitor error logs regularly
4. Monitor disk usage
5. Consider upgrading plan if needed
6. Add custom domain (paid plans)

## Support Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- Flask Documentation: https://flask.palletsprojects.com/
- Python 3.13 What's New: https://docs.python.org/3.13/whatsnew/3.13.html
- This project's README: See README_FLASK.md

## Quick Reference

### Important Paths
- Project: `/home/jpeters/PDF-Editor-private/`
- WSGI: `/var/www/jpeters_pythonanywhere_com_wsgi.py`
- Virtual Env: `/home/jpeters/.virtualenvs/venv`
- Logs: Available in Web tab
- Static: `/home/jpeters/PDF-Editor-private/static/`
- Your URL: `https://jpeters.pythonanywhere.com`

### Important Commands
```bash
# Activate virtual environment
workon venv

# Install/Update deps
pip install -r requirements.txt

# Check Python version
python --version  # Should show 3.13.x

# Test imports
python -c "from flask_session import Session; print('OK')"
python -c "import fitz; print(fitz.__version__)"

# Check disk jpeters
du -sh /home/yourusername/PDF-Editor-private/*

# Clean up files
find uploads -type f -delete
```

### Debugging Checklist
- [ ] Python 3.13 selected in Web tab
- [ ] Virtual environment created and set
- [ ] All dependencies installed in venv
- [ ] WSGI file updated with correct paths
- [ ] Static files mapping configured
- [ ] Directories created (uploads, static/temp, flask_session)
- [ ] Permissions set correctly (755)
- [ ] SECRET_KEY changed from default
- [ ] Error log checked for import errors
- [ ] Disk space available

Good luck with your deployment! 🚀
