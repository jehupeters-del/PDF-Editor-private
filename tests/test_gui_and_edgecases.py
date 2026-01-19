import os
import threading
import tkinter as tk
import pytest
from pdf_manager import PDFManager
from main import PDFEditorApp
from PyPDF2 import PdfWriter, PdfReader


def create_pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    with open(path, 'wb') as f:
        writer.write(f)


def test_gui_interactions(tmp_path, monkeypatch):
    # Create sample pdf
    p = tmp_path / "ui_sample.pdf"
    create_pdf(p, pages=1)

    # Initialize app headlessly
    root = tk.Tk()
    root.withdraw()
    app = PDFEditorApp(root)

    # Add PDF programmatically and refresh
    pid = app.pdf_manager.add_pdf(str(p))
    app.refresh_pdf_list()

    # Ensure listbox has an entry
    assert app.pdf_listbox.size() == 1

    # Select the first PDF and display pages
    app.pdf_listbox.selection_set(0)
    app.on_pdf_selected()

    # A page widget should exist
    children = app.page_frame.winfo_children()
    assert len(children) == 1

    # Toggle selection for the page, then remove selected
    page = app.pdf_manager.get_pages_for_pdf(pid)[0]
    widget = children[0]
    app.toggle_page_selection(widget, page)
    assert page['id'] in app.selected_pages

    app.remove_selected_pages()
    assert app.pdf_manager.get_total_page_count() == 0

    # Test remove selected PDF with confirmation
    # Add again
    pid = app.pdf_manager.add_pdf(str(p))
    app.refresh_pdf_list()
    app.pdf_listbox.selection_set(0)
    app.on_pdf_selected()

    # Monkeypatch messagebox.askyesno in the main module (where it's imported) to auto-confirm
    import main as _main
    monkeypatch.setattr(_main.messagebox, 'askyesno', lambda title, msg: True)
    # Sanity checks
    assert app.selected_pdf_id is not None
    assert app.selected_pdf_id in app.pdf_manager.get_all_pdfs()

    # Capture the id to be removed and run
    to_remove = app.selected_pdf_id
    app.remove_selected_pdf()

    # Ensure that specific PDF id was removed from the model
    assert to_remove not in app.pdf_manager.get_all_pdfs()

    # Refresh UI and ensure the listbox is updated
    app.refresh_pdf_list()
    # Listbox should reflect the underlying model (remaining PDFs)
    assert app.pdf_listbox.size() == len(app.pdf_manager.get_all_pdfs())

    root.destroy()


def test_merge_via_ui(monkeypatch, tmp_path):
    # Prepare PDFs
    a = tmp_path / "a_ui.pdf"
    b = tmp_path / "b_ui.pdf"
    out = tmp_path / "merged_ui.pdf"
    create_pdf(a, pages=1)
    create_pdf(b, pages=2)

    root = tk.Tk()
    root.withdraw()
    app = PDFEditorApp(root)

    app.pdf_manager.add_pdf(str(a))
    app.pdf_manager.add_pdf(str(b))
    app.refresh_pdf_list()

    # Monkeypatch asksaveasfilename to return our output path
    monkeypatch.setattr('tkinter.filedialog.asksaveasfilename', lambda **kwargs: str(out))

    # Replace threading.Thread with a dummy that runs target immediately
    class ImmediateThread:
        def __init__(self, target, daemon=True):
            self._target = target
        def start(self):
            self._target()
    monkeypatch.setattr('threading.Thread', ImmediateThread)

    # Monkeypatch messagebox.showinfo to capture message
    captured = {}
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda title, msg: captured.setdefault('info', (title, msg)))

    # Invoke merge via UI
    app.merge_pdfs()

    # Ensure merged file exists and has 3 pages
    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3

    root.destroy()


def test_merge_propagates_reader_errors(tmp_path):
    p = tmp_path / "valid.pdf"
    create_pdf(p, pages=1)

    pm = PDFManager()
    pid = pm.add_pdf(str(p))

    # Replace the reader with a broken object
    class BrokenReader:
        @property
        def pages(self):
            raise ValueError('corrupt reader')

    pm.pdfs[pid]['reader'] = BrokenReader()

    out = tmp_path / "out_err.pdf"
    with pytest.raises(ValueError):
        pm.merge_all(str(out))

    assert not out.exists()
