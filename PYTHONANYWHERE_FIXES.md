# PythonAnywhere Python 3.13 Deployment Fixes

## Quick Reference for jpeters
- **Username**: jpeters
- **Project Path**: `/home/jpeters/PDF-Editor-private`
- **Repository**: https://github.com/jehupeters-del/PDF-Editor-private.git
- **URL**: https://jpeters.pythonanywhere.com
- **Python Version**: 3.13

## Summary of Changes

This document outlines all the fixes made to resolve PythonAnywhere deployment issues with Python 3.13.

## Issues Fixed

### 1. Flask-Session Import Error ✅
**Problem**: `from flask_session import Session` failing on PythonAnywhere

**Solution**:
- Updated [app.py](app.py#L1-L45) to gracefully handle missing Flask-Session with try/except
- Added clear error message if Flask-Session not installed
- Updated [requirements.txt](requirements.txt) with flexible version constraints (>= instead of ==)

**Installation Command**:
```bash
workon venv
pip install Flask-Session cachelib
```

### 2. FileNotFoundError for Batch Output PDFs ✅
**Problem**: Files saved in one session directory but downloaded from another

**Root Cause**: 
- Working directory not set correctly in WSGI file
- Relative paths (./uploads) resolved to wrong location

**Solution**:
- Updated [pythonanywhere_wsgi.py](pythonanywhere_wsgi.py) to include `os.chdir(project_home)`
- Changed to absolute paths by setting working directory
- Added comprehensive error logging in download_extracted function
- Improved error messages to help debug path issues

### 3. OSError: Write Error ✅
**Problem**: Multiple "OSError: write error" in logs (disk quota/permissions)

**Solutions Implemented**:

a. **Added comprehensive error handling** in [pdf_manager.py](pdf_manager.py):
   - `merge_all()` function: Catches OSError with detailed messages
   - `extract_question_pages()` function: Catches OSError during PDF save
   - All errors now include helpful context about disk space/quota

b. **Updated DEPLOYMENT_GUIDE.md** with:
   - Disk cleanup commands
   - Monitoring disk usage instructions
   - Scheduled task setup for automatic cleanup
   - Free tier limitations (512MB)

c. **Cleanup Commands**:
```bash
# Manual cleanup
find /home/yourusername/PDF-Editor-private/uploads -type f -delete
find /home/yourusername/PDF-Editor-private/static/temp -type f -delete
find /home/yourusername/PDF-Editor-private/flask_session -type f -delete

# Check disk usage
du -sh /home/yourusername/PDF-Editor-private/*
quota
```

### 4. Python 3.13 Compatibility ✅
**Problem**: Need to ensure all components work with Python 3.13

**Solution**:
- Updated [requirements.txt](requirements.txt) with note about Python 3.13 compatibility
- Updated [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) with Python 3.13 specific instructions
- Verified all dependencies support Python 3.13
- Added virtual environment setup instructions for Python 3.13

### 5. WSGI Configuration ✅
**Problem**: Original WSGI file incomplete and missing critical settings

**Solution**: Completely rewrote [pythonanywhere_wsgi.py](pythonanywhere_wsgi.py):
- Added logging configuration BEFORE imports
- Added `os.chdir(project_home)` to fix working directory
- Added try/except for directory creation with error logging
- Added try/except for Flask app import with helpful error messages
- Added detailed comments for each configuration step
- Better error reporting for troubleshooting

## Files Modified

1. **app.py**
   - Added Flask-Session import error handling
   - Improved download_extracted function with better error handling
   - Added extensive logging for debugging

2. **requirements.txt**
   - Updated to use >= for version flexibility
   - Added Python 3.13 compatibility notes
   - Specified minimum Python version

3. **pythonanywhere_wsgi.py**
   - Complete rewrite with proper error handling
   - Added working directory change
   - Added comprehensive logging
   - Included detailed setup instructions in comments

4. **pdf_manager.py**
   - Added OSError handling to merge_all()
   - Added OSError handling to extract_question_pages()
   - Improved error messages with actionable information

5. **DEPLOYMENT_GUIDE.md**
   - Updated for Python 3.13
   - Added virtual environment setup
   - Added disk cleanup procedures
   - Added troubleshooting for all known issues
   - Added debugging checklist

## New WSGI File - Critical Changes

Your updated WSGI file now includes:

```python
# 1. Logging configured FIRST
logging.basicConfig(level=logging.INFO, ...)

# 2. Path setup
project_home = '/home/jpeters/PDF-Editor-private'  # UPDATE THIS!
sys.path.insert(0, project_home)

# 3. SECRET_KEY environment variable
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # UPDATE THIS!

# 4. CRITICAL: Set working directory
os.chdir(project_home)  # This fixes FileNotFoundError

# 5. Create directories with error handling
try:
    for directory in [uploads_dir, static_temp_dir, flask_session_dir]:
        os.makedirs(directory, mode=0o755, exist_ok=True)
except Exception as e:
    logging.error(f'Error creating directories: {e}')

# 6. Import Flask app with error handling
try:
    from app import app as application
except ImportError as e:
    logging.error('Failed to import app')
    raise
```

## Deployment Steps for PythonAnywhere

### Quick Setup (For jpeters Account)

1. **Clone Repository**:
```bash
cd ~
git clone https://github.com/jehupeters-del/PDF-Editor-private.git PDF-Editor-private
cd PDF-Editor-private
```

2. **Create Virtual Environment**:
```bash
mkvirtualenv venv --python=python3.13
workon venv
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify Flask-Session**:
```bash
python -c "from flask_session import Session; print('Flask-Session OK')"
```

5. **Create Directories**:
```bash
mkdir -p uploads static/temp flask_session
chmod 755 uploads static/temp flask_session
```

6. **Update WSGI File** at `/var/www/jpeters_pythonanywhere_com_wsgi.py`:
   - Project path already set to: `/home/jpeters/PDF-Editor-private`
   - Generate and set SECRET_KEY:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Update line 31 in WSGI file with the generated key

7. **Set Virtual Environment** in Web Tab:
   - Virtualenv: `/home/jpeters/.virtualenvs/venv`

8. **Configure Static Files** in Web Tab:
   - URL: `/static/`
   - Directory: `/home/jpeters/PDF-Editor-private/static/`

9. **Reload** the web app

10. **Check Error Log** for any issues

11. **Test** at https://jpeters.pythonanywhere.com

### Generate Secret Key

Run this in a Python console to generate a secure key:
```python
import secrets
print(secrets.token_hex(32))
```

## Monitoring and Maintenance

### Check Disk Usage
```bash
du -sh /home/jpeters/PDF-Editor-private/*
quota
```

### Clean Up Old Files
```bash
cd /home/jpeters/PDF-Editor-private
find uploads -type f -mtime +1 -delete
find static/temp -type f -mtime +1 -delete
find flask_session -type f -mtime +1 -delete
```

### Set Up Scheduled Cleanup
In PythonAnywhere Tasks tab, create a daily task:
```bash
#!/bin/bash
find /home/jpeters/PDF-Editor-private/uploads/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/jpeters/PDF-Editor-private/static/temp/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/jpeters/PDF-Editor-private/flask_session/* -type f -mmin +120 -delete 2>/dev/null
```

## Testing Checklist

After deployment, verify:
- [ ] Homepage loads
- [ ] Can upload a PDF
- [ ] Can view PDF pages
- [ ] Can merge multiple PDFs
- [ ] Can extract questions (single)
- [ ] Can extract questions (batch)
- [ ] Can download extracted PDFs
- [ ] No errors in Error Log
- [ ] Static files (CSS) load correctly

## Common Errors and Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| "flask_session not found" | `workon venv && pip install Flask-Session` |
| "FileNotFoundError" when downloading | Verify `os.chdir(project_home)` in WSGI |
| "OSError: write error" | Clean up old files, check disk quota |
| "Working directory not found" | Update `project_home` path in WSGI |
| Static files not loading | Check Static Files mapping in Web tab |

## What's Different from Previous Setup

1. **Virtual Environment Required**: Must use venv with Python 3.13
2. **Working Directory Set**: WSGI now sets working directory explicitly
3. **Better Error Handling**: All file operations catch OSError
4. **Flexible Dependencies**: Using >= instead of == for better compatibility
5. **Graceful Degradation**: App works even if Flask-Session fails to import

## Support

If you still encounter issues:

1. Check the Error Log in Web tab
2. Verify all paths in WSGI file
3. Confirm virtual environment is set correctly
4. Check disk quota: `quota`
5. Review the DEPLOYMENT_GUIDE.md for detailed troubleshooting

## Known Limitations on PythonAnywhere

### Background Tasks (In-Memory)
The app stores background task data in-memory (`background_tasks` dictionary). This means:

**Limitation**: If PythonAnywhere restarts your app, in-progress tasks are lost

**Impact**:
- Users may see "Task not found" if app restarts during processing
- Download links for completed tasks become invalid after restart

**Mitigation**:
- Tasks complete quickly (usually < 30 seconds), so restarts are rare
- Users can simply re-upload and process again
- For production, consider upgrading to use Redis or database storage

**Not an Issue for**:
- Direct operations (upload, view, merge) - these work immediately
- Small PDFs that process quickly

### Free Tier Considerations
- **CPU Time**: Limited daily CPU seconds
- **Disk Space**: 512MB total (cleanup is critical!)
- **Request Timeout**: 300 seconds (5 minutes)
- **Concurrency**: One worker (background tasks run sequentially)

**Best Practices**:
- Set up automatic cleanup (see scheduled task above)
- Process one PDF at a time for best results
- Keep individual PDFs under 10MB
- Monitor disk usage regularly

## Success Indicators

You'll know it's working when:
- ✅ Error log shows "Successfully imported Flask app"
- ✅ Error log shows "Changed working directory to: /home/jpeters/PDF-Editor-private"
- ✅ Homepage loads without errors
- ✅ Can upload and process PDFs
- ✅ Can download extracted files
- ✅ No "OSError: write error" messages

---

**Next Steps**: Copy your updated `pythonanywhere_wsgi.py` to the WSGI configuration file on PythonAnywhere and reload your web app!
