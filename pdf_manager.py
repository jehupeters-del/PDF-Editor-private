"""
PDF Manager - Handles PDF document operations
"""
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from PyPDF2 import PdfReader, PdfWriter


class PDFManager:
    def __init__(self):
        self.pdfs: Dict[str, dict] = {}
        self.all_pages: List[dict] = []
        
    def add_pdf(self, file_path: str) -> str:
        """Add a PDF file to the manager"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read PDF
        reader = PdfReader(str(file_path))
        pdf_id = str(uuid.uuid4())
        
        # Store PDF info
        self.pdfs[pdf_id] = {
            'id': pdf_id,
            'name': file_path.name,
            'path': str(file_path),
            'page_count': len(reader.pages),
            'reader': reader
        }
        
        # Create page entries
        for page_num in range(len(reader.pages)):
            page_id = f"{pdf_id}-page-{page_num}"
            page_info = {
                'id': page_id,
                'pdf_id': pdf_id,
                'page_num': page_num + 1,  # 1-indexed for display
                'page_index': page_num,     # 0-indexed for PyPDF2
            }
            self.all_pages.append(page_info)
            
        return pdf_id
        
    def remove_pdf(self, pdf_id: str):
        """Remove a PDF and all its pages"""
        if pdf_id in self.pdfs:
            # Remove all pages from this PDF
            self.all_pages = [p for p in self.all_pages if p['pdf_id'] != pdf_id]
            
            # Remove PDF
            del self.pdfs[pdf_id]
            
    def remove_page(self, page_id: str):
        """Remove a single page"""
        self.all_pages = [p for p in self.all_pages if p['id'] != page_id]
        
        # Update page count for the PDF
        for page in self.all_pages:
            if page['id'] == page_id:
                pdf_id = page['pdf_id']
                if pdf_id in self.pdfs:
                    remaining = len([p for p in self.all_pages if p['pdf_id'] == pdf_id])
                    self.pdfs[pdf_id]['page_count'] = remaining
                break
                
    def get_all_pdfs(self) -> Dict[str, dict]:
        """Get all loaded PDFs"""
        return self.pdfs
        
    def get_pdf_info(self, pdf_id: str) -> Optional[dict]:
        """Get info for a specific PDF"""
        return self.pdfs.get(pdf_id)
        
    def get_pages_for_pdf(self, pdf_id: str) -> List[dict]:
        """Get all pages for a specific PDF"""
        return [p for p in self.all_pages if p['pdf_id'] == pdf_id]
        
    def get_total_page_count(self) -> int:
        """Get total number of pages across all PDFs"""
        return len(self.all_pages)
        
    def merge_all(self, output_path: str):
        """Merge all pages into a single PDF"""
        writer = PdfWriter()
        
        # Add pages in current order
        for page_info in self.all_pages:
            pdf_id = page_info['pdf_id']
            page_index = page_info['page_index']
            
            if pdf_id in self.pdfs:
                reader = self.pdfs[pdf_id]['reader']
                writer.add_page(reader.pages[page_index])
                
        # Write output
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
