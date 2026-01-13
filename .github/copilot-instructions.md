# PDF Editor - AI Agent Instructions

## Project Overview
A Python desktop application using tkinter for loading, viewing, manipulating, and merging multiple PDF documents. Completely offline - no network dependencies. Users can load PDFs, view page thumbnails, remove pages/PDFs, and merge everything into a single output file.

## Architecture

### Core Components
- **main.py (PDFEditorApp)**: Main tkinter GUI orchestrator managing UI state and user interactions
- **pdf_manager.py (PDFManager)**: Business logic for PDF operations (loading, page tracking, merging)
- **pdf_viewer.py (PDFViewer)**: PDF rendering utilities for thumbnail generation

### Data Flow
1. User selects PDFs → `PDFManager.add_pdf()` creates PdfReader, extracts metadata
2. Pages stored in flat `all_pages` list (enables cross-PDF operations)
3. Selecting PDF in listbox filters display to show only that PDF's pages
4. Page removals update `all_pages` directly (single source of truth)
5. Merge reads `all_pages` order, uses PyPDF2.PdfWriter to create output

### Key Architectural Decisions
- **Flat page list**: `all_pages` contains all pages across all PDFs for simplified reordering/filtering
- **Threading for I/O**: PDF loading and merging use background threads to prevent UI freezing
- **PdfReader caching**: Each PDF keeps its PdfReader in memory (avoids re-parsing on merge)
- **Minimal thumbnail generation**: Currently simplified (pdf2image integration partial) to avoid performance issues

## Development Workflow

### Setup
```bash
pip install -r requirements.txt
```

**Important**: Install Poppler for pdf2image support:
- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/, add `bin` to PATH
- Linux: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`

### Running
```bash
python main.py
```

### Testing
Manual testing workflow (no automated tests):
1. Load multiple PDFs with varying page counts
2. Verify PDF list updates and selection works
3. Test page removal for each PDF
4. Test PDF removal
5. Test merge operation - validate output opens correctly

## Project Conventions

### Code Organization
```
├── main.py           # PDFEditorApp class (tkinter UI)
├── pdf_manager.py    # PDFManager class (PDF business logic)
├── pdf_viewer.py     # PDFViewer utilities (rendering)
└── requirements.txt  # Dependencies
```

### Class Responsibilities
- **PDFEditorApp**: UI setup, event handlers, threading coordination
- **PDFManager**: Data model (pdfs dict, all_pages list), PDF I/O operations
- **PDFViewer**: Pure functions for thumbnail generation (stateless)

### Naming Conventions
- Classes: PascalCase (`PDFManager`, `PDFEditorApp`)
- Methods: snake_case (`add_pdf`, `remove_page`)
- Private methods: Leading underscore (`_get_thumbnail`)
- Tkinter callbacks: `on_*` prefix (`on_pdf_selected`)

### Threading Pattern
Long-running operations use background threads with `root.after(0, callback)` for UI updates:
```python
def load_worker():
    result = expensive_operation()
    self.root.after(0, lambda: update_ui(result))
    
thread = threading.Thread(target=load_worker, daemon=True)
thread.start()
```

## Key Technologies
- **Python 3.8+**: Core language
- **tkinter**: GUI framework (stdlib, no installation needed)
- **PyPDF2**: PDF parsing and merging (reader/writer operations)
- **Pillow (PIL)**: Image processing for thumbnails
- **pdf2image**: Converts PDF pages to PIL Images (requires Poppler)

## Important Files
- [main.py](main.py): tkinter UI patterns, threading for async operations
- [pdf_manager.py](pdf_manager.py): PDF data model, PyPDF2 PdfReader/PdfWriter usage
- [pdf_viewer.py](pdf_viewer.py): Thumbnail generation (currently simplified)

## Integration Points
- **Poppler**: External binary dependency for pdf2image (must be in PATH or project dir)
- **File I/O**: All PDF operations work with file paths (stored in `PDFManager.pdfs`)
- **tkinter event loop**: All UI updates must use `root.after()` from background threads

## Common Tasks

### Adding New PDF Operations
1. Add method to `PDFManager` (e.g., `rotate_page()`, `extract_text()`)
2. Create UI button/handler in `PDFEditorApp`
3. Call manager method in background thread if I/O-heavy
4. Update UI via `root.after(0, callback)`

### Improving Thumbnail Display
Current implementation has placeholders. To fully enable:
1. Pass `pdf_path` to `PDFViewer.create_page_widget()`
2. Call `generate_thumbnail_from_path()` in background thread
3. Cache result in `_thumbnail_cache` dict
4. Update widget with `img_label.configure(image=photo)`

### Modifying UI Layout
- **Sidebar width**: `sidebar = ttk.Frame(parent, width=250)` in `setup_sidebar()`
- **Grid columns**: `cols = 5` in `display_pages()` method
- **Thumbnail size**: `width=150` parameter in `generate_thumbnail_from_path()`

### Handling Poppler Issues (Work Computers)
If Poppler installation is blocked:
- Option 1: Bundle Poppler binaries in project, set path: `poppler_path = "./poppler/bin"`
- Option 2: Skip thumbnails entirely (use text placeholders)
- Option 3: Use PyMuPDF (fitz) instead of pdf2image (no Poppler needed)
