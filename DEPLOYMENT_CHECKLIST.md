# ✅ DEPLOYMENT CHECKLIST - jpeters

> For Streamlit Community Cloud deployment, use **[STREAMLIT_DEPLOYMENT_CHECKLIST.md](STREAMLIT_DEPLOYMENT_CHECKLIST.md)** with entrypoint `streamlit_app.py`.

## Pre-Flight Check
- [ ] Logged into PythonAnywhere as `jpeters`
- [ ] On Dashboard page

---

## 🔧 PART 1: Bash Console Setup

### Open Bash Console
- [ ] Click "Consoles" tab → Click "Bash"

### Commands to Run (Copy-Paste Each)

```bash
# 1. Clone repo
cd ~
git clone https://github.com/jehupeters-del/PDF-Editor-private.git PDF-Editor-private
cd PDF-Editor-private
```
- [ ] ✅ Cloning completed

```bash
# 2. Create virtual environment
mkvirtualenv venv --python=python3.13
```
- [ ] ✅ See "(venv)" in prompt

```bash
# 3. Install packages (takes 2-3 min)
pip install -r requirements.txt
```
- [ ] ✅ "Successfully installed..." shown

```bash
# 4. Verify installation
python -c "from flask_session import Session; print('✓ OK')"
python -c "import fitz; print('✓ OK')"
python -c "import flask; print('✓ OK')"
```
- [ ] ✅ Three "✓ OK" messages

```bash
# 5. Create directories
mkdir -p uploads static/temp flask_session
chmod 755 uploads static/temp flask_session
```
- [ ] ✅ No errors

```bash
# 6. Generate secret key - COPY THE OUTPUT!
python -c "import secrets; print(secrets.token_hex(32))"
```
- [ ] ✅ Copied 64-character string: `________________________________`

---

## 🌐 PART 2: Web Tab Configuration

### Create Web App
- [ ] Click "Web" tab
- [ ] Click "Add a new web app"
- [ ] Click "Next"
- [ ] Select "Manual configuration"
- [ ] Select "Python 3.13" ⚠️ CRITICAL
- [ ] Click "Next"

### Configure Virtual Environment
- [ ] Find "Virtualenv" section
- [ ] Enter: `/home/jpeters/.virtualenvs/venv`
- [ ] Press Enter
- [ ] ✅ Path accepted

### Configure Static Files
- [ ] Find "Static files" section
- [ ] URL: `/static/`
- [ ] Directory: `/home/jpeters/PDF-Editor-private/static/`
- [ ] ✅ Mapping added

### Edit WSGI File
- [ ] Find "Code" section
- [ ] Click WSGI file link: `/var/www/jpeters_pythonanywhere_com_wsgi.py`
- [ ] Select All (Ctrl+A) and Delete
- [ ] Open local file: `pythonanywhere_wsgi.py`
- [ ] Copy ALL content
- [ ] Paste into editor
- [ ] Find line 31: `os.environ['SECRET_KEY']`
- [ ] Replace with YOUR key from step 6
- [ ] Click "Save"
- [ ] ✅ File saved

---

## 🚀 PART 3: Launch

### Reload App
- [ ] Go back to "Web" tab
- [ ] Click green "Reload jpeters.pythonanywhere.com" button
- [ ] Wait 10 seconds

### Check Error Log
- [ ] Click "Error log" link
- [ ] Look for:
  - [ ] ✅ "Successfully imported Flask app"
  - [ ] ✅ "Changed working directory to: /home/jpeters/PDF-Editor-private"

### Test Your Site
- [ ] Click: `jpeters.pythonanywhere.com`
- [ ] ✅ Homepage loads
- [ ] ✅ Upload a PDF
- [ ] ✅ View pages
- [ ] ✅ Download works

---

## 🎉 SUCCESS!

Your site is live at: **https://jpeters.pythonanywhere.com**

---

## 🆘 IF SOMETHING FAILS

### Flask-Session Error
```bash
workon venv
pip install Flask-Session cachelib
```
Then reload web app.

### FileNotFoundError
Check WSGI file has line 35:
```python
os.chdir(project_home)
```

### Module Not Found
Check WSGI line 23:
```python
project_home = '/home/jpeters/PDF-Editor-private'
```

### Can't Find Error
Check error log: Web tab → "Error log" link

---

## 📊 MAINTENANCE

### Weekly Cleanup
```bash
cd /home/jpeters/PDF-Editor-private
find uploads -type f -mtime +1 -delete
find static/temp -type f -mtime +1 -delete
```

### Check Disk Usage
```bash
du -sh /home/jpeters/PDF-Editor-private/*
```

### Update from GitHub
```bash
cd /home/jpeters/PDF-Editor-private
git pull
workon venv
pip install -r requirements.txt
# Reload web app
```

---

## 📞 NEED HELP?

1. Check `START_HERE.md` - Step-by-step guide
2. Check `DEPLOYMENT_GUIDE.md` - Full documentation
3. Check error log in Web tab
4. https://help.pythonanywhere.com/

---

**Estimated Time**: 15 minutes  
**Difficulty**: Easy  
**Cost**: Free
