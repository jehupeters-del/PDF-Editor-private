"""
PDF Viewer - PDF page rendering utilities
"""
import fitz  # PyMuPDF


class PDFViewer:
    """Utilities for rendering PDF pages as thumbnails"""

    @staticmethod
    def generate_thumbnail(pdf_path: str, page_index: int, output_path: str, width: int = 180) -> bool:
        """
        Generate a thumbnail PNG file from a PDF page (for Flask web app)
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 0-based page index
            output_path: Path where PNG thumbnail should be saved
            width: Desired thumbnail width in pixels
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            if page_index >= len(doc):
                doc.close()
                return False
            
            # Get the page
            page = doc[page_index]
            
            # Calculate zoom to achieve desired width
            rect = page.rect
            zoom = width / rect.width
            
            # Render page to pixmap
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save as PNG
            pix.save(output_path)
            
            # Close document
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False
