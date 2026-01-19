# PDF Editor

A comprehensive desktop PDF editor for educators and professionals. Load, view, edit, validate, and merge PDF documents with specialized tools for educational materials.

## Features

### Core PDF Operations
- 📁 **Load Multiple PDFs** - Select and manage multiple PDF files simultaneously
- 👁️ **Visual Page Preview** - View page thumbnails in an organized grid
- ✂️ **Page Management** - Remove unwanted pages from any PDF
- 📑 **PDF Management** - Remove entire PDFs from the workspace
- 🔗 **Merge PDFs** - Combine all pages into a single downloadable PDF
- 💻 **Offline** - Runs completely offline with no network requirements

### Educational Features
- ✅ **Question Validation** - Automatically verify that exam questions are sequential and complete
  - Single PDF validation with detailed results
  - Batch validation for multiple files
  - Export results to CSV or copy to clipboard
  - Detects missing question numbers (e.g., Question 1, 2, 4... will flag missing Question 3)

- 📄 **Question Extraction** - Extract only question pages from exam PDFs
  - Automatically keeps title page
  - Removes instruction pages, answer keys, and non-question content
  - Smart filename generation (e.g., `pc_mg_jun_13.pdf` → `June 2013 solutions.pdf`)
  - Batch extraction for multiple files
  - File size optimization (garbage collection + lossless compression)
  - Preserves all content: images, graphs, diagrams, math equations

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Poppler (for PDF rendering)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/jehupeters-del/PDF-Editor-private.git
cd PDF-Editor-private
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Poppler** (required for pdf2image):

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

### Basic PDF Operations
1. **Load PDFs** - Click "📁 Load PDF Files" and select one or more PDF files
2. **View Pages** - Click a PDF in the sidebar to see its pages as thumbnails
3. **Remove Pages** - Click the "🗑️ Remove" button under any page thumbnail
4. **Remove PDFs** - Select a PDF and click "🗑️ Remove Selected PDF"
5. **Merge** - Click "📥 Merge & Download PDF" to save the combined PDF

### Question Validation
1. **Single PDF** - Click "✅ Validate Questions", choose "No" for single mode
   - Results show if questions are sequential (1, 2, 3...)
   - Lists any missing question numbers

2. **Batch Validation** - Click "✅ Validate Questions", choose "Yes" for batch mode
   - Select multiple PDFs to validate at once
   - View results in a summary window
   - Export to CSV or copy to clipboard

### Question Extraction
1. **Single PDF** - Click "✂️ Extract Questions Only", choose "No" for single mode
   - Select input PDF and output location
   - Automatically keeps title page + question pages
   - Smart filename suggested based on input name

2. **Batch Extraction** - Click "✂️ Extract Questions Only", choose "Yes" for batch mode
   - Select multiple PDFs
   - Choose output folder
   - All files processed with smart naming
   - View extraction summary with before/after page counts

## Technology Stack

- **Python 3.8+** - Core language
- **tkinter** - GUI framework (built into Python)
- **PyPDF2 3.0.1** - PDF manipulation and merging
- **PyMuPDF (fitz) 1.26.7** - Fast PDF text extraction, rendering, and optimization
- **pdf2image** - PDF to image conversion for thumbnails
- **Pillow (PIL)** - Image processing

## Project Structure

```
PDF-Editor/
├── main.py              # Main GUI application
├── pdf_manager.py       # PDF operations (load, merge, validate, extract)
├── pdf_viewer.py        # PDF rendering and thumbnail generation
├── requirements.txt     # Python dependencies
└── tests/               # Comprehensive test suite
    ├── test_pdf_manager.py
    ├── test_pdf_viewer.py
    ├── test_question_validator.py
    ├── test_content_preservation.py
    └── ...
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_pdf_manager.py

# Run with verbose output
pytest -v
```

### Key Implementation Details

**Question Detection**: Uses regex pattern `\bquestion\s+(\d+)\b` (case-insensitive) to find question numbers.

**File Optimization**: Extraction uses PyMuPDF's `save()` with:
- `garbage=4` - Maximum garbage collection (removes unused objects)
- `deflate=True` - Lossless compression of content streams
- `clean=True` - Clean and optimize PDF structure

**Content Preservation**: All visual content is preserved during extraction:
- Vector graphics (shapes, lines, diagrams)
- Embedded images (photos, scanned content)
- Mathematical notation and symbols
- Tables and formatting

## License

MIT
