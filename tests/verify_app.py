import traceback
import tkinter as tk
from main import PDFEditorApp
from PyPDF2 import PdfWriter

try:
    print('Creating sample PDF...')
    p = 'sample_for_verify.pdf'
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with open(p, 'wb') as f:
        writer.write(f)
    print('Sample PDF written:', p)

    root = tk.Tk()
    root.withdraw()
    app = PDFEditorApp(root)

    print('Before add: total pages =', app.pdf_manager.get_total_page_count())

    pid = app.pdf_manager.add_pdf(p)
    print('Added PDF id:', pid)
    print('After add: total pages =', app.pdf_manager.get_total_page_count())

    # Refresh UI and let app select and display pages
    app.refresh_pdf_list()

    # Count widgets in page_frame
    children = app.page_frame.winfo_children()
    print('Number of page widgets created:', len(children))

    # Inspect first widget for image reference
    if children:
        child = children[0]
        sub = child.winfo_children()
        print('Child sub-widgets count:', len(sub))
        has_image = any(getattr(w, 'image', None) is not None for w in sub)
        print('First page widget has image:', has_image)

    print('Verification complete')

except Exception as e:
    print('Error during verification:')
    traceback.print_exc()

finally:
    try:
        root.destroy()
    except Exception:
        pass
