"""
PDF Viewer Web - Web-compatible version without Tkinter dependencies
Generates Base64-encoded thumbnails for browser display
"""
import fitz  # PyMuPDF
import base64
from typing import Optional


class PDFViewerWeb:
    """Utilities for rendering PDF pages as thumbnails for web display"""
    
    @staticmethod
    def generate_thumbnail_base64(pdf_path: str, page_index: int, width: int = 200) -> Optional[str]:
        """
        Generate a Base64-encoded PNG thumbnail from a PDF page
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 0-based page index
            width: Desired thumbnail width in pixels
            
        Returns:
            Base64-encoded PNG string suitable for use in HTML img src,
            or None if thumbnail generation fails
        """
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            if page_index >= len(doc):
                doc.close()
                return None
            
            # Get the page
            page = doc[page_index]
            
            # Calculate zoom to achieve desired width
            rect = page.rect
            zoom = width / rect.width
            
            # Render page to pixmap
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Get PNG bytes from pixmap
            try:
                png_bytes = pix.tobytes("png")
            except (TypeError, AttributeError):
                # Fallback for other PyMuPDF versions
                png_bytes = pix.getPNGData()
            
            # Close document
            doc.close()
            
            # Encode PNG as base64
            b64_string = base64.b64encode(png_bytes).decode('ascii')
            
            # Return data URI format for direct use in <img src="">
            return f"data:image/png;base64,{b64_string}"
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    @staticmethod
    def generate_thumbnail_bytes(pdf_path: str, page_index: int, width: int = 200) -> Optional[bytes]:
        """
        Generate PNG thumbnail bytes from a PDF page
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 0-based page index
            width: Desired thumbnail width in pixels
            
        Returns:
            PNG image bytes, or None if thumbnail generation fails
        """
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            if page_index >= len(doc):
                doc.close()
                return None
            
            # Get the page
            page = doc[page_index]
            
            # Calculate zoom to achieve desired width
            rect = page.rect
            zoom = width / rect.width
            
            # Render page to pixmap
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Get PNG bytes from pixmap
            try:
                png_bytes = pix.tobytes("png")
            except (TypeError, AttributeError):
                # Fallback for other PyMuPDF versions
                png_bytes = pix.getPNGData()
            
            # Close document
            doc.close()
            
            return png_bytes
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
