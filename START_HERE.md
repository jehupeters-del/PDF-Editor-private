# 🚀 START HERE - Deploy PDF Editor to PythonAnywhere

**User**: jpeters  
**URL**: https://jpeters.pythonanywhere.com  
**Repo**: https://github.com/jehupeters-del/PDF-Editor-private.git  
**Python**: 3.13  

---

## Prerequisites ✅

Before starting, make sure you have:
- [ ] PythonAnywhere account (free tier is fine)
- [ ] Username is `jpeters`
- [ ] Internet connection

## Step-by-Step Deployment (15 minutes)

### PART 1: Setup on PythonAnywhere (5 minutes)

#### 1. Login to PythonAnywhere
Go to https://www.pythonanywhere.com/ and login as `jpeters`

#### 2. Open a Bash Console
- Click on **"Consoles"** tab at the top
- Click **"Bash"** to start a new bash console

#### 3. Clone the Repository
Copy and paste this command:
```bash
cd ~
git clone https://github.com/jehupeters-del/PDF-Editor-private.git PDF-Editor-private
cd PDF-Editor-private
```

✅ **Expected**: Should see "Cloning into 'PDF-Editor-private'..." and finish successfully

#### 4. Create Virtual Environment
```bash
mkvirtualenv venv --python=python3.13
```

✅ **Expected**: Should see "(venv)" at the start of your prompt

#### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

⏱️ **Wait**: This takes 2-3 minutes. You'll see packages installing.

✅ **Expected**: Should end with "Successfully installed..." message

#### 6. Verify Installation
```bash
python -c "from flask_session import Session; print('✓ Flask-Session OK')"
python -c "import fitz; print('✓ PyMuPDF OK')"
python -c "import flask; print('✓ Flask OK')"
python --version
```

✅ **Expected**: Should see three checkmarks and "Python 3.13.x"

#### 7. Create Required Directories
```bash
mkdir -p uploads static/temp flask_session
chmod 755 uploads static/temp flask_session
ls -la | grep -E 'uploads|static|flask_session'
```

✅ **Expected**: Should see all three directories listed with `drwxr-xr-x` permissions

#### 8. Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

✅ **Expected**: Prints a long random string (64 characters)

📋 **COPY THIS STRING** - You'll need it in Step 13!

---

### PART 2: Configure Web App (5 minutes)

#### 9. Create Web App
- Click on **"Web"** tab at the top
- Click **"Add a new web app"**
- Click **"Next"** (for your domain: jpeters.pythonanywhere.com)
- Select **"Manual configuration"**
- Select **"Python 3.13"** ⚠️ (This is critical!)
- Click **"Next"**

✅ **Expected**: Web app created, you're on the Web app configuration page

#### 10. Set Virtual Environment
On the Web tab, scroll to **"Virtualenv"** section:
- Click in the text box
- Enter: `/home/jpeters/.virtualenvs/venv`
- Press Enter

✅ **Expected**: Shows a checkmark or "OK" next to the path

#### 11. Configure Static Files
Scroll to **"Static files"** section:
- Click **"Enter URL"** in the first empty row
- Enter URL: `/static/`
- Click **"Enter path"** next to it
- Enter Directory: `/home/jpeters/PDF-Editor-private/static/`
- The row should turn blue/green

✅ **Expected**: Mapping shows: `/static/` → `/home/jpeters/PDF-Editor-private/static/`

#### 12. Find WSGI Configuration File
Scroll up to **"Code"** section:
- Find "WSGI configuration file" (looks like: `/var/www/jpeters_pythonanywhere_com_wsgi.py`)
- Click on the file path link

✅ **Expected**: Opens a text editor with Python code

#### 13. Edit WSGI Configuration
You'll see a file with lots of commented code.

**Option A: Complete Replace (Recommended)**
1. Select ALL text (Ctrl+A)
2. Delete it
3. Open your local `pythonanywhere_wsgi.py` file
4. Copy ALL content from that file
5. Paste into the editor
6. Find line 31: `os.environ['SECRET_KEY'] = 'testing-super-secret-random-key'`
7. Replace the value with YOUR secret key from Step 8
8. Click **"Save"** button (top right)

**Option B: Quick Edit (If already updated)**
1. Line 23 should already say: `project_home = '/home/jpeters/PDF-Editor-private'`
2. Line 31: Update SECRET_KEY with your key from Step 8
3. Make sure line 35 has: `os.chdir(project_home)`
4. Click **"Save"** button

✅ **Expected**: File saved successfully

---

### PART 3: Launch & Test (5 minutes)

#### 14. Reload Web App
- Go back to **"Web"** tab (browser back button or click "Web" tab)
- Scroll to top
- Click the big green **"Reload jpeters.pythonanywhere.com"** button
- Wait 5-10 seconds

✅ **Expected**: Shows "Web app reloaded" or similar confirmation

#### 15. Check Error Log
- On Web tab, find **"Log files"** section
- Click **"Error log"** link
- Look at the last few lines

✅ **Expected Success Messages**:
```
Successfully imported Flask app
Changed working directory to: /home/jpeters/PDF-Editor-private
Created directory: /home/jpeters/PDF-Editor-private/uploads
```

❌ **If you see errors**, jump to [Troubleshooting](#troubleshooting-quick-fixes) below

#### 16. Test Your Site! 🎉
- On Web tab, at the very top, click your site link: **jpeters.pythonanywhere.com**
- Should see the PDF Editor homepage

**Test these features:**
1. ✅ Homepage loads
2. ✅ Upload a PDF (use any small PDF)
3. ✅ View pages (should show thumbnails)
4. ✅ Can download the merged PDF

✅ **Expected**: Everything works!

---

## 🎯 YOU'RE DONE! 

Your PDF Editor is live at: **https://jpeters.pythonanywhere.com**

---

## Troubleshooting Quick Fixes

### Error: "flask_session not found"
```bash
# In your Bash console:
cd /home/jpeters/PDF-Editor-private
workon venv
pip install Flask-Session cachelib
```
Then reload web app and check error log again.

### Error: "FileNotFoundError"
Check your WSGI file has this line (around line 35):
```python
os.chdir(project_home)
```
If missing, add it right after the SECRET_KEY line. Save and reload.

### Error: "No module named 'app'"
Your WSGI file path is wrong. Check line 23 in WSGI file:
```python
project_home = '/home/jpeters/PDF-Editor-private'  # Must match exactly
```

### Homepage shows default PythonAnywhere page
- Make sure you clicked "Reload" after changing WSGI file
- Check WSGI file was saved
- Check error log for actual errors

### Static files (CSS) not loading
Double-check Static Files mapping:
- URL: `/static/`
- Directory: `/home/jpeters/PDF-Editor-private/static/`

### Can't download files after extraction
This is fixed if your WSGI has `os.chdir(project_home)`. Verify it's there and reload.

---

## Next Steps After Deployment

### 1. Set Up Automatic Cleanup (Recommended)
Go to **"Tasks"** tab → **"Create a scheduled task"**

**Run daily at 3:00 AM**:
```bash
/home/jpeters/.virtualenvs/venv/bin/python /home/jpeters/PDF-Editor-private/cleanup_task.py
```

(Or manually clean up weekly - see below)

### 2. Monitor Disk Usage
Free tier: 512MB limit. Check regularly:
```bash
cd /home/jpeters/PDF-Editor-private
du -sh *
```

### 3. Manual Cleanup (if needed)
```bash
cd /home/jpeters/PDF-Editor-private
find uploads -type f -mtime +1 -delete
find static/temp -type f -mtime +1 -delete
find flask_session -type f -mtime +1 -delete
```

### 4. Update Your App Later
```bash
cd /home/jpeters/PDF-Editor-private
git pull
workon venv
pip install -r requirements.txt
# Reload web app
```

---

## Important Paths Reference

| What | Path |
|------|------|
| Your URL | https://jpeters.pythonanywhere.com |
| Project Folder | /home/jpeters/PDF-Editor-private |
| WSGI File | /var/www/jpeters_pythonanywhere_com_wsgi.py |
| Virtual Environment | /home/jpeters/.virtualenvs/venv |
| Error Log | Web tab → Log files section |

---

## Commands Cheat Sheet

```bash
# Always activate venv first
workon venv

# Update from GitHub
cd /home/jpeters/PDF-Editor-private && git pull

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version

# Test imports
python -c "from flask_session import Session; print('OK')"

# Check disk usage
du -sh /home/jpeters/PDF-Editor-private/*

# Clean up old files
find /home/jpeters/PDF-Editor-private/uploads -type f -mtime +1 -delete
```

---

## Need More Help?

📘 **Detailed Guides in this repo:**
- `QUICK_SETUP_PYTHONANYWHERE.md` - Quick reference card
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `PYTHONANYWHERE_FIXES.md` - Detailed explanation of all fixes

🆘 **External Help:**
- PythonAnywhere Help: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/

---

## Success Checklist ✅

- [ ] Repository cloned
- [ ] Virtual environment created with Python 3.13
- [ ] Dependencies installed
- [ ] Directories created
- [ ] Web app created with Python 3.13
- [ ] Virtual environment configured in Web tab
- [ ] Static files mapping set
- [ ] WSGI file updated with secret key
- [ ] Web app reloaded
- [ ] Error log shows success messages
- [ ] Homepage loads at jpeters.pythonanywhere.com
- [ ] Can upload and process PDFs
- [ ] Can download results

**If all checked: YOU'RE LIVE! 🎉**

---

**Quick Start Time**: ~15 minutes  
**Difficulty**: Easy (just copy-paste!)  
**Cost**: $0 (Free tier)
