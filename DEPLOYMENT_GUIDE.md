# PDF Editor Web App - Deployment Guide for PythonAnywhere

## Overview
This guide walks you through deploying the PDF Editor web application on PythonAnywhere, migrated from the Tkinter desktop version.

---

## Prerequisites

1. **PythonAnywhere Account**: Sign up at [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
   - Free tier supports Python 3.10/3.11
   - For Python 3.13, a paid account is required

2. **Local Repository**: Ensure all files are ready for upload

---

## Deployment Steps

### 1. Upload Files to PythonAnywhere

**Option A: Using Git (Recommended)**
```bash
# On PythonAnywhere Bash console
cd ~
git clone https://github.com/yourusername/PDF-Editor.git
cd PDF-Editor
```

**Option B: Manual Upload**
1. Go to **Files** tab in PythonAnywhere dashboard
2. Navigate to `/home/yourusername/`
3. Create directory `PDF-Editor`
4. Upload all files:
   - `app.py`
   - `pdf_manager.py`
   - `pdf_viewer_web.py`
   - `cleanup.py`
   - `requirements.txt`
   - `templates/` folder (all HTML files)
   - `static/` folder (CSS and JS files)

### 2. Create Virtual Environment

```bash
# In PythonAnywhere Bash console
cd ~/PDF-Editor
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure WSGI File

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select Python version (3.11 or 3.13)
5. Click on the WSGI configuration file link
6. Replace the entire contents with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/PDF-Editor'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from app import create_app
application = create_app()

# Set secret key from environment variable (recommended for production)
import os
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production-abc123xyz789')
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username.

### 4. Configure Static Files

In the **Web** tab, scroll to **Static files** section:

| URL                | Directory                                      |
|--------------------|------------------------------------------------|
| `/static/`         | `/home/yourusername/PDF-Editor/static/`        |

Click the checkmark to add each mapping.

### 5. Set Environment Variables

```bash
# In PythonAnywhere Bash console
cd ~/PDF-Editor

# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and set it as environment variable
# Edit .bashrc or .bash_profile
echo 'export SECRET_KEY="your-generated-secret-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 6. Create Upload Directory

```bash
cd ~/PDF-Editor
mkdir -p instance/uploads
chmod 755 instance/uploads
```

### 7. Reload Web App

1. Go to **Web** tab
2. Click **Reload yourusername.pythonanywhere.com**
3. Visit your site: `https://yourusername.pythonanywhere.com`

---

## Setting Up Automatic Cleanup

To prevent storage bloat, configure automatic cleanup of old session files:

### 1. Test Cleanup Script

```bash
cd ~/PDF-Editor
source venv/bin/activate

# Test with dry run
python cleanup.py --dry-run

# Create test sessions
python cleanup.py --test

# Run actual cleanup
python cleanup.py
```

### 2. Schedule Hourly Task

1. Go to **Tasks** tab in PythonAnywhere dashboard
2. Under **Scheduled tasks**, create a new task:
   - **Command**: `/home/yourusername/PDF-Editor/venv/bin/python /home/yourusername/PDF-Editor/cleanup.py`
   - **Hour**: Select "Every hour" or specific hours
   - **Minute**: Set to any minute (e.g., 0)

3. Click **Create**

The cleanup script will now run hourly and delete session folders older than 2 hours.

---

## Configuration Options

Edit `app.py` to customize:

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # Max file size (32MB)
app.config['SECRET_KEY'] = '...'  # Session encryption key
```

Edit `cleanup.py` to customize:

```python
MAX_AGE_HOURS = 2  # Session expiration time
```

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Solution**:
1. Check error logs in **Web** tab → **Log files** → **Error log**
2. Common issues:
   - Missing dependencies: Re-run `pip install -r requirements.txt`
   - Wrong paths in WSGI file: Verify username
   - Permission issues: Run `chmod -R 755 ~/PDF-Editor`

### Issue: Static files not loading

**Solution**:
1. Verify static file mappings in **Web** tab
2. Check that paths are absolute: `/home/yourusername/PDF-Editor/static/`
3. Reload the web app

### Issue: File uploads failing

**Solution**:
1. Check upload directory exists: `mkdir -p ~/PDF-Editor/instance/uploads`
2. Set permissions: `chmod 755 ~/PDF-Editor/instance/uploads`
3. Verify `MAX_CONTENT_LENGTH` is set appropriately

### Issue: Sessions not persisting

**Solution**:
1. Ensure `SECRET_KEY` is set and consistent
2. Check that Flask sessions are enabled (default)
3. Verify browser allows cookies

### Issue: Cleanup script not running

**Solution**:
1. Check scheduled task is created in **Tasks** tab
2. Verify the command path is absolute
3. Test manually: `python ~/PDF-Editor/cleanup.py`
4. Check task logs for errors

---

## Security Best Practices

### 1. Secret Key
Never commit the `SECRET_KEY` to version control. Use environment variables:

```bash
# In PythonAnywhere Bash console
echo 'export SECRET_KEY="'$(python3 -c "import secrets; print(secrets.token_hex(32))")'"' >> ~/.bashrc
source ~/.bashrc
```

### 2. File Size Limits
The default 32MB limit prevents DoS attacks. Adjust based on your needs:

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### 3. File Validation
The app already validates:
- File extensions (PDF only)
- Secure filenames (using `werkzeug.utils.secure_filename`)

### 4. Session Isolation
Each user gets a unique session folder (UUID-based) to prevent data leakage.

---

## Testing the Deployment

### Test Checklist

1. **Upload Test**
   - [ ] Upload 1 PDF file
   - [ ] Upload 3 PDF files simultaneously
   - [ ] Try uploading non-PDF file (should be rejected)
   - [ ] Try uploading file > 32MB (should be rejected)

2. **Editor Test**
   - [ ] View all pages in grid
   - [ ] Select and delete a page
   - [ ] Delete multiple pages using checkboxes
   - [ ] Verify page count updates correctly

3. **Validation Test**
   - [ ] Click "Validate Questions" button
   - [ ] Verify modal displays results
   - [ ] Test with incomplete question set

4. **Extraction Test**
   - [ ] Click "Extract Questions" button
   - [ ] Verify extraction report in modal

5. **Download Test**
   - [ ] Click "Download Merged PDF"
   - [ ] Verify PDF downloads correctly
   - [ ] Open PDF and check content

6. **Multi-User Test**
   - [ ] Open app in two different browsers
   - [ ] Upload different PDFs in each
   - [ ] Verify sessions are isolated (no data overlap)

7. **Cleanup Test**
   - [ ] Create test sessions: `python cleanup.py --test`
   - [ ] Run cleanup: `python cleanup.py`
   - [ ] Verify old sessions are deleted

---

## Performance Optimization

### 1. Thumbnail Generation
For large PDFs (50+ pages), consider implementing lazy loading:

```javascript
// Add to editor.js
const lazyLoadThumbnails = () => {
    const thumbnails = document.querySelectorAll('img[loading="lazy"]');
    // Browser handles lazy loading automatically
};
```

### 2. Session Storage
Monitor disk usage:

```bash
du -sh ~/PDF-Editor/instance/uploads/
```

If storage is filling up:
- Reduce `MAX_AGE_HOURS` in `cleanup.py`
- Increase cleanup frequency (run every 30 minutes)

### 3. Database Alternative (Advanced)
For high-traffic scenarios, consider storing session state in Redis or a database instead of filesystem-based sessions.

---

## Monitoring

### Check Application Logs

```bash
# Error log
tail -f ~/logs/yourusername.pythonanywhere.com.error.log

# Access log
tail -f ~/logs/yourusername.pythonanywhere.com.access.log
```

### Monitor Storage Usage

```bash
# Check upload directory size
du -sh ~/PDF-Editor/instance/uploads/

# Count sessions
ls -1 ~/PDF-Editor/instance/uploads/ | wc -l

# Check oldest session
ls -lt ~/PDF-Editor/instance/uploads/ | tail -1
```

---

## Upgrading

To update the application:

```bash
cd ~/PDF-Editor
git pull  # If using Git

# Or upload new files manually via Files tab

source venv/bin/activate
pip install -r requirements.txt --upgrade

# Reload web app
# Go to Web tab → Reload
```

---

## Migration from Desktop App

### What Changed

| Desktop (Tkinter) | Web (Flask) |
|-------------------|-------------|
| Stateful single-user | Stateless multi-user |
| Local file system | Session-based storage |
| `pdf_viewer.py` (Tk images) | `pdf_viewer_web.py` (Base64 PNG) |
| `main.py` (Tk GUI) | `app.py` (Flask routes) |
| Clipboard output | Modal dialogs |

### What Stayed the Same

- `pdf_manager.py`: Core business logic unchanged
- PDF operations: Merge, validate, extract
- Question validation algorithm
- Smart filename generation

---

## Support & Resources

- **PythonAnywhere Help**: [https://help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Flask Documentation**: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- **PyMuPDF Docs**: [https://pymupdf.readthedocs.io](https://pymupdf.readthedocs.io)

---

## License

This application is for educational use. Ensure compliance with your institution's policies.

---

**Deployment Complete!** 🎉

Your PDF Editor is now accessible at: `https://yourusername.pythonanywhere.com`
