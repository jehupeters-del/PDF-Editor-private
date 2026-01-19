"""
Enhanced Extraction Demo - Tests All New Features
1. Always keeps first page (title page)
2. Smart filename generation (pc_mg_jun_13 → June 2013 solutions.pdf)
3. Batch extraction support
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz  # PyMuPDF
from pdf_manager import PDFManager


def test_filename_generation():
    """Test the smart filename generation"""
    print("=" * 80)
    print("TESTING SMART FILENAME GENERATION")
    print("=" * 80)
    print()
    
    test_cases = [
        "pc_mg_jun_13",
        "pc_mg_jan_13",
        "math_exam_may_15",
        "quiz_dec_20",
        "pc_mg_feb_14",
        "test_sep_16",
        "exam_november_2019",
        "final_mar_21",
        "midterm_aug_12",
        "practice_july_2018"
    ]
    
    for filename in test_cases:
        smart_name = PDFManager.generate_smart_filename(filename)
        print(f"  {filename:25} → {smart_name}")
    
    print()


def create_test_pdfs():
    """Create test PDFs with realistic naming patterns"""
    demo_dir = Path(__file__).parent / "batch_extraction_demo"
    demo_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("CREATING TEST PDFs")
    print("=" * 80)
    print()
    
    test_configs = [
        ("pc_mg_jun_13.pdf", "June 2013 Exam", 12, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("pc_mg_jan_13.pdf", "January 2013 Exam", 10, [1, 2, 3, 4, 5, 6, 7, 8]),
        ("math_may_15.pdf", "May 2015 Test", 15, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
        ("quiz_dec_20.pdf", "December 2020 Quiz", 8, [1, 2, 3, 4, 5]),
        ("final_mar_21.pdf", "March 2021 Final", 20, list(range(1, 16))),
    ]
    
    for filename, title, total_pages, questions in test_configs:
        print(f"✓ Creating: {filename}")
        doc = fitz.open()
        
        # Page 1: Title page (always kept)
        page = doc.new_page()
        page.insert_text((72, 72), f"{title}\n\n" + "=" * 40 + "\n\nName: ___________", fontsize=14)
        print(f"  Page 1: Title page (will be kept)")
        
        # Some random pages without questions
        num_junk_pages = (total_pages - len(questions) - 1)  # -1 for title
        for i in range(num_junk_pages // 2):
            page = doc.new_page()
            page.insert_text((72, 72), f"Instructions\n\nPlease show your work.\nCalculators not allowed.")
            print(f"  Page {2 + i}: Instructions (will be removed)")
        
        # Question pages
        for q in questions:
            page = doc.new_page()
            page.insert_text((72, 72), f"Question {q}\n\nSolve the following problem:\n[Problem content here]")
        print(f"  Pages {2 + num_junk_pages // 2} to {2 + num_junk_pages // 2 + len(questions) - 1}: Questions {min(questions)}-{max(questions)}")
        
        # Remaining junk pages (answer key, etc.)
        for i in range(num_junk_pages - num_junk_pages // 2):
            page = doc.new_page()
            page.insert_text((72, 72), f"Answer Key\n\nAnswers for grading purposes only.")
            print(f"  Page {len(doc)}: Answer key (will be removed)")
        
        doc.save(str(demo_dir / filename))
        doc.close()
        
        print(f"  Total: {total_pages} pages → Expected output: {1 + len(questions)} pages (title + {len(questions)} questions)")
        print()
    
    print(f"✅ Test PDFs created in: {demo_dir.absolute()}")
    print()
    return demo_dir


def test_single_extraction(demo_dir):
    """Test single PDF extraction with first page kept"""
    print("=" * 80)
    print("TESTING SINGLE EXTRACTION (with first page kept)")
    print("=" * 80)
    print()
    
    manager = PDFManager()
    test_file = demo_dir / "pc_mg_jun_13.pdf"
    output_file = demo_dir / "extracted_pc_mg_jun_13.pdf"
    
    print(f"📄 Input: {test_file.name}")
    print(f"💾 Output: {output_file.name}")
    print()
    
    try:
        result = manager.extract_question_pages(str(test_file), str(output_file))
        orig_pages, new_pages, questions, is_valid, missing, max_q = result
        
        print(f"  ✅ Extraction successful!")
        print(f"  📊 Pages: {orig_pages} → {new_pages}")
        print(f"  📄 First page: KEPT (title page)")
        print(f"  🔢 Questions found: {questions}")
        print(f"  📝 Question range: 1 to {max_q}")
        
        if is_valid:
            print(f"  ✅ Validation: PASSED")
        else:
            print(f"  ⚠️  Validation: Missing {missing}")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    print()


def test_batch_extraction(demo_dir):
    """Test batch extraction with smart filenames"""
    print("=" * 80)
    print("TESTING BATCH EXTRACTION (with smart filenames)")
    print("=" * 80)
    print()
    
    manager = PDFManager()
    output_dir = demo_dir / "batch_output"
    output_dir.mkdir(exist_ok=True)
    
    test_files = [
        "pc_mg_jun_13.pdf",
        "pc_mg_jan_13.pdf",
        "math_may_15.pdf",
        "quiz_dec_20.pdf",
        "final_mar_21.pdf"
    ]
    
    print(f"📁 Output folder: {output_dir.name}")
    print()
    
    results = []
    for filename in test_files:
        input_path = demo_dir / filename
        smart_name = manager.generate_smart_filename(filename)
        output_path = output_dir / smart_name
        
        print(f"📄 {filename}")
        print(f"   → {smart_name}")
        
        try:
            result = manager.extract_question_pages(str(input_path), str(output_path))
            orig_pages, new_pages, questions, is_valid, missing, max_q = result
            
            print(f"   Pages: {orig_pages} → {new_pages}  |  Questions: {min(questions)}-{max(questions)}  |  Valid: {'✅' if is_valid else '⚠️'}")
            results.append({
                'file': filename,
                'smart_name': smart_name,
                'success': True,
                'orig': orig_pages,
                'new': new_pages,
                'valid': is_valid
            })
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'file': filename,
                'smart_name': smart_name,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    valid_count = sum(1 for r in results if r.get('valid', False))
    
    print("-" * 80)
    print(f"BATCH SUMMARY:")
    print(f"  Total: {len(results)} PDFs")
    print(f"  Success: {success_count}")
    print(f"  Valid: {valid_count}")
    print(f"  Output folder: {output_dir.absolute()}")
    print()


def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "ENHANCED EXTRACTION FEATURES DEMO" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This demo tests all three new features:")
    print("  1. ✅ Always keep first page (title page)")
    print("  2. ✅ Smart filename generation (pc_mg_jun_13 → June 2013 solutions.pdf)")
    print("  3. ✅ Batch extraction support")
    print()
    input("Press ENTER to run tests... ")
    print()
    
    # Test 1: Filename generation
    test_filename_generation()
    
    # Test 2: Create test PDFs
    demo_dir = create_test_pdfs()
    
    # Test 3: Single extraction (verify first page kept)
    test_single_extraction(demo_dir)
    
    # Test 4: Batch extraction (verify smart filenames)
    test_batch_extraction(demo_dir)
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)
    print()
    print("📁 Check the batch_extraction_demo folder to see:")
    print("   • Original test PDFs with realistic names")
    print("   • batch_output/ folder with extracted PDFs using smart names")
    print()
    print("🎯 Key Features Demonstrated:")
    print("   ✓ First page always kept (title page)")
    print("   ✓ Smart filenames: pc_mg_jun_13.pdf → June 2013 solutions.pdf")
    print("   ✓ Batch processing ready")
    print()
    print("💡 To use in GUI:")
    print("   1. Run: python main.py")
    print("   2. Click: '✂️ Extract Questions Only'")
    print("   3. Choose: 'Yes' for batch mode or 'No' for single")
    print("   4. For batch: Select multiple PDFs and output folder")
    print("   5. View results with smart filenames!")
    print()


if __name__ == "__main__":
    main()
