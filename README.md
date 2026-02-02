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

#### ✅ Question Validation
Automatically verify that exam questions are sequential and complete. Detects missing question numbers using pattern matching (e.g., "Question 1", "Question 2", etc.).

**Single PDF Mode:**
- Validates one PDF at a time
- Shows detailed results with missing question numbers
- Special warning if Question 1 is missing

**Batch Validation Mode:**
- Validate multiple PDFs at once (Ctrl+Click or Shift+Click to select)
- Comprehensive results window with status indicators (✅ Valid, ⚠️ Issues, ❌ Error)
- Export to text file or copy to clipboard
- Summary statistics showing valid/issues/errors counts

#### 📄 Question Extraction  
Extract only question pages from exam PDFs, automatically removing cover pages, instructions, answer keys, and non-question content.

**Features:**
- Scans for "Question {number}" pattern (case-insensitive)
- Automatically preserves pages with question numbers
- Multi-question support (handles multiple questions on same page)
- Smart filename generation (e.g., `pc_mg_jun_13.pdf` → `June 2013 solutions.pdf`)
- File size optimization (garbage collection + lossless compression)
- Content preservation (images, graphs, diagrams, math equations)
- Validation check after extraction to verify no questions were lost

**Modes:**
- **Single PDF:** Extract one file with custom output name
- **Batch Mode:** Process multiple PDFs with automatic naming

## Getting Started

### Prerequisites

- Python 3.8 or higher

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

**Single PDF Mode:**
1. Click "✅ Validate Questions"
2. Choose "No" when asked about batch mode
3. Select a PDF file
4. View results showing:
   - ✅ "All questions present (1-X)" if valid
   - ⚠️ Missing question numbers if issues found
   - Special warning if Question 1 is missing

**Batch Validation Mode:**
1. Click "✅ Validate Questions"
2. Choose "Yes" for batch mode
3. Select multiple PDFs (Ctrl+Click or Shift+Click)
4. View comprehensive results window:
   - Summary header with counts (✅ Valid | ⚠️ Issues | ❌ Errors)
   - Individual results for each PDF
   - Status indicators and missing question details
5. Export options:
   - **📁 Export to Text File** - Detailed report for documentation
   - **📋 Copy to Clipboard** - Quick summary for sharing

**Status Indicators:**
- ✅ Valid - All questions present and sequential
- ⚠️ Issues - Missing questions detected (shows which numbers)
- ℹ️ Info - No questions found in PDF
- ❌ Error - Validation failed (corrupted file, etc.)

### Question Extraction

**Single PDF Mode:**
1. Click "✂️ Extract Questions Only"
2. Choose "No" when asked about batch mode
3. Select source PDF file
4. Choose output location (auto-suggests "_questions_only.pdf" suffix)
5. View results window showing:
   - Extraction statistics (pages before → after, reduction %)
   - Questions found (count and range)
   - Validation check (✅ all present or ⚠️ missing numbers)
   - Option to open output folder

**Batch Extraction Mode:**
1. Click "✂️ Extract Questions Only"
2. Choose "Yes" for batch mode
3. Select multiple PDFs to process
4. Choose output folder for all extracted files
5. View batch results with statistics for each file

**What Gets Extracted:**
- ✅ Pages with "Question 1", "Question 2", etc. (case-insensitive)
- ✅ Multiple questions on same page
- ❌ Cover pages, instructions, answer keys, blank pages

**Use Cases:**
- Clean up exam PDFs with extra pages
- Remove scanned blank pages  
- Standardize format across multiple exams
- Quality check before merging parts

## Technology Stack

- **Python 3.8+** - Core language
- **tkinter** - GUI framework (built into Python)
- **PyPDF2 3.0.1** - PDF manipulation and merging
- **PyMuPDF (fitz) 1.26.7** - Fast PDF text extraction, rendering, thumbnails, and optimization
- **Pillow (PIL) 10.1.0** - Image processing

## Project Structure

```
PDF-Editor/
├── main.py              # Main GUI application (1,584 lines)
├── pdf_manager.py       # PDF operations (load, merge, validate, extract)
├── pdf_viewer.py        # PDF rendering and thumbnail generation
├── requirements.txt     # Python dependencies
├── tests/               # Comprehensive test suite
│   ├── test_pdf_manager.py
│   ├── test_pdf_viewer.py
│   ├── test_question_validator.py
│   ├── test_content_preservation.py
│   ├── test_file_size.py
│   ├── test_gui_and_edgecases.py
│   └── ...
└── archive/             # Demo scripts and old documentation
```

## Troubleshooting

### Question Validation

**"No questions found"**
- PDF doesn't contain "Question {number}" pattern
- Check if questions use different wording (e.g., "Problem", "Exercise")
- Verify PDF is text-based (not scanned image without OCR)

**"Missing questions detected"**
- Some question numbers are not in sequence
- Verify all questions have numbers in source PDF
- Check for typos in question numbering

### Question Extraction

**"No pages with question numbers found"**
- Check pattern: must be "Question 1" with space (not "Question1" or "Q1")
- Verify PDF contains text (not scanned image)
- Questions must use exact pattern "Question {number}"

**"Output same size as input"**
- All pages contained question numbers (already clean)
- This is expected if no pages needed removal

**Performance Tips:**
- Large PDFs (100+ pages) may take 2-4 seconds
- UI won't freeze - runs in background thread
- Processing speed: ~0.1 sec per page for validation, ~0.3 sec per page for extraction

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

**Question Detection:**
- Uses regex pattern `\bquestion\s+(\d+)\b` (case-insensitive)
- Matches "Question 1", "QUESTION 2", "question 3", etc.
- Must have space between "Question" and number

**File Optimization:**
- Extraction uses PyMuPDF's `save()` with optimization flags:
  - `garbage=4` - Maximum garbage collection (removes unused objects)
  - `deflate=True` - Lossless compression of content streams
  - `clean=True` - Clean and optimize PDF structure
- Typical size reduction: 10-30% depending on source PDF

**Content Preservation:**
All visual content is preserved during extraction:
- Vector graphics (shapes, lines, diagrams)
- Embedded images (photos, scanned content)
- Mathematical notation and symbols
- Tables and formatting

**Architecture:**
- `PDFEditorApp` (main.py) - Main GUI application using tkinter
- `PDFManager` (pdf_manager.py) - Core PDF operations backend
- `PDFViewer` (pdf_viewer.py) - Thumbnail rendering using PyMuPDF
- Threading for background operations (validation, extraction)

## License

MIT
