import pytest
import tkinter as tk
from tkinter import TclError
from pdf_viewer import PDFViewer
from PyPDF2 import PdfWriter


def create_sample_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with open(path, 'wb') as f:
        writer.write(f)


def test_generate_thumbnail_returns_photoimage(tmp_path):
    p = tmp_path / "sample.pdf"
    create_sample_pdf(p)

    # Try to initialize Tk; skip the test if Tcl/Tk isn't available in the environment
    try:
        root = tk.Tk()
        root.withdraw()
    except TclError as e:
        pytest.skip(f"Tk not available in this environment: {e}")

    try:
        thumb = PDFViewer.generate_thumbnail_from_path(str(p), 0, width=150, master=root)

        assert thumb is not None
        import tkinter
        assert isinstance(thumb, tkinter.PhotoImage)
    finally:
        root.destroy()
