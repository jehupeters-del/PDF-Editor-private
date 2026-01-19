import traceback
import tkinter as tk
from pdf_manager import PDFManager
from pdf_viewer import PDFViewer
from PyPDF2 import PdfWriter

try:
    print('Creating test PDF...')
    # Create a small one-page test PDF
    p = 'test_sample.pdf'
    writer = PdfWriter()
    # Add a blank page (A4-ish)
    writer.add_blank_page(width=595, height=842)
    with open(p, 'wb') as f:
        writer.write(f)
    print('PDF written:', p)

    # Initialize Tk root in withdrawn mode for PhotoImage creation
    print('Starting Tk root...')
    root = tk.Tk()
    root.withdraw()

    pm = PDFManager()
    pid = pm.add_pdf(p)
    pages = pm.get_pages_for_pdf(pid)
    print('Pages found:', pages)

    thumb = PDFViewer.generate_thumbnail_from_path(p, pages[0]['page_index'], width=150, master=root)
    print('thumbnail type:', type(thumb), 'is None?', thumb is None)

except Exception as e:
    print('Error during test:')
    traceback.print_exc()

finally:
    try:
        root.destroy()
    except Exception:
        pass
    print('Done')
