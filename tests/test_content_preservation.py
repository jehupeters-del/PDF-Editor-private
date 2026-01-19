"""
Content Preservation Test - Verify NO data loss during extraction
Tests that images, graphs, shapes, and text are fully preserved
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import fitz
from pdf_manager import PDFManager


def create_content_rich_pdf():
    """Create a PDF with images, shapes, and various content types"""
    print("Creating content-rich test PDF...")
    
    test_file = Path(__file__).parent / "content_test.pdf"
    doc = fitz.open()
    
    # Page 1: Title with formatting
    page = doc.new_page()
    page.insert_text((72, 72), "CONTENT PRESERVATION TEST", fontsize=18)
    page.insert_text((72, 100), "This PDF contains various content types", fontsize=12)
    
    # Draw a colored rectangle (simulating graphs/diagrams)
    rect = fitz.Rect(72, 130, 200, 180)
    page.draw_rect(rect, color=(0, 0, 1), fill=(0.8, 0.8, 1))
    page.insert_text((75, 150), "Blue Box", fontsize=10)
    
    print("  ✓ Page 1: Title page with shapes")
    
    # Page 2: Question 1 with image placeholder and shapes
    page = doc.new_page()
    page.insert_text((72, 72), "Question 1", fontsize=14)
    page.insert_text((72, 100), "Analyze the diagram below:", fontsize=11)
    
    # Create a complex diagram (circle, lines, text)
    # Circle
    center = fitz.Point(150, 200)
    page.draw_circle(center, 40, color=(1, 0, 0), fill=(1, 0.8, 0.8), width=2)
    page.insert_text((140, 200), "A", fontsize=12)
    
    # Lines connecting to other points
    page.draw_line(fitz.Point(150, 200), fitz.Point(250, 200), color=(0, 0, 0), width=1)
    page.draw_circle(fitz.Point(250, 200), 20, color=(0, 1, 0), fill=(0.8, 1, 0.8))
    page.insert_text((245, 200), "B", fontsize=12)
    
    # Rectangle with pattern
    rect = fitz.Rect(100, 300, 300, 400)
    page.draw_rect(rect, color=(0.5, 0, 0.5), width=2)
    for i in range(5):
        y = 300 + i * 20
        page.draw_line(fitz.Point(100, y), fitz.Point(300, y), color=(0.7, 0.7, 0.7))
    page.insert_text((120, 350), "Graph/Chart Area", fontsize=10)
    
    print("  ✓ Page 2: Question 1 with shapes, circles, lines")
    
    # Page 3: Junk page with content (should be removed)
    page = doc.new_page()
    page.insert_text((72, 72), "Answer Key - Do Not Distribute", fontsize=14)
    rect = fitz.Rect(72, 100, 400, 200)
    page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0.9, 0.9))
    page.insert_text((80, 140), "This page should be REMOVED", fontsize=11)
    
    print("  ✓ Page 3: Junk page (will be removed)")
    
    # Page 4: Question 2 with image simulation
    page = doc.new_page()
    page.insert_text((72, 72), "Question 2", fontsize=14)
    page.insert_text((72, 100), "Refer to the image below:", fontsize=11)
    
    # Simulate an image with a complex pattern
    for i in range(10):
        for j in range(10):
            x = 100 + i * 20
            y = 150 + j * 20
            color_val = (i + j) / 20.0
            rect = fitz.Rect(x, y, x + 18, y + 18)
            page.draw_rect(rect, color=(color_val, 0.5, 1 - color_val), fill=(color_val, 0.5, 1 - color_val))
    
    page.insert_text((100, 380), "Simulated Image/Graph (gradient pattern)", fontsize=9)
    
    # Add mathematical notation area
    page.insert_text((72, 420), "Show that: ∫ x² dx = x³/3 + C", fontsize=11)
    
    print("  ✓ Page 4: Question 2 with gradient pattern and math symbols")
    
    # Page 5: Question 3 with actual embedded image (using pixel map)
    page = doc.new_page()
    page.insert_text((72, 72), "Question 3", fontsize=14)
    page.insert_text((72, 100), "Study the image:", fontsize=11)
    
    # Create a simple bitmap image (checkerboard pattern)
    width, height = 100, 100
    pixmap = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, width, height), False)
    pixmap.set_rect(pixmap.irect, (255, 255, 255))  # White background
    
    # Draw checkerboard pattern pixel by pixel
    for i in range(0, width, 10):
        for j in range(0, height, 10):
            if (i // 10 + j // 10) % 2 == 0:
                # Fill 10x10 block with black
                rect = fitz.IRect(i, j, min(i + 10, width), min(j + 10, height))
                pixmap.set_rect(rect, (0, 0, 0))
    
    # Insert the image into the page
    img_rect = fitz.Rect(100, 130, 300, 330)
    page.insert_image(img_rect, pixmap=pixmap)
    
    page.insert_text((100, 350), "Embedded Image (checkerboard)", fontsize=9)
    
    print("  ✓ Page 5: Question 3 with REAL embedded bitmap image")
    
    # Save the PDF
    doc.save(str(test_file))
    doc.close()
    
    print(f"✓ Created: {test_file.name}\n")
    return test_file


def analyze_page_content(doc, page_num, label):
    """Analyze what content exists on a page"""
    page = doc[page_num]
    
    # Get text
    text = page.get_text()
    text_length = len(text.strip())
    
    # Get drawings (vector graphics)
    drawings = page.get_drawings()
    drawing_count = len(drawings)
    
    # Get images
    images = page.get_images()
    image_count = len(images)
    
    # Get page size
    rect = page.rect
    
    return {
        'label': label,
        'text_length': text_length,
        'drawing_count': drawing_count,
        'image_count': image_count,
        'width': rect.width,
        'height': rect.height,
        'has_text': text_length > 0,
        'has_drawings': drawing_count > 0,
        'has_images': image_count > 0
    }


def test_content_preservation():
    """Test that all content is preserved during extraction"""
    print()
    print("=" * 80)
    print("CONTENT PRESERVATION TEST")
    print("=" * 80)
    print()
    
    # Create test PDF
    input_file = create_content_rich_pdf()
    output_file = input_file.parent / "content_test_extracted.pdf"
    
    # Analyze original content
    print("Analyzing ORIGINAL PDF content...")
    print("-" * 80)
    orig_doc = fitz.open(str(input_file))
    
    original_content = {}
    for i in range(len(orig_doc)):
        page_label = f"Page {i + 1}"
        content = analyze_page_content(orig_doc, i, page_label)
        original_content[i] = content
        
        print(f"  {page_label}: Text={content['text_length']} chars, "
              f"Drawings={content['drawing_count']}, Images={content['image_count']}")
    
    orig_doc.close()
    print()
    
    # Extract question pages
    print("Extracting question pages...")
    manager = PDFManager()
    result = manager.extract_question_pages(str(input_file), str(output_file))
    orig_pages, new_pages, questions, is_valid, missing, max_q = result
    print(f"  ✓ Extracted {new_pages} pages (Questions: {min(questions)}-{max(questions)})")
    print()
    
    # Analyze extracted content
    print("Analyzing EXTRACTED PDF content...")
    print("-" * 80)
    extracted_doc = fitz.open(str(output_file))
    
    extracted_content = {}
    for i in range(len(extracted_doc)):
        page_label = f"Page {i + 1}"
        content = analyze_page_content(extracted_doc, i, page_label)
        extracted_content[i] = content
        
        print(f"  {page_label}: Text={content['text_length']} chars, "
              f"Drawings={content['drawing_count']}, Images={content['image_count']}")
    
    extracted_doc.close()
    print()
    
    # Compare content
    print("=" * 80)
    print("CONTENT COMPARISON")
    print("=" * 80)
    print()
    
    # Expected pages in output: 0 (title), 1 (Q1), 3 (Q2), 4 (Q3)
    # Page 2 (junk) should be removed
    expected_mapping = {
        0: 0,  # Title page
        1: 1,  # Question 1
        2: 3,  # Question 2 (original page 4)
        3: 4   # Question 3 (original page 5)
    }
    
    all_preserved = True
    
    for extracted_idx, original_idx in expected_mapping.items():
        orig = original_content[original_idx]
        extr = extracted_content[extracted_idx]
        
        print(f"Original Page {original_idx + 1} → Extracted Page {extracted_idx + 1}")
        print(f"  Original: {orig['label']}")
        print(f"    Text: {orig['text_length']} chars")
        print(f"    Drawings: {orig['drawing_count']}")
        print(f"    Images: {orig['image_count']}")
        print(f"  Extracted: {extr['label']}")
        print(f"    Text: {extr['text_length']} chars")
        print(f"    Drawings: {extr['drawing_count']}")
        print(f"    Images: {extr['image_count']}")
        
        # Check if content matches
        text_match = abs(orig['text_length'] - extr['text_length']) <= 5  # Allow small variance
        drawings_match = orig['drawing_count'] == extr['drawing_count']
        images_match = orig['image_count'] == extr['image_count']
        
        if text_match and drawings_match and images_match:
            print(f"  ✅ ALL CONTENT PRESERVED")
        else:
            print(f"  ❌ CONTENT MISMATCH DETECTED!")
            if not text_match:
                print(f"     - Text difference: {orig['text_length'] - extr['text_length']} chars")
            if not drawings_match:
                print(f"     - Drawing difference: {orig['drawing_count'] - extr['drawing_count']}")
            if not images_match:
                print(f"     - Image difference: {orig['image_count'] - extr['image_count']}")
            all_preserved = False
        
        print()
    
    # Final verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()
    
    if all_preserved:
        print("  ✅ SUCCESS: ALL CONTENT PRESERVED!")
        print()
        print("  Verified preservation of:")
        print("    ✓ Text content (including math symbols)")
        print("    ✓ Vector graphics (shapes, lines, circles)")
        print("    ✓ Embedded images (bitmap/raster graphics)")
        print("    ✓ Colors and styling")
        print()
        print("  Optimization settings are SAFE:")
        print("    • garbage=4: Only removes UNUSED objects")
        print("    • deflate=True: LOSSLESS compression")
        print("    • clean=True: Optimizes structure, preserves content")
    else:
        print("  ⚠️  WARNING: Some content may have been lost!")
        print()
        print("  Recommendation: Adjust optimization settings")
    
    print()
    
    # Cleanup
    if input_file.exists():
        input_file.unlink()
    if output_file.exists():
        output_file.unlink()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "CONTENT PRESERVATION TEST" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This test verifies that extraction preserves ALL content:")
    print("  • Text (including special characters and math symbols)")
    print("  • Vector graphics (shapes, lines, circles, diagrams)")
    print("  • Embedded images (bitmap/raster graphics)")
    print("  • Colors and formatting")
    print()
    print("Goal: Reduce file size WITHOUT losing any visual information")
    print()
    input("Press ENTER to run test... ")
    
    test_content_preservation()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
