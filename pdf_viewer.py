"""
PDF Viewer - Handles PDF page rendering and display
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
from pathlib import Path
from typing import Callable, Optional


class PDFViewer:
    """Utilities for rendering PDF pages as thumbnails"""
    
    @staticmethod
    def create_page_widget(parent: tk.Widget, page: dict, pdf_path: str, on_remove: Callable, on_select: Callable) -> ttk.Frame:
        """
        Create a widget displaying a page thumbnail with remove button
        
        Args:
            parent: Parent widget
            page: Page info dict with 'id', 'pdf_id', 'page_num', 'page_index'
            pdf_path: Path to the PDF file
            on_remove: Callback function when remove button is clicked
            on_select: Callback function when widget is clicked (for multi-select)
        """
        frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        
        # Generate thumbnail
        thumbnail = PDFViewer.generate_thumbnail_from_path(pdf_path, page['page_index'], width=150)
        
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
    def generate_thumbnail_from_path(pdf_path: str, page_index: int, width: int = 150) -> Optional[ImageTk.PhotoImage]:
        """
        Generate a thumbnail image from a PDF page using PyMuPDF
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 0-based page index
            width: Desired thumbnail width in pixels
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
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Close document
            doc.close()
            
            # Convert to PhotoImage
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
