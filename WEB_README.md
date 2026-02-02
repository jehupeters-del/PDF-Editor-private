# PDF Editor - Web Version

A Flask-based web application for merging, editing, and validating PDF exam documents. Migrated from a Tkinter desktop application for increased accessibility and multi-user support.

## Features

- **Multi-File Upload**: Upload multiple PDF files simultaneously via drag-and-drop or file browser
- **Visual Page Grid**: View all pages from multiple PDFs in an interactive grid layout
- **Page Management**: Delete unwanted pages individually or in bulk
- **Question Validation**: Automatically validate sequential question numbering
- **Question Extraction**: Extract pages containing questions and remove unnecessary content
- **Smart Merge**: Combine PDFs with intelligent filename generation
- **Session Isolation**: Multiple users can work simultaneously without data conflicts
- **Automatic Cleanup**: Old session data is automatically purged to prevent storage bloat

## Tech Stack

- **Backend**: Flask 3.0, Python 3.11+
- **PDF Processing**: PyMuPDF (fitz), PyPDF2
- **Frontend**: HTML5, CSS Grid, Vanilla JavaScript
- **Template Engine**: Jinja2
- **Deployment**: PythonAnywhere

## Quick Start (Local Development)

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PDF-Editor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
PDF-Editor/
├── app.py                      # Flask application (main entry point)
├── pdf_manager.py              # Core PDF business logic
├── pdf_viewer_web.py           # Web-compatible PDF thumbnail generator
├── cleanup.py                  # Session cleanup script
├── requirements.txt            # Python dependencies
├── DEPLOYMENT_GUIDE.md         # PythonAnywhere deployment instructions
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── upload.html            # Upload page
│   └── editor.html            # Page editor with grid view
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       ├── modal.js           # Modal dialog functionality
│       ├── upload.js          # File upload handling
│       └── editor.js          # Page grid interactions
└── instance/                   # Runtime data (not in version control)
    └── uploads/               # Session-based file storage
        └── {session-id}/      # Per-session directories
```

## Architecture

### Session Management

The application uses Flask sessions with UUID-based session IDs to maintain state:

- Each user gets a unique session ID on first visit
- Files are stored in `instance/uploads/{session_id}/`
- PDF manager state is serialized to session storage
- Sessions are isolated - users never see each other's data

### File Storage Strategy

```
instance/uploads/
└── abc123-def456-ghi789/          # Session UUID
    ├── .timestamp                 # Creation time for cleanup
    ├── exam_part1.pdf            # Uploaded file 1
    ├── exam_part2.pdf            # Uploaded file 2
    └── merged_exam.pdf           # Generated output
```

### State Flow

```
1. Upload Page (/):
   - User uploads PDFs
   - POST /upload → saves files to session folder
   - Initializes PDFManager with file paths
   - Redirects to editor

2. Editor Page (/editor):
   - Loads PDFManager from session
   - Generates thumbnails for all pages
   - Displays interactive grid

3. API Endpoints:
   - POST /api/delete_page → removes page, updates session
   - POST /api/validate → checks question continuity
   - POST /api/extract → generates extraction report
   - GET /download → merges PDFs and sends file

4. Cleanup (scheduled):
   - Runs hourly via cleanup.py
   - Deletes folders older than 2 hours
```

## API Reference

### Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page with upload interface |
| POST | `/upload` | Handle file uploads |
| GET | `/editor` | Page grid editor |
| POST | `/api/delete_page` | Delete a specific page |
| POST | `/api/validate` | Validate question continuity |
| POST | `/api/extract` | Extract question pages (preview) |
| GET | `/download` | Download merged PDF |
| GET | `/reset` | Clear session and restart |

### API Examples

**Delete a page:**
```javascript
fetch('/api/delete_page', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({page_id: 'abc-123-page-0'})
})
```

**Validate questions:**
```javascript
fetch('/api/validate', {method: 'POST'})
.then(res => res.json())
.then(data => {
    // data.is_valid, data.missing_questions, data.max_question
})
```

## Core Functionality

### PDF Manager (`pdf_manager.py`)

Preserved from the desktop version with minimal changes:

- `add_pdf(file_path)`: Load a PDF into the manager
- `remove_pdf(pdf_id)`: Remove all pages from a PDF
- `remove_page(page_id)`: Delete a single page
- `merge_all(output_path)`: Combine all pages into one PDF
- `validate_question_continuity(pdf_path)`: Check for missing questions
- `extract_question_pages(input, output)`: Extract pages with questions
- `generate_smart_filename(name)`: Create intelligent output filenames

### PDF Viewer Web (`pdf_viewer_web.py`)

Replaces Tkinter-dependent `pdf_viewer.py`:

- `generate_thumbnail_base64(path, page_index, width)`: Returns Base64 PNG for HTML
- `generate_thumbnail_bytes(path, page_index, width)`: Returns raw PNG bytes

### Cleanup Script (`cleanup.py`)

Prevents storage bloat by removing old sessions:

- Scans `instance/uploads/` directory
- Reads `.timestamp` file from each session folder
- Deletes folders older than configured threshold (default: 2 hours)
- Logs actions and freed storage

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions on deploying to PythonAnywhere.

Quick summary:
1. Upload files to PythonAnywhere
2. Create virtual environment and install dependencies
3. Configure WSGI file
4. Map static files
5. Set up scheduled cleanup task
6. Reload web app

## Configuration

### Environment Variables

```bash
# Secret key for session encryption (REQUIRED for production)
export SECRET_KEY="your-secure-random-key-here"
```

### Application Settings (`app.py`)

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload
app.config['UPLOAD_FOLDER'] = Path('instance/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
```

### Cleanup Settings (`cleanup.py`)

```python
MAX_AGE_HOURS = 2      # Session expiration time
DRY_RUN = False        # Set True for testing without deletion
```

## Security Features

1. **File Validation**
   - Only PDF files allowed
   - Filenames sanitized with `secure_filename()`
   - File size limited (32MB default)

2. **Session Isolation**
   - UUID-based session folders
   - No cross-session data access
   - Encrypted session cookies

3. **Automatic Cleanup**
   - Old sessions auto-deleted
   - Prevents storage exhaustion
   - Configurable retention period

4. **No Persistent Storage**
   - No database → no data breaches
   - Temporary files only
   - Stateless architecture

## Differences from Desktop Version

| Aspect | Desktop (Tkinter) | Web (Flask) |
|--------|-------------------|-------------|
| **UI Framework** | Tkinter | HTML/CSS/JavaScript |
| **State** | In-memory | Session-based |
| **Users** | Single | Multiple concurrent |
| **Thumbnails** | PhotoImage | Base64 PNG |
| **Clipboard** | OS clipboard | Modal dialogs |
| **Persistence** | None | Session cookies |
| **Deployment** | Local install | Web server |

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance Notes

- **Thumbnail Generation**: Generated on-demand during page load. For PDFs with 50+ pages, expect 2-5 seconds load time.
- **Lazy Loading**: Images use `loading="lazy"` attribute for deferred rendering.
- **Session Storage**: Filesystem-based. For high traffic, consider Redis.

## Troubleshooting

### Common Issues

**Upload fails:**
- Check file size < 32MB
- Verify file is actually a PDF
- Check browser console for errors

**Pages not displaying:**
- Verify PyMuPDF is installed correctly
- Check server logs for thumbnail generation errors
- Ensure PDF is not corrupted

**Session lost:**
- Check browser allows cookies
- Verify `SECRET_KEY` is set
- Session may have expired (>2 hours)

## Contributing

This project was migrated from a Tkinter desktop application. When contributing:

1. **Preserve `pdf_manager.py`**: Core logic should remain framework-agnostic
2. **Web-specific code**: Keep in `app.py` and `pdf_viewer_web.py`
3. **Session safety**: All state must be serializable to session storage
4. **Multi-user**: Test with concurrent sessions

## License

Educational use only. Check with your institution for deployment policies.

## Credits

- Original desktop version: Tkinter-based local application
- Web migration: Flask conversion for PythonAnywhere deployment
- PDF processing: PyMuPDF and PyPDF2 libraries

## Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review server error logs
3. Test with `--dry-run` mode for cleanup issues

---

**Built for Teachers, by Teachers** 📚✨
