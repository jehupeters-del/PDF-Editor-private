# PDF Editor

A desktop PDF editor application for loading, viewing, manipulating, and merging multiple PDF documents.

## Features

- 📁 **Load Multiple PDFs**: Select and manage multiple PDF files simultaneously
- 👁️ **Visual Page Preview**: View page thumbnails in an organized grid
- ✂️ **Page Management**: Remove unwanted pages from any PDF
- 📑 **PDF Management**: Remove entire PDFs from the workspace
- 🔗 **Merge PDFs**: Combine all pages into a single downloadable PDF
- 💻 **Offline**: Runs completely offline with no network requirements

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Poppler (for PDF rendering)

### Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Poppler** (required for pdf2image):

**Windows**:
- Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
- Extract and add `bin` folder to your system PATH
- Or place `poppler/bin` in your project directory

**Linux**:
```bash
sudo apt-get install poppler-utils
```

**macOS**:
```bash
brew install poppler
```

### Running the Application

```bash
python main.py
```

## Usage

1. **Load PDFs**: Click "Load PDF Files" button and select one or more PDF files
2. **View Pages**: Click a PDF in the sidebar to see its pages as thumbnails
3. **Remove Pages**: Click the "Remove" button under any page thumbnail
4. **Remove PDFs**: Select a PDF and click "Remove Selected PDF"
5. **Merge**: Click "Merge & Download PDF" to save the combined PDF

## Technology Stack

- **Python 3** - Core language
- **tkinter** - GUI framework (built into Python)
- **PyPDF2** - PDF manipulation and merging
- **Pillow (PIL)** - Image processing (optional — not required for thumbnail generation)
- **pdf2image** - PDF to image conversion
- **PyMuPDF (fitz)** - Used for thumbnail generation (preferred). Thumbnails are generated from page PNG bytes via PyMuPDF and displayed with `tk.PhotoImage`, so Pillow is optional.

### Running tests

- Install test runner: `pip install pytest`
- Run tests: `pytest`

Note: Some tests require a working Tcl/Tk installation. If Tcl/Tk isn't available in your environment those tests will be skipped.
## Project Structure

```
├── main.py           # Main application with tkinter UI
├── pdf_manager.py    # PDF operations (load, remove, merge)
├── pdf_viewer.py     # PDF rendering and thumbnail generation
└── requirements.txt  # Python dependencies
```

## License

MIT
