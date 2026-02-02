# PDF Editor - Flask Web Application

A comprehensive web-based PDF editor for educators and professionals. Originally built as a desktop application with Tkinter, now migrated to Flask for easy deployment on PythonAnywhere and other hosting platforms.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py

# Open browser to http://localhost:5000
```

### Deploy to PythonAnywhere
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## Features

### Core PDF Operations
- **PDF Viewer**: Browse and visualize PDF documents page-by-page with thumbnail previews
- **Page Selection**: Select specific pages for extraction or removal
- **Page Removal**: Delete unwanted pages from PDFs
- **PDF Merging**: Combine multiple PDFs into a single document
- **File Management**: Upload, manage, and download PDFs through web interface

### Educational Features

#### Question Validation
Validate test questions to ensure proper numbering and formatting:
- Checks for missing question numbers
- Validates number sequences
- Identifies spacing issues
- Provides detailed validation reports
- Supports single file and batch processing

#### Question Extraction
Extract and organize questions from test PDFs:
- Automatically detects question patterns
- Extracts question numbers and content
- Supports multiple question formats
- Generates structured JSON output
- Single file and batch modes available

## Architecture

- **Backend**: Flask 3.1.0 with Flask-Session for state management
- **Frontend**: Bootstrap 5.3.0 with responsive design
- **PDF Processing**: PyPDF2 and PyMuPDF (fitz) for robust PDF operations
- **Background Tasks**: Threading with AJAX polling for long-running operations
- **Session Management**: Filesystem-based sessions with 2-hour timeout

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Local Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-editor.git
cd pdf-editor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Usage

### Upload PDFs
1. Navigate to the home page
2. Click "Upload PDF" button
3. Select one or more PDF files
4. Files appear in the sidebar

### View and Edit Pages
1. Click on a PDF name in the sidebar
2. View page thumbnails in a grid layout
3. Select pages using checkboxes
4. Use "Remove Selected Pages" to delete unwanted pages
5. Click "Download Modified PDF" to save changes

### Question Extraction
1. Navigate to "Extract Questions" page
2. Choose between single file or batch mode
3. Upload PDF(s)
4. System processes files in background
5. Download extracted results when ready

### Question Validation
1. Navigate to "Validate Questions" page
2. Choose single or batch validation
3. Upload PDF(s)
4. View validation results showing:
   - Missing question numbers
   - Sequence issues
   - Detailed reports for each file

## Project Structure

```
PDF-Editor/
├── app.py                      # Main Flask application
├── pdf_manager.py              # PDF processing logic
├── pdf_viewer.py               # Thumbnail generation
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── base.html              # Base template with Bootstrap
│   ├── index.html             # Home page
│   ├── pdf_view.html          # PDF viewer with page grid
│   ├── extract.html           # Question extraction interface
│   ├── validate.html          # Question validation interface
│   └── task_status.html       # Background task polling
├── static/                    # Static assets (CSS, JS, images)
│   └── temp/                  # Temporary session files
├── uploads/                   # Uploaded PDF files (by session)
├── flask_session/             # Session data storage
└── tests/                     # Test suite

Legacy (Desktop Version):
├── main.py                    # Original Tkinter application
└── archive/                   # Historical documentation
```

## Documentation

- **[README_FLASK.md](README_FLASK.md)** - Detailed Flask application documentation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - PythonAnywhere deployment instructions
- **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Migration summary from Tkinter to Flask
- **[BUGFIX_REQUEST_CONTEXT.md](BUGFIX_REQUEST_CONTEXT.md)** - Request context bug fix details

## Desktop Version

The original Tkinter desktop application is preserved as `main.py`. To run the desktop version:

```bash
python main.py
```

Note: The desktop version requires a display environment and cannot be deployed to web hosting platforms.

## Development

### Running Tests
```bash
# Run pre-deployment tests
python test_flask_app.py

# Run all test suites
pytest tests/
```

### Creating Test PDFs
```bash
python create_test_pdfs.py
```

## Requirements

- Flask==3.0.0
- Flask-Session==0.5.0
- Werkzeug==3.0.1
- PyPDF2==3.0.1
- PyMuPDF==1.24.0
- Pillow>=10.0.0

See [requirements.txt](requirements.txt) for complete dependency list.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask and Bootstrap
- PDF processing powered by PyPDF2 and PyMuPDF
- Originally developed as a desktop application for educators

## Support

For issues, questions, or deployment help, please see the documentation files or open an issue on GitHub.
