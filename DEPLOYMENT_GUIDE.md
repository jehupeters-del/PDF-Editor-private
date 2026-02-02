# Flask Web Application - Quick Start Guide

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

## Deploy to PythonAnywhere

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com/
2. Sign up for free account
3. Confirm email

### Step 2: Upload Files
Option A - Via Web Interface:
1. Go to "Files" tab
2. Create directory: `/home/yourusername/PDF-Editor`
3. Upload all project files

Option B - Via Git (recommended):
1. Go to "Consoles" tab
2. Start a Bash console
3. Run:
   ```bash
   git clone YOUR_REPO_URL PDF-Editor
   cd PDF-Editor
   ```

### Step 3: Install Dependencies
In the Bash console:
```bash
cd PDF-Editor
pip3 install --user -r requirements.txt
```

### Step 4: Create Required Directories
```bash
mkdir -p uploads
mkdir -p static/temp
mkdir -p flask_session
chmod 755 uploads static/temp flask_session
```

### Step 5: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10 (or latest available)
5. Click through to create app

### Step 6: Edit WSGI Configuration
1. In Web tab, click on WSGI configuration file link
2. Delete all content
3. Copy content from `pythonanywhere_wsgi.py`
4. **IMPORTANT**: Update these lines:
   ```python
   project_home = '/home/yourusername/PDF-Editor'  # Change 'yourusername'
   os.environ['SECRET_KEY'] = 'your-random-secret-key-here'  # Change to random string
   ```
5. Save file

### Step 7: Set Static Files
Still in Web tab, scroll to "Static files" section:
1. Add mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/PDF-Editor/static/`

### Step 8: Reload Web App
1. Scroll to top of Web tab
2. Click green "Reload" button
3. Wait for reload to complete

### Step 9: Test Your App
1. Click the link at top of Web tab (e.g., `yourusername.pythonanywhere.com`)
2. Test all features:
   - Upload PDFs
   - View pages
   - Merge PDFs
   - Extract questions
   - Validate questions

## Troubleshooting

### App shows "Something went wrong"
- Check Error log (link in Web tab)
- Common issues:
  - Wrong path in WSGI file
  - Missing dependencies
  - Directory permissions

### "Import Error: No module named 'flask'"
- Dependencies not installed
- Run: `pip3 install --user -r requirements.txt`
- Make sure you're in the right directory

### Uploads not working
- Check directory exists: `/home/yourusername/PDF-Editor/uploads/`
- Check permissions: `chmod 755 uploads`

### Sessions not persisting
- Check flask_session directory exists and is writable
- Try clearing browser cookies

### Static files (CSS/thumbnails) not loading
- Check Static files mapping in Web tab
- URL should be `/static/`
- Directory should be full path to static folder

## Maintenance

### Clean Up Old Files
Create a scheduled task (in Tasks tab):
```bash
# Run daily at 3 AM
find /home/yourusername/PDF-Editor/uploads/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/yourusername/PDF-Editor/static/temp/* -type d -mmin +120 -exec rm -rf {} + 2>/dev/null
find /home/yourusername/PDF-Editor/flask_session/* -type f -mmin +120 -delete 2>/dev/null
```

### View Logs
- Error log: Shows Python errors
- Server log: Shows HTTP requests
- Both available in Web tab

### Update App
If using Git:
```bash
cd PDF-Editor
git pull
# Reload web app in Web tab
```

If uploading manually:
- Upload changed files via Files tab
- Reload web app in Web tab

## Security Notes

1. **Change SECRET_KEY**: Never use default key in production
2. **File Size Limits**: Default is 50MB, adjust if needed
3. **Rate Limiting**: Consider adding for production use
4. **Authentication**: Current version has no authentication (public access)

## Performance Tips

1. **Free Tier Limits**:
   - 300-second request timeout
   - Limited CPU time per day
   - Avoid processing very large PDFs

2. **Optimization**:
   - Batch operations may timeout on free tier
   - Single-file operations work best
   - Consider upgrading for heavy use

3. **Session Management**:
   - Sessions expire after 2 hours
   - Regular cleanup prevents disk space issues

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Set up cleanup cron job
3. Monitor error logs regularly
4. Consider upgrading plan if needed
5. Add custom domain (paid plans)

## Support Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Flask Documentation: https://flask.palletsprojects.com/
- This project's README: See README_FLASK.md

## Quick Reference

### Important Paths (replace 'yourusername')
- Project: `/home/yourusername/PDF-Editor/`
- WSGI: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
- Logs: Available in Web tab
- Static: `/home/yourusername/PDF-Editor/static/`

### Important Commands
- Install deps: `pip3 install --user -r requirements.txt`
- Check Python: `python3 --version`
- Test import: `python3 -c "import flask; print(flask.__version__)"`

Good luck with your deployment! 🚀
