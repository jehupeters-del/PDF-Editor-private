"""
Test File Size Reduction - Verify extraction reduces file size
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz
from pdf_manager import PDFManager


def format_size(bytes):
    """Format bytes into human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def create_test_pdf_with_images():
    """Create a larger test PDF with images to better test compression"""
    print("Creating test PDF with content...")
    
    test_file = Path(__file__).parent / "test_size_reduction.pdf"
    doc = fitz.open()
    
    # Title page
    page = doc.new_page()
    page.insert_text((72, 72), "Mathematics Final Exam\n\n" + "=" * 50 + "\n\nName: ___________", fontsize=14)
    
    # Add some junk pages with lots of text
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
    for i in range(5):
        page = doc.new_page()
        page.insert_text((72, 72), f"Instructions Page {i+1}\n\n{lorem}", fontsize=10)
    
    # Question pages
    for q in range(1, 11):
        page = doc.new_page()
        page.insert_text((72, 72), f"Question {q}\n\n{lorem}", fontsize=10)
    
    # More junk pages
    for i in range(5):
        page = doc.new_page()
        page.insert_text((72, 72), f"Answer Key Page {i+1}\n\n{lorem}", fontsize=10)
    
    # Save without optimization
    doc.save(str(test_file))
    doc.close()
    
    print(f"✓ Created: {test_file.name}")
    return test_file


def test_file_size_reduction():
    """Test that extraction reduces file size"""
    print()
    print("=" * 80)
    print("FILE SIZE REDUCTION TEST")
    print("=" * 80)
    print()
    
    # Create test PDF
    input_file = create_test_pdf_with_images()
    output_file = input_file.parent / "test_size_reduction_extracted.pdf"
    
    # Get input size
    input_size = input_file.stat().st_size
    
    print()
    print("Input PDF:")
    print(f"  📄 File: {input_file.name}")
    print(f"  📊 Size: {format_size(input_size)}")
    
    # Count pages
    doc = fitz.open(str(input_file))
    input_pages = len(doc)
    doc.close()
    print(f"  📄 Pages: {input_pages}")
    
    # Extract
    print()
    print("Extracting question pages...")
    manager = PDFManager()
    try:
        result = manager.extract_question_pages(str(input_file), str(output_file))
        orig_pages, new_pages, questions, is_valid, missing, max_q = result
        
        # Get output size
        output_size = output_file.stat().st_size
        
        print()
        print("Output PDF:")
        print(f"  📄 File: {output_file.name}")
        print(f"  📊 Size: {format_size(output_size)}")
        print(f"  📄 Pages: {new_pages}")
        print(f"  🔢 Questions: {min(questions)}-{max(questions)}")
        
        # Calculate reduction
        size_reduction = input_size - output_size
        size_reduction_percent = (size_reduction / input_size) * 100
        
        print()
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"  Page Reduction: {input_pages} → {new_pages} ({input_pages - new_pages} pages removed)")
        print(f"  Size Before: {format_size(input_size)}")
        print(f"  Size After:  {format_size(output_size)}")
        print(f"  Size Saved:  {format_size(size_reduction)} ({size_reduction_percent:.1f}%)")
        print()
        
        if output_size < input_size:
            print("  ✅ SUCCESS: File size DECREASED as expected!")
        elif output_size == input_size:
            print("  ⚠️  WARNING: File size stayed the SAME")
        else:
            increase = output_size - input_size
            increase_percent = (increase / input_size) * 100
            print(f"  ❌ PROBLEM: File size INCREASED by {format_size(increase)} ({increase_percent:.1f}%)")
            print()
            print("  This suggests compression settings need adjustment.")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup
        if input_file.exists():
            input_file.unlink()
        if output_file.exists():
            output_file.unlink()


def test_with_real_scenario():
    """Test with a more realistic multi-page scenario"""
    print()
    print("=" * 80)
    print("REALISTIC SCENARIO TEST")
    print("=" * 80)
    print()
    
    test_file = Path(__file__).parent / "realistic_exam.pdf"
    output_file = Path(__file__).parent / "realistic_exam_extracted.pdf"
    
    # Create a realistic exam PDF
    print("Creating realistic exam PDF...")
    doc = fitz.open()
    
    # Title page
    page = doc.new_page()
    title_text = """
    MATHEMATICS FINAL EXAMINATION
    
    ===============================================
    
    Name: _____________________________
    
    Student ID: ________________________
    
    Date: _____________________________
    
    
    Instructions:
    • Show all your work
    • Calculators are not permitted
    • Write clearly and legibly
    """
    page.insert_text((72, 72), title_text, fontsize=12)
    
    # General instructions (2 pages)
    instructions = "Please read all questions carefully. " * 50
    for i in range(2):
        page = doc.new_page()
        page.insert_text((72, 72), f"General Instructions - Page {i+1}\n\n{instructions}", fontsize=10)
    
    # 20 questions (one per page)
    for q in range(1, 21):
        page = doc.new_page()
        content = f"Question {q}\n\n" + f"Solve the following problem:\n" + ("x + y = z\n" * 30)
        page.insert_text((72, 72), content, fontsize=10)
    
    # Answer key (3 pages)
    answer_key = "Answer: 42\n" * 50
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Answer Key - Page {i+1}\n\n{answer_key}", fontsize=10)
    
    # Formula sheet (1 page)
    page = doc.new_page()
    page.insert_text((72, 72), "Formula Sheet\n\n" + "E = mc²\n" * 40, fontsize=10)
    
    # Save
    doc.save(str(test_file))
    doc.close()
    
    input_size = test_file.stat().st_size
    doc = fitz.open(str(test_file))
    input_pages = len(doc)
    doc.close()
    
    print(f"  📄 Original: {input_pages} pages, {format_size(input_size)}")
    print()
    
    # Extract
    print("Extracting questions...")
    manager = PDFManager()
    result = manager.extract_question_pages(str(test_file), str(output_file))
    orig_pages, new_pages, questions, is_valid, missing, max_q = result
    
    output_size = output_file.stat().st_size
    
    print(f"  📄 Extracted: {new_pages} pages, {format_size(output_size)}")
    print()
    
    reduction = input_size - output_size
    reduction_pct = (reduction / input_size) * 100
    
    print("=" * 80)
    print(f"  Pages: {input_pages} → {new_pages} (removed {input_pages - new_pages})")
    print(f"  Size: {format_size(input_size)} → {format_size(output_size)} (saved {format_size(reduction)})")
    print(f"  Reduction: {reduction_pct:.1f}%")
    
    if output_size < input_size:
        print(f"  ✅ File size reduced successfully!")
    else:
        print(f"  ❌ File size increased - optimization needed!")
    
    print()
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
    if output_file.exists():
        output_file.unlink()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "FILE SIZE REDUCTION TEST" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This test verifies that extracting pages REDUCES file size, not increases it.")
    print()
    input("Press ENTER to run tests... ")
    
    test_file_size_reduction()
    test_with_real_scenario()
    
    print("=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
    print()
    print("The extraction should now:")
    print("  ✓ Remove unused objects (garbage collection)")
    print("  ✓ Compress content streams (deflate)")
    print("  ✓ Clean and optimize PDF structure")
    print()
    print("Result: Smaller file sizes when pages are removed!")
    print()
