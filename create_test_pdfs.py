"""
Test script to create a sample PDF for testing extraction
"""
from PyPDF2 import PdfWriter, PdfReader
import fitz  # PyMuPDF
from pathlib import Path


def create_test_pdf():
    """Create a simple test PDF with question markers"""
    # Create a PDF with PyMuPDF
    doc = fitz.open()
    
    # Page 1 - Title page
    page1 = doc.new_page()
    page1.insert_text((50, 100), "Test Exam", fontsize=20)
    page1.insert_text((50, 150), "Sample Questions", fontsize=16)
    
    # Page 2 - Question 1
    page2 = doc.new_page()
    page2.insert_text((50, 100), "Question 1", fontsize=14)
    page2.insert_text((50, 130), "What is 2 + 2?", fontsize=12)
    
    # Page 3 - Random content (no question)
    page3 = doc.new_page()
    page3.insert_text((50, 100), "Additional Information", fontsize=14)
    page3.insert_text((50, 130), "This page has no question marker", fontsize=12)
    
    # Page 4 - Question 2
    page4 = doc.new_page()
    page4.insert_text((50, 100), "Question 2", fontsize=14)
    page4.insert_text((50, 130), "What is the capital of France?", fontsize=12)
    
    # Page 5 - Question 3
    page5 = doc.new_page()
    page5.insert_text((50, 100), "Question 3", fontsize=14)
    page5.insert_text((50, 130), "Explain photosynthesis.", fontsize=12)
    
    # Save
    output_path = Path("test_sample.pdf")
    doc.save(str(output_path))
    doc.close()
    
    print(f"✓ Created test PDF: {output_path}")
    print(f"  Total pages: 5")
    print(f"  Expected extraction: 4 pages (title + Q1, Q2, Q3)")
    print(f"  Page without question: Page 3 should be removed")
    return output_path


def create_batch_test_pdfs():
    """Create multiple test PDFs for batch testing"""
    pdfs = []
    
    # PDF 1
    doc1 = fitz.open()
    p1 = doc1.new_page()
    p1.insert_text((50, 100), "Exam A - Title", fontsize=20)
    p2 = doc1.new_page()
    p2.insert_text((50, 100), "Question 1", fontsize=14)
    p3 = doc1.new_page()
    p3.insert_text((50, 100), "Question 2", fontsize=14)
    
    path1 = Path("test_batch_1.pdf")
    doc1.save(str(path1))
    doc1.close()
    pdfs.append(path1)
    print(f"✓ Created {path1} (3 pages, 2 questions)")
    
    # PDF 2
    doc2 = fitz.open()
    p1 = doc2.new_page()
    p1.insert_text((50, 100), "Exam B - Title", fontsize=20)
    p2 = doc2.new_page()
    p2.insert_text((50, 100), "Extra info", fontsize=14)
    p3 = doc2.new_page()
    p3.insert_text((50, 100), "Question 1", fontsize=14)
    p4 = doc2.new_page()
    p4.insert_text((50, 100), "Question 2", fontsize=14)
    p5 = doc2.new_page()
    p5.insert_text((50, 100), "Question 3", fontsize=14)
    
    path2 = Path("test_batch_2.pdf")
    doc2.save(str(path2))
    doc2.close()
    pdfs.append(path2)
    print(f"✓ Created {path2} (5 pages, 3 questions)")
    
    return pdfs


if __name__ == '__main__':
    print("=" * 60)
    print("Creating Test PDFs for Extract Feature Testing")
    print("=" * 60)
    print()
    
    # Create single test PDF
    print("Creating single test PDF...")
    single_pdf = create_test_pdf()
    print()
    
    # Create batch test PDFs
    print("Creating batch test PDFs...")
    batch_pdfs = create_batch_test_pdfs()
    print()
    
    print("=" * 60)
    print("Test PDFs Created Successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Go to Extract page")
    print("3. Test single mode with: test_sample.pdf")
    print("4. Test batch mode with: test_batch_1.pdf and test_batch_2.pdf")
    print()
    print("Expected results:")
    print("- test_sample.pdf: 5 pages → 4 pages (removes page 3)")
    print("- test_batch_1.pdf: 3 pages → 3 pages (all have markers)")
    print("- test_batch_2.pdf: 5 pages → 4 pages (removes page 2)")
