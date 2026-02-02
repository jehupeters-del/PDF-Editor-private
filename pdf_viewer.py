"""
PDF Viewer - Handles PDF page rendering and display
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional

# Keep tkinter imports for backwards compatibility with desktop app
try:
    import tkinter as tk
    from tkinter import ttk
    import base64
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class PDFViewer:
    """Utilities for rendering PDF pages as thumbnails"""
    
    @staticmethod
    def create_page_widget(parent, page: dict, pdf_path: str, on_remove, on_select):
        """
        Create a widget displaying a page thumbnail with remove button (Tkinter version)
        
        Args:
            parent: Parent widget
            page: Page info dict with 'id', 'pdf_id', 'page_num', 'page_index'
            pdf_path: Path to the PDF file
            on_remove: Callback function when remove button is clicked
            on_select: Callback function when widget is clicked (for multi-select)
        """
        if not TKINTER_AVAILABLE:
            raise ImportError("Tkinter not available")
            
        frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        
        # Generate thumbnail (pass parent as master for the PhotoImage to ensure same Tcl interpreter)
        master = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else None
        thumbnail = PDFViewer.generate_thumbnail_from_path(pdf_path, page['page_index'], width=150, master=master)
        
        if thumbnail:
            # Display thumbnail
            img_label = tk.Label(frame, image=thumbnail, bg="white")
            img_label.image = thumbnail  # Keep reference
            img_label.pack(padx=5, pady=5)
        else:
            # Placeholder if thumbnail generation fails
            placeholder = tk.Label(
                frame, 
                text="PDF Page", 
                width=20, 
                height=15,
                bg="lightgray"
            )
            placeholder.pack(padx=5, pady=5)
        
        # Bind click for selection (with Ctrl key for multi-select feel)
        frame.bind('<Button-1>', lambda e: on_select(frame, page))
        
        # Page number label
        page_label = ttk.Label(
            frame, 
            text=f"Page {page['page_num']}", 
            font=("Arial", 9)
        )
        page_label.pack(pady=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(
            frame,
            text="Remove",
            command=on_remove,
            width=10
        )
        remove_btn.pack(pady=(0, 5))
        
        return frame
    
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
        
    @staticmethod        
    def generate_thumbnail_from_path(pdf_path: str, page_index: int, width: int = 150, master=None):
        """
        Generate a thumbnail image from a PDF page using PyMuPDF (Tkinter version)
        Uses PNG bytes from PyMuPDF and Tk's PhotoImage to avoid Pillow dependency.
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 0-based page index
            width: Desired thumbnail width in pixels
            master: Tkinter master widget
        """
        if not TKINTER_AVAILABLE:
            return None
            
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
            
            # Try to get PNG bytes from pixmap (API varies across versions)
            try:
                png_bytes = pix.tobytes("png")
            except TypeError:
                # Fallback for other PyMuPDF versions
                png_bytes = pix.getPNGData()
            
            # Close document
            doc.close()
            
            # Encode PNG as base64 and return a Tk PhotoImage (attach to the provided master or the default root)
            b64 = base64.b64encode(png_bytes).decode('ascii')
            final_master = master if master is not None else (tk._default_root if getattr(tk, "_default_root", None) is not None else None)
            if final_master:
                return tk.PhotoImage(master=final_master, data=b64)
            return tk.PhotoImage(data=b64)
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
