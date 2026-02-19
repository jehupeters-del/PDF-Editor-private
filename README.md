# PDF Editor

A command-line tool for PDF manipulation — merge, extract question pages, validate question continuity, generate thumbnails, and smart-rename files.

## Usage

```bash
# Show help
python main.py --help

# Merge multiple PDFs into one
python main.py merge file1.pdf file2.pdf file3.pdf -o merged.pdf

# Extract only question pages from a PDF (auto-generates smart filename)
python main.py extract exam.pdf
python main.py extract exam.pdf -o clean_exam.pdf

# Validate question continuity (checks for missing questions 1..N)
python main.py validate exam.pdf

# Batch extract from multiple PDFs
python main.py batch-extract *.pdf -o output_dir/

# Batch validate multiple PDFs
python main.py batch-validate *.pdf

# Show smart filename suggestion
python main.py rename pc_mg_jun_13.pdf
python main.py rename pc_mg_jun_13.pdf --apply   # actually rename

# Generate a thumbnail PNG from a PDF page
python main.py thumbnail exam.pdf -p 0 -o thumb.png -w 300

# Show PDF info (page count, question detection)
python main.py info exam.pdf
```

## Features

| Command | Description |
|---------|-------------|
| `merge` | Combine multiple PDFs into a single file |
| `extract` | Remove non-question pages, keep title page + question pages |
| `validate` | Check that questions 1 through N are all present |
| `batch-extract` | Extract from multiple files at once |
| `batch-validate` | Validate multiple files at once |
| `rename` | Suggest smart filenames (e.g., `pc_mg_jun_13` → `Jun 2013 solutions.pdf`) |
| `thumbnail` | Render a PDF page to PNG |
| `info` | Show page count and question detection results |

## Dependencies

- **PyPDF2** — PDF reading, writing, and merging
- **PyMuPDF (fitz)** — Text extraction, page rendering, and PDF optimization

## Project Structure

```
PDF-Editor/
├── main.py           # CLI entry point (argparse)
├── pdf_manager.py    # Core PDF logic (merge, extract, validate, rename)
├── pdf_viewer.py     # Thumbnail generation utility
├── create_test_pdfs.py  # Test PDF generator
├── requirements.txt
└── tests/
    ├── test_pdf_manager.py        # Core add/remove tests
    ├── test_merge_and_errors.py   # Merge and error handling tests
    ├── test_question_validator.py # Validation tests (perfect, missing, gaps, etc.)
    ├── test_content_preservation.py
    ├── test_file_size.py
    └── test_realistic_content.py
```

## Running Tests

```bash
cd PDF-Editor
python -m pytest tests/ -v
```
