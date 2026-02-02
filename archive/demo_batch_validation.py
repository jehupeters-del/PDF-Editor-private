"""
Batch Validation Demo - Test Multiple PDFs at Once

This script creates various test PDFs and demonstrates the batch validation feature.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz  # PyMuPDF
from main import main as run_app


def create_batch_demo_pdfs():
    """Create a variety of PDFs for batch testing"""
    demo_dir = Path(__file__).parent / "batch_demo_pdfs"
    demo_dir.mkdir(exist_ok=True)
    
    print("Creating batch demo PDFs for testing...")
    print()
    
    # 1. Perfect Exam A (Q1-25)
    print("  ✓ exam_a_perfect.pdf (Questions 1-25, all present)")
    doc1 = fitz.open()
    for i in range(1, 26):
        page = doc1.new_page()
        page.insert_text((72, 72), f"QUESTION {i}\\n\\nContent for question {i}")
    doc1.save(str(demo_dir / "exam_a_perfect.pdf"))
    doc1.close()
    
    # 2. Perfect Exam B (Q1-30)
    print("  ✓ exam_b_perfect.pdf (Questions 1-30, all present)")
    doc2 = fitz.open()
    for i in range(1, 31):
        page = doc2.new_page()
        page.insert_text((72, 72), f"question {i}\\n\\nContent for question {i}")
    doc2.save(str(demo_dir / "exam_b_perfect.pdf"))
    doc2.close()
    
    # 3. Midterm with gaps (missing Q5, Q12, Q18)
    print("  ✓ midterm_incomplete.pdf (Missing Q5, Q12, Q18)")
    doc3 = fitz.open()
    questions = [i for i in range(1, 21) if i not in [5, 12, 18]]
    for q in questions:
        page = doc3.new_page()
        page.insert_text((72, 72), f"Question {q}\\n\\nContent for question {q}")
    doc3.save(str(demo_dir / "midterm_incomplete.pdf"))
    doc3.close()
    
    # 4. Final with missing Q1
    print("  ✓ final_missing_start.pdf (Missing Q1 - starts at Q2)")
    doc4 = fitz.open()
    for i in range(2, 16):
        page = doc4.new_page()
        page.insert_text((72, 72), f"Question {i}\\n\\nContent for question {i}")
    doc4.save(str(demo_dir / "final_missing_start.pdf"))
    doc4.close()
    
    # 5. Quiz - Perfect (Q1-10)
    print("  ✓ quiz_complete.pdf (Questions 1-10, all present)")
    doc5 = fitz.open()
    for i in range(1, 11):
        page = doc5.new_page()
        page.insert_text((72, 72), f"Question {i}\\n\\nContent for question {i}")
    doc5.save(str(demo_dir / "quiz_complete.pdf"))
    doc5.close()
    
    # 6. Practice - Many missing (Q1-50, but missing every 5th)
    print("  ✓ practice_many_gaps.pdf (Q1-50, missing every 5th question)")
    doc6 = fitz.open()
    questions = [i for i in range(1, 51) if i % 5 != 0]
    for q in questions:
        page = doc6.new_page()
        page.insert_text((72, 72), f"Question {q}\\n\\nContent for question {q}")
    doc6.save(str(demo_dir / "practice_many_gaps.pdf"))
    doc6.close()
    
    # 7. Homework - No questions
    print("  ✓ homework_instructions.pdf (No questions - just instructions)")
    doc7 = fitz.open()
    page = doc7.new_page()
    page.insert_text((72, 72), "Homework Instructions\\n\\nPlease complete all exercises.\\n\\nNo question numbers here.")
    doc7.save(str(demo_dir / "homework_instructions.pdf"))
    doc7.close()
    
    # 8. Assignment - Out of order but complete
    print("  ✓ assignment_shuffled.pdf (Q1-8, out of order but all present)")
    doc8 = fitz.open()
    for q in [3, 1, 5, 7, 2, 4, 6, 8]:
        page = doc8.new_page()
        page.insert_text((72, 72), f"Question {q}\\n\\nContent for question {q}")
    doc8.save(str(demo_dir / "assignment_shuffled.pdf"))
    doc8.close()
    
    # 9. Review - Duplicate questions (Q1-5, with Q3 repeated)
    print("  ✓ review_with_duplicates.pdf (Q1-5, Q3 appears twice)")
    doc9 = fitz.open()
    for q in [1, 2, 3, 3, 4, 5]:
        page = doc9.new_page()
        page.insert_text((72, 72), f"Question {q}\\n\\nContent for question {q}")
    doc9.save(str(demo_dir / "review_with_duplicates.pdf"))
    doc9.close()
    
    # 10. Test - Single missing in middle
    print("  ✓ test_single_gap.pdf (Q1-20, missing only Q10)")
    doc10 = fitz.open()
    questions = [i for i in range(1, 21) if i != 10]
    for q in questions:
        page = doc10.new_page()
        page.insert_text((72, 72), f"Question {q}\\n\\nContent for question {q}")
    doc10.save(str(demo_dir / "test_single_gap.pdf"))
    doc10.close()
    
    print()
    print(f"✅ Created 10 test PDFs in: {demo_dir.absolute()}")
    print()
    return demo_dir


def print_instructions(demo_dir):
    """Print detailed instructions for batch validation"""
    print("=" * 80)
    print("BATCH VALIDATION DEMO")
    print("=" * 80)
    print()
    print("The GUI will launch. Here's how to test batch validation:")
    print()
    print("STEP 1: Click '📋 Validate Questions' button")
    print("        (Located in bottom-right of the window)")
    print()
    print("STEP 2: Choose 'Yes' when asked 'Do you want to validate multiple PDFs?'")
    print()
    print("STEP 3: Navigate to batch_demo_pdfs folder:")
    print(f"        {demo_dir.absolute()}")
    print()
    print("STEP 4: Select multiple PDFs (Ctrl+Click to select multiple)")
    print("        Try selecting all 10 PDFs at once!")
    print()
    print("EXPECTED RESULTS:")
    print("─" * 80)
    print()
    print("  ✅ exam_a_perfect.pdf          → All 25 questions present")
    print("  ✅ exam_b_perfect.pdf          → All 30 questions present")
    print("  ⚠️  midterm_incomplete.pdf     → Missing Q5, Q12, Q18")
    print("  ⚠️  final_missing_start.pdf    → Missing Q1 (Critical warning!)")
    print("  ✅ quiz_complete.pdf           → All 10 questions present")
    print("  ⚠️  practice_many_gaps.pdf     → Missing 10 questions (every 5th)")
    print("  ℹ️  homework_instructions.pdf  → No questions found")
    print("  ✅ assignment_shuffled.pdf     → All 8 questions present (order OK)")
    print("  ✅ review_with_duplicates.pdf  → All 5 questions present (dupes OK)")
    print("  ⚠️  test_single_gap.pdf        → Missing Q10")
    print()
    print("─" * 80)
    print()
    print("FEATURES TO TEST:")
    print("  • Summary header shows: ✅ Valid | ⚠️ Issues | ❌ Errors")
    print("  • Each PDF shows as a card with icon and details")
    print("  • Export results to text file (📁 button)")
    print("  • Copy to clipboard (📋 button)")
    print("  • Scroll through all results")
    print()
    print("EXPORT FORMATS:")
    print("  • Text file: Detailed report with all information")
    print("  • Clipboard: Quick summary for pasting into emails/docs")
    print()
    print("=" * 80)
    print()
    input("Press ENTER to launch the GUI and test batch validation... ")
    print()


if __name__ == "__main__":
    demo_dir = create_batch_demo_pdfs()
    print_instructions(demo_dir)
    
    print("Launching PDF Editor GUI...")
    print("(Close the window when done testing)")
    print()
    
    run_app()
