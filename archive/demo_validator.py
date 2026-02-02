"""
Quick Demo - Question Validator GUI Integration

This script creates sample PDFs and launches the GUI for demonstration.
Run this to see the validator in action with real test data.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz  # PyMuPDF
from main import main as run_app


def create_demo_pdfs():
    """Create sample PDFs for testing the validator"""
    demo_dir = Path(__file__).parent / "demo_pdfs"
    demo_dir.mkdir(exist_ok=True)
    
    print("Creating demo PDFs...")
    
    # 1. Perfect exam (Questions 1-20)
    print("  ✓ Creating perfect_exam.pdf (Questions 1-20)")
    doc1 = fitz.open()
    for i in range(1, 21):
        page = doc1.new_page()
        page.insert_text((72, 72), f"Question {i}\n\nThis is question number {i}.")
    doc1.save(str(demo_dir / "perfect_exam.pdf"))
    doc1.close()
    
    # 2. Missing questions (1-15, missing 7, 11)
    print("  ✓ Creating missing_questions.pdf (Missing Q7 and Q11)")
    doc2 = fitz.open()
    questions = [1,2,3,4,5,6,8,9,10,12,13,14,15]  # Skip 7 and 11
    for q in questions:
        page = doc2.new_page()
        page.insert_text((72, 72), f"Question {q}\n\nThis is question number {q}.")
    doc2.save(str(demo_dir / "missing_questions.pdf"))
    doc2.close()
    
    # 3. No questions
    print("  ✓ Creating no_questions.pdf")
    doc3 = fitz.open()
    page = doc3.new_page()
    page.insert_text((72, 72), "This is a regular document.\n\nIt has no questions.")
    doc3.save(str(demo_dir / "no_questions.pdf"))
    doc3.close()
    
    # 4. Out of order (Questions 5,1,3,2,4)
    print("  ✓ Creating out_of_order.pdf (Q5,Q1,Q3,Q2,Q4)")
    doc4 = fitz.open()
    for q in [5,1,3,2,4]:
        page = doc4.new_page()
        page.insert_text((72, 72), f"Question {q}\n\nThis is question number {q}.")
    doc4.save(str(demo_dir / "out_of_order.pdf"))
    doc4.close()
    
    # 5. Missing Question 1
    print("  ✓ Creating missing_q1.pdf (Starting at Q2)")
    doc5 = fitz.open()
    for i in range(2, 11):
        page = doc5.new_page()
        page.insert_text((72, 72), f"Question {i}\n\nThis is question number {i}.")
    doc5.save(str(demo_dir / "missing_q1.pdf"))
    doc5.close()
    
    print(f"\n✅ Demo PDFs created in: {demo_dir.absolute()}\n")
    return demo_dir


def print_instructions(demo_dir):
    """Print usage instructions"""
    print("=" * 70)
    print("PDF EDITOR - QUESTION VALIDATOR DEMO")
    print("=" * 70)
    print()
    print("The GUI will now launch. Here's what to try:")
    print()
    print("1. Click '📋 Validate Questions' button (bottom right)")
    print("2. Navigate to the demo_pdfs folder")
    print(f"   Location: {demo_dir.absolute()}")
    print()
    print("3. Test these files:")
    print()
    print("   📄 perfect_exam.pdf")
    print("      → Should show: ✅ All 20 questions present")
    print()
    print("   📄 missing_questions.pdf")
    print("      → Should show: ⚠️ Missing Q7 and Q11")
    print()
    print("   📄 no_questions.pdf")
    print("      → Should show: ℹ️ No questions found")
    print()
    print("   📄 out_of_order.pdf")
    print("      → Should show: ✅ All 5 questions present (order doesn't matter!)")
    print()
    print("   📄 missing_q1.pdf")
    print("      → Should show: ⚠️ Missing Q1 (with critical warning)")
    print()
    print("=" * 70)
    print()
    input("Press ENTER to launch the GUI... ")
    print()


if __name__ == "__main__":
    demo_dir = create_demo_pdfs()
    print_instructions(demo_dir)
    
    # Launch the GUI
    print("Launching PDF Editor GUI...")
    print("(Close the window to exit)")
    print()
    
    run_app()
