"""
Question Page Extraction Demo
Tests the automated extraction of pages containing question numbers
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz  # PyMuPDF
from pdf_manager import PDFManager


def create_test_pdfs():
    """Create test PDFs with various scenarios"""
    demo_dir = Path(__file__).parent / "extraction_demo_pdfs"
    demo_dir.mkdir(exist_ok=True)
    
    print("Creating test PDFs for extraction demo...\n")
    
    # Test 1: Exam with extra pages (cover, instructions, answer key)
    print("  ✓ Creating: messy_exam.pdf")
    print("    - Cover page (no question)")
    print("    - Instructions page (no question)")
    print("    - Questions 1-10 (each on own page)")
    print("    - Answer key page (no question)")
    print("    - Blank page (no question)")
    
    doc1 = fitz.open()
    
    # Cover page
    page = doc1.new_page()
    page.insert_text((72, 72), "FINAL EXAM\n\nMath 101\nFall 2025", fontsize=18)
    
    # Instructions page
    page = doc1.new_page()
    page.insert_text((72, 72), "INSTRUCTIONS\n\nPlease answer all questions.\nShow your work.\nNo calculators allowed.")
    
    # Question pages
    for i in range(1, 11):
        page = doc1.new_page()
        page.insert_text((72, 72), f"Question {i}\n\nSolve the following problem:\n[Problem content here]")
    
    # Answer key
    page = doc1.new_page()
    page.insert_text((72, 72), "ANSWER KEY\n\n1. A\n2. B\n3. C\n4. D\n5. A\n6. B\n7. C\n8. D\n9. A\n10. B")
    
    # Blank page
    page = doc1.new_page()
    page.insert_text((72, 72), "[This page intentionally left blank]")
    
    doc1.save(str(demo_dir / "messy_exam.pdf"))
    doc1.close()
    print(f"    → Total: 14 pages (should extract 10)\n")
    
    # Test 2: Multiple questions per page with junk pages
    print("  ✓ Creating: multi_question_pages.pdf")
    print("    - Title page (no question)")
    print("    - Page with Q1 and Q2")
    print("    - Page with Q3 and Q4")
    print("    - Random notes page (no question)")
    print("    - Page with Q5")
    
    doc2 = fitz.open()
    
    # Title
    page = doc2.new_page()
    page.insert_text((72, 72), "Quiz 3\n\nName: ___________")
    
    # Q1 and Q2 on same page
    page = doc2.new_page()
    page.insert_text((72, 72), "Question 1\nWhat is 2+2?\n\nQuestion 2\nWhat is 3+3?")
    
    # Q3 and Q4 on same page
    page = doc2.new_page()
    page.insert_text((72, 72), "Question 3\nWhat is 4+4?\n\nQuestion 4\nWhat is 5+5?")
    
    # Notes page
    page = doc2.new_page()
    page.insert_text((72, 72), "Notes:\n\nRemember to review chapters 3-5.\nTest date: Next Friday.")
    
    # Q5
    page = doc2.new_page()
    page.insert_text((72, 72), "Question 5\nWhat is 6+6?")
    
    doc2.save(str(demo_dir / "multi_question_pages.pdf"))
    doc2.close()
    print(f"    → Total: 5 pages (should extract 3)\n")
    
    # Test 3: All question pages (no junk)
    print("  ✓ Creating: clean_exam.pdf")
    print("    - Questions 1-5 (each on own page, no extra pages)")
    
    doc3 = fitz.open()
    for i in range(1, 6):
        page = doc3.new_page()
        page.insert_text((72, 72), f"Question {i}\n\nSolve: [Problem {i}]")
    
    doc3.save(str(demo_dir / "clean_exam.pdf"))
    doc3.close()
    print(f"    → Total: 5 pages (should extract 5)\n")
    
    # Test 4: Exam with missing question in sequence
    print("  ✓ Creating: incomplete_exam.pdf")
    print("    - Cover page")
    print("    - Questions 1, 2, 3, 5, 6 (missing Q4)")
    print("    - Notes page")
    
    doc4 = fitz.open()
    
    # Cover
    page = doc4.new_page()
    page.insert_text((72, 72), "Midterm Exam")
    
    # Questions (skip 4)
    for i in [1, 2, 3, 5, 6]:
        page = doc4.new_page()
        page.insert_text((72, 72), f"Question {i}\n\nAnswer the following:")
    
    # Notes
    page = doc4.new_page()
    page.insert_text((72, 72), "Additional notes")
    
    doc4.save(str(demo_dir / "incomplete_exam.pdf"))
    doc4.close()
    print(f"    → Total: 7 pages (should extract 5, with validation warning)\n")
    
    # Test 5: No question numbers at all
    print("  ✓ Creating: no_questions.pdf")
    print("    - Generic document with no question numbers")
    
    doc5 = fitz.open()
    page = doc5.new_page()
    page.insert_text((72, 72), "This is a regular document.\n\nIt has multiple pages but no questions.")
    page = doc5.new_page()
    page.insert_text((72, 72), "Page 2 of the document.\n\nStill no questions here.")
    
    doc5.save(str(demo_dir / "no_questions.pdf"))
    doc5.close()
    print(f"    → Total: 2 pages (should fail - no questions)\n")
    
    print(f"✅ Test PDFs created in: {demo_dir.absolute()}\n")
    return demo_dir


def run_extraction_tests(demo_dir):
    """Run extraction tests and display results"""
    print("=" * 80)
    print("RUNNING EXTRACTION TESTS")
    print("=" * 80)
    print()
    
    manager = PDFManager()
    test_files = [
        "messy_exam.pdf",
        "multi_question_pages.pdf",
        "clean_exam.pdf",
        "incomplete_exam.pdf",
        "no_questions.pdf"
    ]
    
    for filename in test_files:
        input_path = demo_dir / filename
        output_path = demo_dir / f"extracted_{filename}"
        
        print(f"📄 Testing: {filename}")
        print("-" * 80)
        
        try:
            result = manager.extract_question_pages(str(input_path), str(output_path))
            orig_pages, new_pages, questions, is_valid, missing, max_q = result
            
            print(f"  ✓ Extraction successful!")
            print(f"  📊 Pages: {orig_pages} → {new_pages} (removed {orig_pages - new_pages})")
            print(f"  🔢 Questions found: {questions}")
            print(f"  📝 Question range: 1 to {max_q}")
            
            if is_valid:
                print(f"  ✅ Validation: PASSED - All questions present")
            else:
                print(f"  ⚠️  Validation: FAILED - Missing questions: {missing}")
            
            print(f"  💾 Saved to: {output_path.name}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    print("=" * 80)
    print()


def print_instructions():
    """Print usage instructions"""
    print()
    print("=" * 80)
    print("QUESTION PAGE EXTRACTION - DEMO & TEST")
    print("=" * 80)
    print()
    print("This demo creates test PDFs and runs automated extraction tests.")
    print()
    print("WHAT IT DOES:")
    print("  1. Creates 5 test PDFs with various scenarios")
    print("  2. Runs extraction on each PDF")
    print("  3. Shows statistics and validation results")
    print()
    print("TEST SCENARIOS:")
    print("  • Exam with cover page, instructions, and answer key")
    print("  • Multiple questions on same page")
    print("  • Clean exam (questions only)")
    print("  • Incomplete exam (missing question in sequence)")
    print("  • Document with no questions (should fail)")
    print()
    print("EXTRACTION PROCESS:")
    print("  → Scans each page for 'Question {number}' text")
    print("  → Extracts only pages with question numbers")
    print("  → Removes cover pages, instructions, answer keys, etc.")
    print("  → Validates result to ensure no questions lost")
    print()
    print("=" * 80)
    print()
    input("Press ENTER to run the tests... ")
    print()


if __name__ == "__main__":
    print_instructions()
    
    # Create test PDFs
    demo_dir = create_test_pdfs()
    
    # Run extraction tests
    run_extraction_tests(demo_dir)
    
    print("✅ Demo complete!")
    print()
    print("📁 Check the extraction_demo_pdfs folder to see:")
    print("   • Original test PDFs")
    print("   • Extracted PDFs (extracted_*.pdf)")
    print()
    print("💡 To use in GUI:")
    print("   1. Run: python main.py")
    print("   2. Click: '✂️ Extract Questions Only'")
    print("   3. Select a PDF with mixed content")
    print("   4. Choose output location")
    print("   5. View results with statistics and validation")
    print()
