# PythonAnywhere Quick Setup Card - jpeters

## Your Configuration
- **Username**: jpeters
- **Project**: PDF-Editor-private
- **Repository**: https://github.com/jehupeters-del/PDF-Editor-private.git
- **URL**: https://jpeters.pythonanywhere.com
- **Python**: 3.13

## Before You Start
- [ ] PythonAnywhere account created (username: jpeters)
- [ ] Ready to clone repo from GitHub
- [ ] Web app created (Manual configuration, Python 3.13)

## Setup Commands (Copy & Paste)

### 1. Clone Repository
```bash
cd ~
git clone https://github.com/jehupeters-del/PDF-Editor-private.git PDF-Editor-private
cd PDF-Editor-private
```

### 2. Create Virtual Environment
```bash
mkvirtualenv venv --python=python3.13
```

### 3. Install Dependencies
```bash
workon venv
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "from flask_session import Session; print('Flask-Session: OK')"
python -c "import fitz; print('PyMuPDF: OK')"
python -c "import flask; print('Flask: OK')"
python --version  # Should show 3.13.x
```

### 5. Create Directories
```bash
mkdir -p uploads static/temp flask_session
chmod 755 uploads static/temp flask_session
```

### 6. Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output - you'll need it for WSGI file
```

## Web App Configuration

### Virtualenv (in Web tab)
```
/home/jpeters/.virtualenvs/venv
```

### Static Files (in Web tab)
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/jpeters/PDF-Editor-private/static/` |

### WSGI File (`/var/www/jpeters_pythonanywhere_com_wsgi.py`)

**Your WSGI file is already configured with username!**
Just need to update the SECRET_KEY on line 31:

```python
os.environ['SECRET_KEY'] = 'paste-your-generated-key-here-from-step-6'
```

The project path is already set to:
```python
project_home = '/home/jpeters/PDF-Editor-private'
```

## After Setup - Reload & Test

1. Click "Reload" button in Web tab
2. Check "Error log" for any errors
3. Visit your site: **https://jpeters.pythonanywhere.com**

## Troubleshooting Commands

### Check Error Log
Look for these success messages:
- "Successfully imported Flask app"
- "Changed working directory to: /home/jpeters/PDF-Editor-private"

### If Flask-Session Error
```bash
workon venv
pip install Flask-Session cachelib
# Reload web app
```

### Check Disk Usage
```bash
du -sh /home/jpeters/PDF-Editor-private/*
quota
```

### Clean Up Space
```bash
cd /home/jpeters/PDF-Editor-private
find uploads -type f -delete
find static/temp -type f -delete
find flask_session -type f -delete
```

## Maintenance (Run Weekly)

```bash
cd /home/jpeters/PDF-Editor-private
workon venv

# Update from Git
git pull

# Update dependencies if needed
pip install --upgrade -r requirements.txt

# Clean old files
find uploads -type f -mtime +1 -delete
find static/temp -type f -mtime +1 -delete

# Check disk usage
du -sh *
```

## Common Errors & Fixes

| Error Message | Fix |
|--------------|-----|
| `flask_session not found` | `workon venv && pip install Flask-Session` |
| `FileNotFoundError` | Already fixed in WSGI with `os.chdir()` |
| `OSError: write error` | Run cleanup commands above |
| `Task not found` | App restarted, user needs to re-upload |

## Important Paths (Your Specific Setup)

| What | Path |
|------|------|
| Project | `/home/jpeters/PDF-Editor-private/` |
| WSGI File | `/var/www/jpeters_pythonanywhere_com_wsgi.py` |
| Virtual Env | `/home/jpeters/.virtualenvs/venv` |
| Python | `/usr/bin/python3.13` |
| Your URL | `https://jpeters.pythonanywhere.com` |

## Testing Checklist

After deployment:
- [ ] Homepage loads at jpeters.pythonanywhere.com
- [ ] Upload single PDF
- [ ] View PDF pages
- [ ] Merge 2+ PDFs
- [ ] Extract questions (single)
- [ ] Extract questions (batch)
- [ ] Download extracted file
- [ ] Check Error log (no errors)

## Need Help?

1. Check Error log in Web tab
2. See `PYTHONANYWHERE_FIXES.md` for detailed troubleshooting
3. See `DEPLOYMENT_GUIDE.md` for comprehensive guide
4. PythonAnywhere help: https://help.pythonanywhere.com/

---

**Remember**: 
- Always activate venv before pip commands: `workon venv`
- Reload web app after any changes
- Clean up old files regularly (512MB limit!)
- Monitor Error log for issues
