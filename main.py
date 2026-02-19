"""
PDF Editor - Command-line tool for PDF manipulation

Usage:
    python main.py merge file1.pdf file2.pdf -o merged.pdf
    python main.py extract input.pdf -o output.pdf
    python main.py validate input.pdf
    python main.py batch-extract *.pdf -o output_dir
    python main.py batch-validate *.pdf
    python main.py rename input.pdf
    python main.py thumbnail input.pdf -p 0 -o thumb.png
    python main.py info input.pdf
"""

import argparse
import glob
import sys
from pathlib import Path

from pdf_manager import PDFManager
from pdf_viewer import PDFViewer


def cmd_merge(args):
    """Merge multiple PDFs into one."""
    manager = PDFManager()

    for pdf_path in args.files:
        try:
            pdf_id = manager.add_pdf(pdf_path)
            info = manager.get_pdf_info(pdf_id)
            print(f"  Added: {info['name']} ({info['page_count']} pages)")
        except FileNotFoundError:
            print(f"  ERROR: File not found: {pdf_path}", file=sys.stderr)
            return 1

    total = manager.get_total_page_count()
    if total == 0:
        print("No pages to merge.")
        return 1

    output = args.output or "merged.pdf"
    manager.merge_all(output)
    print(f"\nMerged {total} pages into: {output}")
    return 0


def cmd_extract(args):
    """Extract question pages from a single PDF."""
    manager = PDFManager()
    input_path = args.file

    if not Path(input_path).exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        return 1

    if args.output:
        output_path = args.output
    else:
        smart_name = PDFManager.generate_smart_filename(Path(input_path).name)
        output_path = str(Path(input_path).parent / smart_name)

    try:
        orig, extracted, questions, valid, missing, max_q = manager.extract_question_pages(
            input_path, output_path
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"  Input:     {input_path}")
    print(f"  Output:    {output_path}")
    print(f"  Pages:     {orig} -> {extracted} (removed {orig - extracted})")
    print(f"  Questions: {len(questions)} found (1-{max_q})")

    if valid:
        print(f"  Validation: PASS - all questions 1-{max_q} present")
    else:
        print(f"  Validation: FAIL - missing questions: {missing}")

    return 0


def cmd_validate(args):
    """Validate question continuity in a single PDF."""
    manager = PDFManager()
    input_path = args.file

    if not Path(input_path).exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        is_valid, missing, max_q = manager.validate_question_continuity(input_path)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"  File: {input_path}")
    if max_q == 0:
        print("  No questions found in this PDF.")
    elif is_valid:
        print(f"  PASS - all questions 1-{max_q} present")
    else:
        print(f"  FAIL - missing questions: {missing}")
        print(f"  Expected 1-{max_q}, found {max_q - len(missing)} of {max_q}")

    return 0


def cmd_batch_extract(args):
    """Extract question pages from multiple PDFs."""
    files = _expand_globs(args.files)
    if not files:
        print("No matching PDF files found.", file=sys.stderr)
        return 1

    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    manager = PDFManager()
    errors = 0

    for pdf_path in files:
        smart_name = PDFManager.generate_smart_filename(Path(pdf_path).name)
        if output_dir:
            out_path = str(output_dir / smart_name)
        else:
            out_path = str(Path(pdf_path).parent / smart_name)

        try:
            orig, extracted, questions, valid, missing, max_q = manager.extract_question_pages(
                pdf_path, out_path
            )
            status = "PASS" if valid else f"FAIL (missing: {missing})"
            print(f"  {Path(pdf_path).name}: {orig} -> {extracted} pages, {status}")
        except Exception as e:
            print(f"  {Path(pdf_path).name}: ERROR - {e}", file=sys.stderr)
            errors += 1

    print(f"\nBatch complete: {len(files)} files processed, {errors} errors")
    return 1 if errors > 0 else 0


def cmd_batch_validate(args):
    """Validate question continuity in multiple PDFs."""
    files = _expand_globs(args.files)
    if not files:
        print("No matching PDF files found.", file=sys.stderr)
        return 1

    manager = PDFManager()
    pass_count = 0
    fail_count = 0

    for pdf_path in files:
        try:
            is_valid, missing, max_q = manager.validate_question_continuity(pdf_path)
            if max_q == 0:
                print(f"  {Path(pdf_path).name}: no questions found")
            elif is_valid:
                print(f"  {Path(pdf_path).name}: PASS (1-{max_q})")
                pass_count += 1
            else:
                print(f"  {Path(pdf_path).name}: FAIL - missing {missing}")
                fail_count += 1
        except Exception as e:
            print(f"  {Path(pdf_path).name}: ERROR - {e}", file=sys.stderr)
            fail_count += 1

    print(f"\nBatch complete: {pass_count} passed, {fail_count} failed")
    return 1 if fail_count > 0 else 0


def cmd_rename(args):
    """Show smart filename suggestion for a PDF."""
    input_path = args.file
    name = Path(input_path).name
    smart_name = PDFManager.generate_smart_filename(name)
    print(f"  Original:  {name}")
    print(f"  Suggested: {smart_name}")

    if args.apply:
        new_path = Path(input_path).parent / smart_name
        if new_path.exists():
            print(f"  ERROR: Target already exists: {new_path}", file=sys.stderr)
            return 1
        Path(input_path).rename(new_path)
        print(f"  Renamed to: {new_path}")

    return 0


def cmd_thumbnail(args):
    """Generate a thumbnail PNG from a PDF page."""
    input_path = args.file

    if not Path(input_path).exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        return 1

    output = args.output or "thumbnail.png"
    page_index = args.page or 0
    width = args.width or 180

    success = PDFViewer.generate_thumbnail(input_path, page_index, output, width)
    if success:
        print(f"  Thumbnail saved: {output} (page {page_index}, width {width}px)")
        return 0
    else:
        print(f"  ERROR: Failed to generate thumbnail", file=sys.stderr)
        return 1


def cmd_info(args):
    """Show information about a PDF file."""
    manager = PDFManager()
    input_path = args.file

    if not Path(input_path).exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        pdf_id = manager.add_pdf(input_path)
        info = manager.get_pdf_info(pdf_id)
        print(f"  File:  {info['name']}")
        print(f"  Path:  {info['path']}")
        print(f"  Pages: {info['page_count']}")

        # Also check for questions
        is_valid, missing, max_q = manager.validate_question_continuity(input_path)
        if max_q > 0:
            print(f"  Questions: 1-{max_q} ({max_q} total)")
            if not is_valid:
                print(f"  Missing: {missing}")
        else:
            print(f"  Questions: none detected")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


def _expand_globs(patterns):
    """Expand glob patterns into file paths."""
    files = []
    for pattern in patterns:
        expanded = glob.glob(pattern)
        if expanded:
            files.extend(expanded)
        elif Path(pattern).exists():
            files.append(pattern)
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(
        prog="pdf-editor",
        description="PDF Editor - Command-line tool for PDF manipulation",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # merge
    p_merge = subparsers.add_parser("merge", help="Merge multiple PDFs into one")
    p_merge.add_argument("files", nargs="+", help="PDF files to merge")
    p_merge.add_argument("-o", "--output", help="Output file (default: merged.pdf)")
    p_merge.set_defaults(func=cmd_merge)

    # extract
    p_extract = subparsers.add_parser("extract", help="Extract question pages from a PDF")
    p_extract.add_argument("file", help="Input PDF file")
    p_extract.add_argument("-o", "--output", help="Output file (default: smart name)")
    p_extract.set_defaults(func=cmd_extract)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate question continuity")
    p_validate.add_argument("file", help="Input PDF file")
    p_validate.set_defaults(func=cmd_validate)

    # batch-extract
    p_bextract = subparsers.add_parser("batch-extract", help="Extract from multiple PDFs")
    p_bextract.add_argument("files", nargs="+", help="PDF files (supports glob patterns)")
    p_bextract.add_argument("-o", "--output", help="Output directory")
    p_bextract.set_defaults(func=cmd_batch_extract)

    # batch-validate
    p_bvalidate = subparsers.add_parser("batch-validate", help="Validate multiple PDFs")
    p_bvalidate.add_argument("files", nargs="+", help="PDF files (supports glob patterns)")
    p_bvalidate.set_defaults(func=cmd_batch_validate)

    # rename
    p_rename = subparsers.add_parser("rename", help="Suggest smart filename for a PDF")
    p_rename.add_argument("file", help="Input PDF file")
    p_rename.add_argument("--apply", action="store_true", help="Actually rename the file")
    p_rename.set_defaults(func=cmd_rename)

    # thumbnail
    p_thumb = subparsers.add_parser("thumbnail", help="Generate a thumbnail PNG")
    p_thumb.add_argument("file", help="Input PDF file")
    p_thumb.add_argument("-o", "--output", help="Output PNG (default: thumbnail.png)")
    p_thumb.add_argument("-p", "--page", type=int, default=0, help="Page index (default: 0)")
    p_thumb.add_argument("-w", "--width", type=int, default=180, help="Width in pixels (default: 180)")
    p_thumb.set_defaults(func=cmd_thumbnail)

    # info
    p_info = subparsers.add_parser("info", help="Show PDF information")
    p_info.add_argument("file", help="Input PDF file")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
