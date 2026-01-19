"""
Unit tests for PDF Question Continuity Validator
Tests the validate_question_continuity method of PDFManager
"""
import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF
from pdf_manager import PDFManager


class TestQuestionValidator(unittest.TestCase):
    """Test suite for question continuity validation"""
    
    @classmethod
    def setUpClass(cls):
        """Create test PDF files once for all tests"""
        cls.test_dir = Path(__file__).parent / "test_pdfs"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Create test PDFs
        cls.perfect_pdf = cls.test_dir / "perfect_questions.pdf"
        cls.missing_middle_pdf = cls.test_dir / "missing_middle.pdf"
        cls.missing_start_pdf = cls.test_dir / "missing_start.pdf"
        cls.out_of_order_pdf = cls.test_dir / "out_of_order.pdf"
        cls.duplicates_pdf = cls.test_dir / "duplicates.pdf"
        cls.no_questions_pdf = cls.test_dir / "no_questions.pdf"
        cls.case_insensitive_pdf = cls.test_dir / "case_insensitive.pdf"
        
        # Create perfect sequence: Questions 1-10
        cls._create_pdf_with_questions(cls.perfect_pdf, list(range(1, 11)))
        
        # Missing questions 5, 7, 8
        cls._create_pdf_with_questions(cls.missing_middle_pdf, 
                                       [1, 2, 3, 4, 6, 9, 10])
        
        # Missing Question 1 (starts at 2)
        cls._create_pdf_with_questions(cls.missing_start_pdf, 
                                       list(range(2, 11)))
        
        # Out of order: 5, 1, 3, 2, 4
        cls._create_pdf_with_questions(cls.out_of_order_pdf, 
                                       [5, 1, 3, 2, 4])
        
        # With duplicates: 1, 2, 2, 3, 3, 3, 4, 5
        cls._create_pdf_with_questions(cls.duplicates_pdf, 
                                       [1, 2, 2, 3, 3, 3, 4, 5])
        
        # No questions at all
        cls._create_pdf_with_text(cls.no_questions_pdf, 
                                  "This is a PDF with no questions.")
        
        # Case insensitive: QUESTION 1, question 2, QuEsTiOn 3
        cls._create_pdf_with_case_variations(cls.case_insensitive_pdf)
    
    @classmethod
    def _create_pdf_with_questions(cls, path: Path, question_numbers: list):
        """Helper to create a PDF with specified question numbers"""
        doc = fitz.open()
        
        for q_num in question_numbers:
            page = doc.new_page()
            text = f"Question {q_num}\n\nThis is the content for question {q_num}."
            page.insert_text((72, 72), text)
        
        doc.save(str(path))
        doc.close()
    
    @classmethod
    def _create_pdf_with_text(cls, path: Path, text: str):
        """Helper to create a PDF with custom text"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        doc.save(str(path))
        doc.close()
    
    @classmethod
    def _create_pdf_with_case_variations(cls, path: Path):
        """Helper to create PDF with different case variations"""
        doc = fitz.open()
        
        variations = [
            "QUESTION 1",
            "question 2",
            "QuEsTiOn 3",
            "Question 4"
        ]
        
        for text in variations:
            page = doc.new_page()
            page.insert_text((72, 72), text)
        
        doc.save(str(path))
        doc.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test PDFs after all tests"""
        # Remove test files
        for pdf_file in cls.test_dir.glob("*.pdf"):
            pdf_file.unlink()
        
        # Remove test directory if empty
        try:
            cls.test_dir.rmdir()
        except:
            pass
    
    def setUp(self):
        """Create a new PDFManager instance for each test"""
        self.manager = PDFManager()
    
    def test_perfect_sequence(self):
        """Test PDF with perfect question sequence (1-10)"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.perfect_pdf)
        )
        
        self.assertTrue(is_valid, "Perfect sequence should be valid")
        self.assertEqual(missing, [], "Should have no missing questions")
        self.assertEqual(max_q, 10, "Maximum question should be 10")
    
    def test_missing_middle_questions(self):
        """Test PDF missing questions 5, 7, 8"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.missing_middle_pdf)
        )
        
        self.assertFalse(is_valid, "Should be invalid with missing questions")
        self.assertEqual(missing, [5, 7, 8], "Should identify missing questions")
        self.assertEqual(max_q, 10, "Maximum question should be 10")
    
    def test_missing_start(self):
        """Test PDF missing Question 1"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.missing_start_pdf)
        )
        
        self.assertFalse(is_valid, "Should be invalid when Question 1 is missing")
        self.assertIn(1, missing, "Question 1 should be in missing list")
        self.assertEqual(max_q, 10, "Maximum question should be 10")
    
    def test_out_of_order(self):
        """Test PDF with questions in non-sequential page order"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.out_of_order_pdf)
        )
        
        self.assertTrue(is_valid, "Should be valid even when out of order")
        self.assertEqual(missing, [], "All questions 1-5 should be found")
        self.assertEqual(max_q, 5, "Maximum question should be 5")
    
    def test_duplicates(self):
        """Test PDF with duplicate question numbers"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.duplicates_pdf)
        )
        
        self.assertTrue(is_valid, "Should be valid even with duplicates")
        self.assertEqual(missing, [], "All questions 1-5 should be found")
        self.assertEqual(max_q, 5, "Maximum question should be 5")
    
    def test_no_questions(self):
        """Test PDF with no questions"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.no_questions_pdf)
        )
        
        self.assertTrue(is_valid, "Should be valid (no questions to check)")
        self.assertEqual(missing, [], "Should have no missing questions")
        self.assertEqual(max_q, 0, "Maximum question should be 0")
    
    def test_case_insensitive(self):
        """Test case-insensitive pattern matching"""
        is_valid, missing, max_q = self.manager.validate_question_continuity(
            str(self.case_insensitive_pdf)
        )
        
        self.assertTrue(is_valid, "Should find questions regardless of case")
        self.assertEqual(missing, [], "All questions 1-4 should be found")
        self.assertEqual(max_q, 4, "Maximum question should be 4")
    
    def test_nonexistent_file(self):
        """Test with nonexistent file path"""
        with self.assertRaises(RuntimeError):
            self.manager.validate_question_continuity("nonexistent.pdf")
    
    def test_large_gap(self):
        """Test PDF with large gap in question numbers"""
        # Create PDF with questions 1, 2, 50
        test_pdf = self.test_dir / "large_gap.pdf"
        self._create_pdf_with_questions(test_pdf, [1, 2, 50])
        
        try:
            is_valid, missing, max_q = self.manager.validate_question_continuity(
                str(test_pdf)
            )
            
            self.assertFalse(is_valid, "Should be invalid with large gap")
            self.assertEqual(len(missing), 47, "Should have 47 missing questions (3-49)")
            self.assertEqual(max_q, 50, "Maximum question should be 50")
            self.assertEqual(missing[0], 3, "First missing should be 3")
            self.assertEqual(missing[-1], 49, "Last missing should be 49")
        finally:
            test_pdf.unlink()


if __name__ == '__main__':
    unittest.main()
