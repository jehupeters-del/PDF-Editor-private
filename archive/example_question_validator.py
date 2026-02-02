"""
Example usage of the PDF Question Continuity Validator

This script demonstrates how to use the validate_question_continuity method
to check if a PDF has all questions in sequence.
"""
from pdf_manager import PDFManager
from pathlib import Path


def validate_pdf_questions(pdf_path: str):
    """
    Validate question continuity in a PDF and print results.
    
    Args:
        pdf_path: Path to the PDF file to validate
    """
    manager = PDFManager()
    
    print(f"\nValidating: {Path(pdf_path).name}")
    print("-" * 60)
    
    try:
        is_valid, missing, max_question = manager.validate_question_continuity(pdf_path)
        
        if max_question == 0:
            print("ℹ  No questions found in this PDF")
        elif is_valid:
            print(f"✓ All questions present (1 to {max_question})")
            print(f"✓ Total questions: {max_question}")
        else:
            print(f"✗ Missing questions detected!")
            print(f"  Expected range: 1 to {max_question}")
            print(f"  Missing questions: {missing}")
            print(f"  Count of missing: {len(missing)}")
            
            # Helpful suggestions
            if 1 in missing:
                print("\n  ⚠ Warning: Question 1 is missing!")
            
            if len(missing) > 10:
                print(f"\n  ⚠ Large gap detected ({len(missing)} questions missing)")
        
        return is_valid, missing, max_question
        
    except RuntimeError as e:
        print(f"✗ Error: {e}")
        return None, None, None


def main():
    """Main example demonstrating different scenarios"""
    print("=" * 60)
    print("PDF Question Continuity Validator - Examples")
    print("=" * 60)
    
    # Example 1: Check a merged exam PDF
    print("\n📋 Example 1: Validating a merged exam")
    print("This would typically be called after merging PDFs")
    
    # In practice, you would use this after creating a merged PDF
    # For example:
    # manager = PDFManager()
    # manager.add_pdf("exam_part1.pdf")
    # manager.add_pdf("exam_part2.pdf")
    # manager.merge_all("merged_exam.pdf")
    # validate_pdf_questions("merged_exam.pdf")
    
    print("""
Usage in your workflow:
1. Load and arrange PDF pages using PDFManager
2. Merge pages to create final PDF
3. Call validate_question_continuity() on the output
4. Report any missing questions before distribution
    """)
    
    # Example 2: Integration with existing merge workflow
    print("\n📋 Example 2: Integrated merge workflow")
    print("""
def merge_and_validate(pdf_manager, output_path):
    '''Merge PDFs and validate question continuity'''
    # Merge all pages
    pdf_manager.merge_all(output_path)
    
    # Validate the merged result
    is_valid, missing, max_q = pdf_manager.validate_question_continuity(output_path)
    
    if not is_valid:
        print(f"WARNING: Missing questions: {missing}")
        print("Please verify the source PDFs before distributing!")
        return False
    
    print(f"Success! All {max_q} questions are present.")
    return True
    """)
    
    # Example 3: API Reference
    print("\n📋 API Reference")
    print("""
Method Signature:
    validate_question_continuity(pdf_path: str) -> Tuple[bool, List[int], int]

Parameters:
    pdf_path: str - Path to the PDF file to validate

Returns:
    Tuple containing:
    - is_valid (bool): True if all questions 1-max are present
    - missing (List[int]): List of missing question numbers (empty if valid)
    - max_question (int): Highest question number found (0 if none)

Features:
    ✓ Case-insensitive pattern matching ("Question", "QUESTION", "question")
    ✓ Works with questions in any page order
    ✓ Handles duplicate question numbers gracefully
    ✓ Fast text extraction using PyMuPDF (fitz)
    ✓ Identifies specific missing questions, not just count
    
Edge Cases Handled:
    - Missing Question 1: Explicitly flagged in missing list
    - Out of order pages: Scans entire document regardless of order
    - Duplicates: Acceptable as long as each number appears at least once
    - No questions: Returns (True, [], 0) - valid empty case
    """)


if __name__ == "__main__":
    main()
