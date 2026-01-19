import os
import pytest
from pdf_manager import PDFManager
from PyPDF2 import PdfWriter, PdfReader


def create_pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    with open(path, 'wb') as f:
        writer.write(f)


def test_merge_all_creates_merged_pdf(tmp_path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    out = tmp_path / "merged.pdf"

    create_pdf(a, pages=1)
    create_pdf(b, pages=2)

    pm = PDFManager()
    pid_a = pm.add_pdf(str(a))
    pid_b = pm.add_pdf(str(b))

    pm.merge_all(str(out))

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3


def test_merge_all_with_no_pages_creates_empty_pdf(tmp_path):
    out = tmp_path / "empty.pdf"
    pm = PDFManager()

    pm.merge_all(str(out))
    assert out.exists()

    # Reading an empty/zero-page PDF may still succeed; ensure no pages
    reader = PdfReader(str(out))
    assert len(reader.pages) == 0


def test_remove_page_updates_page_count(tmp_path):
    p = tmp_path / "two.pdf"
    create_pdf(p, pages=2)

    pm = PDFManager()
    pid = pm.add_pdf(str(p))
    pages = pm.get_pages_for_pdf(pid)
    assert len(pages) == 2

    # Remove first page
    pm.remove_page(pages[0]['id'])
    assert pm.get_total_page_count() == 1
    assert pm.get_pdf_info(pid)['page_count'] == 1


def test_add_pdf_nonexistent_raises_FileNotFoundError():
    pm = PDFManager()
    with pytest.raises(FileNotFoundError):
        pm.add_pdf('does_not_exist_hopefully_12345.pdf')


def test_merge_ignores_missing_pdf_pages(tmp_path):
    p = tmp_path / "one.pdf"
    out = tmp_path / "merged2.pdf"
    create_pdf(p, pages=1)

    pm = PDFManager()
    pid = pm.add_pdf(str(p))

    # Inject a fake page entry referencing a missing PDF id
    fake = {'id': 'fake-page', 'pdf_id': 'missing-pdf', 'page_num': 1, 'page_index': 0}
    pm.all_pages.insert(0, fake)

    # Should not raise and merged output should contain only 1 valid page
    pm.merge_all(str(out))
    reader = PdfReader(str(out))
    assert len(reader.pages) == 1