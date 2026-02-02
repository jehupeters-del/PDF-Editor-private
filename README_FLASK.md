# PDF Editor - Flask Web Application

A web application for loading, viewing, manipulating, and merging PDF files. Migrated from Tkinter desktop app to Flask for deployment on PythonAnywhere.

## Features

### Core PDF Management
- **Multi-PDF Upload**: Upload multiple PDF files at once
- **PDF List View**: Sidebar showing all loaded PDFs
- **Page Grid View**: Responsive thumbnail grid of PDF pages
- **Page Operations**: Remove individual pages or batch remove selected pages
- **PDF Merging**: Combine all loaded PDFs into a single downloadable file

### Question Extraction
- **Single Mode**: Extract question pages from one PDF
- **Batch Mode**: Process multiple PDFs simultaneously
- **Smart Naming**: Automatic output filename generation (e.g., "June 2013 solutions.pdf")
- **Validation**: Automatic validation after extraction to ensure no questions were lost
- **First Page Preservation**: Always keeps the title page

### Question Validation
- **Pattern Detection**: Searches for "Question {number}" pattern
- **Continuity Check**: Verifies all numbers from 1 to max are present
- **Single & Batch Modes**: Validate one or multiple PDFs
- **Missing Detection**: Reports specific missing question numbers
- **Special Warnings**: Alerts if Question 1 is missing

## Installation

### Local Development

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   - Navigate to `http://localhost:5000`

### PythonAnywhere Deployment

1. **Upload files to PythonAnywhere:**
   - Upload all project files via Files tab or Git
   - Create directories: `templates/`, `static/`, `uploads/`, `flask_session/`

2. **Install dependencies:**
   ```bash
   pip3 install --user -r requirements.txt
   ```

3. **Configure WSGI file** (see `pythonanywhere_wsgi.py`):
   - In Web tab, edit WSGI configuration file
   - Point to your app.py location
   - Set up virtual environment if using one

4. **Set environment variables:**
   - In Web tab, set `SECRET_KEY` environment variable
   - Use a strong random key for production

5. **Reload web app** in PythonAnywhere dashboard

## Project Structure

```
PDF-Editor/
├── app.py                  # Flask application with routes
├── pdf_manager.py          # PDF operations backend (unchanged)
├── pdf_viewer.py           # Thumbnail generation (modified for web)
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html          # Base template with Bootstrap
│   ├── index.html         # Home page with PDF list
│   ├── pdf_view.html      # Page grid view
│   ├── extract.html       # Question extraction interface
│   ├── validate.html      # Question validation interface
│   └── task_status.html   # Background task status with polling
├── static/                 # Static files
│   └── temp/              # Session-based thumbnail storage
├── uploads/                # Session-based PDF uploads
├── flask_session/          # Flask-Session storage
├── main.py                 # Original Tkinter app (kept for reference)
└── README.md              # This file
```

## Usage

### Loading PDFs
1. Click "Load PDFs" button
2. Select one or multiple PDF files
3. Click a PDF in the sidebar to view its pages

### Viewing Pages
- Click on a PDF to see thumbnail grid
- Click pages to select/deselect them
- Use "Remove Selected Pages" to batch delete

### Merging PDFs
1. Load multiple PDFs
2. Optionally remove unwanted pages
3. Click "Merge & Download PDF"
4. File downloads automatically

### Extracting Questions
1. Navigate to Extract page
2. Choose Single or Batch mode
3. Upload PDF(s)
4. Wait for processing (with progress indicator)
5. Download extracted files

### Validating Questions
1. Navigate to Validate page
2. Choose Single or Batch mode
3. Upload PDF(s)
4. View validation results
5. See missing question numbers if any

## Technical Details

### Session Management
- Uses Flask-Session with filesystem storage
- Each user gets isolated session (session_id)
- Sessions expire after 2 hours of inactivity
- Uploaded files stored in `uploads/{session_id}/`
- Thumbnails stored in `static/temp/{session_id}/`

### Background Processing
- Uses threading for long operations
- AJAX polling (1-second interval) for status updates
- Task results stored in memory (use Redis for production scale)
- Supports extract and validate operations in single/batch modes

### File Handling
- Max upload size: 50MB per request
- Supported format: PDF only
- Thumbnails generated at 180px width
- Automatic cleanup recommended (cron job)

### Security Considerations
- Public access (no authentication)
- Secure filename sanitization
- Session isolation prevents cross-user access
- Set strong SECRET_KEY in production
- Consider adding rate limiting for production

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (required for production)
- `MAX_CONTENT_LENGTH`: Max upload size in bytes

### app.py Configuration
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2 hours
```

## Differences from Desktop Version

| Feature | Desktop (Tkinter) | Web (Flask) |
|---------|------------------|-------------|
| UI Framework | Tkinter widgets | Bootstrap 5 + HTML |
| State Storage | In-memory | Flask-Session (filesystem) |
| File Selection | Native OS dialog | HTML file input |
| Background Tasks | Threading + root.after() | Threading + AJAX polling |
| File Download | User-chosen location | Browser download |
| Thumbnails | PhotoImage (in-memory) | PNG files in static/ |
| Multi-user | Single user | Multiple concurrent users |

## Known Limitations

1. **PythonAnywhere Free Tier:**
   - 300-second request timeout (may affect large batch operations)
   - Limited CPU time
   - No WebSockets (uses polling instead)

2. **Session Storage:**
   - Files persist until manual cleanup
   - Recommend implementing cleanup cron job
   - Consider Redis for production scale

3. **Memory Usage:**
   - Background tasks store results in memory
   - Large batch operations may consume significant RAM

## Cleanup Recommendations

Add a cron job to clean up old sessions:

```bash
# Clean up sessions older than 2 hours
find ./uploads/* -type d -mmin +120 -exec rm -rf {} +
find ./static/temp/* -type d -mmin +120 -exec rm -rf {} +
find ./flask_session/* -type f -mmin +120 -delete
```

## Troubleshooting

### "Session not found" errors
- Clear browser cookies
- Check flask_session/ directory permissions

### Thumbnails not displaying
- Check static/temp/ directory permissions
- Verify PyMuPDF is installed correctly

### Upload fails
- Check MAX_CONTENT_LENGTH setting
- Verify uploads/ directory exists and is writable

### Task stuck at "Processing..."
- Check app.py console for errors
- Verify background threads are running
- Check for exceptions in PDF processing

## License

Same as original project.

## Credits

Migrated from Tkinter desktop application to Flask web application.
Original functionality and PDF operations logic preserved from desktop version.
