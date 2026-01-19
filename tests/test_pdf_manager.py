import os
from pdf_manager import PDFManager
from PyPDF2 import PdfWriter


def create_sample_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with open(path, 'wb') as f:
        writer.write(f)


def test_add_and_remove_pdf(tmp_path):
    p = tmp_path / "sample.pdf"
    create_sample_pdf(p)

    pm = PDFManager()
    assert pm.get_total_page_count() == 0

    pid = pm.add_pdf(str(p))
    assert pm.get_total_page_count() == 1

    pages = pm.get_pages_for_pdf(pid)
    assert len(pages) == 1

    # Remove the page
    pm.remove_page(pages[0]['id'])
    assert pm.get_total_page_count() == 0

    # Re-add and remove PDF
    pid = pm.add_pdf(str(p))
    pm.remove_pdf(pid)
    assert pm.get_total_page_count() == 0
