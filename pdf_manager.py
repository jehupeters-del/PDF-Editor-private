"""
PDF Manager - Handles PDF document operations
"""
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF


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
        # Find the page to remove to capture its pdf_id
        page = next((p for p in self.all_pages if p['id'] == page_id), None)
        if page is None:
            return
        pdf_id = page['pdf_id']

        # Remove the page
        self.all_pages = [p for p in self.all_pages if p['id'] != page_id]

        # Update page count for the PDF if it still exists
        if pdf_id in self.pdfs:
            remaining = len([p for p in self.all_pages if p['pdf_id'] == pdf_id])
            self.pdfs[pdf_id]['page_count'] = remaining
                
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
                
        # Write output with error handling
        try:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        except OSError as e:
            # Handle disk full, permission errors, etc.
            raise OSError(f"Failed to write PDF to {output_path}: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Unexpected error writing PDF to {output_path}: {str(e)}") from e
    
    def validate_question_continuity(self, pdf_path: str) -> Tuple[bool, List[int], int]:
        """
        Validate that question numbers in a PDF are sequential and complete.
        
        Scans the PDF for patterns like "Question {number}" (case-insensitive) and
        verifies that all integers from 1 to the maximum question number exist.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Returns:
            Tuple containing:
            - bool: True if all questions are present, False otherwise
            - List[int]: List of missing question numbers (empty if all present)
            - int: Maximum question number found (0 if no questions found)
            
        Edge Cases:
            - Missing Start: If "Question 1" is missing, it will be in the missing list
            - Out of Order: Works regardless of physical page order
            - Duplicates: Acceptable, as long as each number exists at least once
            
        Example:
            >>> is_valid, missing, max_q = manager.validate_question_continuity("exam.pdf")
            >>> if not is_valid:
            ...     print(f"Missing questions: {missing}")
        """
        try:
            # Open PDF with PyMuPDF for fast text extraction
            doc = fitz.open(pdf_path)
            
            # Pattern to match "Question {number}" (case-insensitive)
            pattern = re.compile(r'\bquestion\s+(\d+)\b', re.IGNORECASE)
            
            # Set to store all found question numbers
            found_questions = set()
            
            # Extract text from all pages and find question numbers
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Find all question numbers on this page
                matches = pattern.findall(text)
                for match in matches:
                    found_questions.add(int(match))
            
            doc.close()
            
            # Handle case where no questions were found
            if not found_questions:
                return True, [], 0
            
            # Find the maximum question number
            max_question = max(found_questions)
            
            # Check for missing questions from 1 to max
            expected_questions = set(range(1, max_question + 1))
            missing_questions = sorted(expected_questions - found_questions)
            
            # Return results
            is_valid = len(missing_questions) == 0
            return is_valid, missing_questions, max_question
            
        except Exception as e:
            # If there's an error reading the PDF, raise it
            raise RuntimeError(f"Error validating PDF: {str(e)}")
    
    def extract_question_pages(self, input_path: str, output_path: str) -> Tuple[int, int, List[int], bool, List[int], int]:
        """
        Extract only pages that contain question numbers, removing all other pages.
        
        This function scans through a PDF, identifies pages with "Question {number}" text,
        extracts only those pages, and saves them to a new PDF. It then validates the
        result to ensure no questions were dropped.
        
        Args:
            input_path: Path to the source PDF file
            output_path: Path where the extracted PDF will be saved
            
        Returns:
            Tuple containing:
            - int: Original page count (before extraction)
            - int: Extracted page count (after extraction)
            - List[int]: Question numbers found (in order extracted)
            - bool: Validation result (True if all questions present)
            - List[int]: Missing questions (empty if valid)
            - int: Maximum question number found
            
        Example:
            >>> result = manager.extract_question_pages("messy_exam.pdf", "clean_exam.pdf")
            >>> orig_pages, new_pages, questions, valid, missing, max_q = result
            >>> print(f"Reduced from {orig_pages} to {new_pages} pages")
            >>> print(f"Extracted questions: {questions}")
            >>> if not valid:
            ...     print(f"WARNING: Missing questions {missing}")
        """
        try:
            # Open the source PDF
            doc = fitz.open(input_path)
            original_page_count = len(doc)
            
            # Pattern to match "Question {number}"
            pattern = re.compile(r'\bquestion\s+(\d+)\b', re.IGNORECASE)
            
            # Dictionary to map page numbers to question numbers
            page_to_questions = {}
            
            # Always keep the first page (title page)
            page_to_questions[0] = []  # Empty list means it's a title page, not a question page
            
            # Scan each page for question numbers
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Find all question numbers on this page
                matches = pattern.findall(text)
                if matches:
                    # Store all unique question numbers found on this page
                    question_nums = sorted(set(int(m) for m in matches))
                    page_to_questions[page_num] = question_nums
            
            # Close the source document
            doc.close()
            
            # If no questions found, return early
            if not page_to_questions:
                raise ValueError("No pages with question numbers found in the PDF")
            
            # Create new PDF with only question pages
            doc = fitz.open(input_path)  # Reopen for extraction
            output_doc = fitz.open()  # New empty document
            
            # Track which questions we're extracting
            extracted_questions = []
            
            # Extract pages in order
            for page_num in sorted(page_to_questions.keys()):
                # Insert the page into the output document
                output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Record which questions are on this page
                extracted_questions.extend(page_to_questions[page_num])
            
            # Save the output with compression and optimization
            try:
                output_doc.save(
                    output_path,
                    garbage=4,  # Maximum garbage collection (removes unused objects)
                    deflate=True,  # Compress content streams
                    clean=True  # Clean and optimize the PDF structure
                )
            except OSError as e:
                # Handle disk full, permission errors, quota exceeded, etc.
                output_doc.close()
                doc.close()
                raise OSError(f"Failed to save PDF to {output_path}. This may be due to disk space, permissions, or quota limits: {str(e)}") from e
            except Exception as e:
                output_doc.close()
                doc.close()
                raise Exception(f"Unexpected error saving PDF to {output_path}: {str(e)}") from e
            
            output_doc.close()
            doc.close()
            
            # Get statistics
            extracted_page_count = len(page_to_questions)
            unique_questions = sorted(set(extracted_questions))
            
            # Validate the extracted PDF
            is_valid, missing, max_question = self.validate_question_continuity(output_path)
            
            return (
                original_page_count,
                extracted_page_count,
                unique_questions,
                is_valid,
                missing,
                max_question
            )
            
        except Exception as e:
            raise RuntimeError(f"Error extracting question pages: {str(e)}")
    
    @staticmethod
    def generate_smart_filename(original_filename: str) -> str:
        """
        Generate a smart output filename based on patterns in the input filename.
        
        Examples:
            pc_mg_jun_13 → June 2013 solutions.pdf
            pc_mg_jan_13 → Jan 2013 solutions.pdf
            math_exam_may_15 → May 2015 solutions.pdf
            quiz_dec_20 → Dec 2020 solutions.pdf
            
        Args:
            original_filename: The original PDF filename (with or without .pdf)
            
        Returns:
            Smart filename with month, year, and "solutions" suffix
        """
        # Remove .pdf extension if present
        name = original_filename.lower().replace('.pdf', '')
        
        # Month mapping
        months = {
            'jan': 'Jan', 'january': 'January',
            'feb': 'Feb', 'february': 'February',
            'mar': 'Mar', 'march': 'March',
            'apr': 'Apr', 'april': 'April',
            'may': 'May',
            'jun': 'Jun', 'june': 'June',
            'jul': 'Jul', 'july': 'July',
            'aug': 'Aug', 'august': 'August',
            'sep': 'Sep', 'sept': 'Sept', 'september': 'September',
            'oct': 'Oct', 'october': 'October',
            'nov': 'Nov', 'november': 'November',
            'dec': 'Dec', 'december': 'December'
        }
        
        # Try to find month and year
        found_month = None
        found_year = None
        
        # Split by common separators
        parts = re.split(r'[_\-\s]+', name)
        
        # Look for month
        for part in parts:
            if part in months:
                found_month = months[part]
                break
        
        # Look for year (2 or 4 digit)
        for part in parts:
            # Check for 2-digit year (e.g., "13" for 2013)
            if part.isdigit() and len(part) == 2:
                year_num = int(part)
                # Assume 00-50 is 2000s, 51-99 is 1900s
                if year_num <= 50:
                    found_year = 2000 + year_num
                else:
                    found_year = 1900 + year_num
                break
            # Check for 4-digit year
            elif part.isdigit() and len(part) == 4:
                found_year = int(part)
                break
        
        # Generate filename
        if found_month and found_year:
            return f"{found_month} {found_year} solutions.pdf"
        elif found_month:
            return f"{found_month} solutions.pdf"
        elif found_year:
            return f"{found_year} solutions.pdf"
        else:
            # Fallback to original name with _solutions suffix
            clean_name = original_filename.replace('.pdf', '')
            return f"{clean_name}_solutions.pdf"
