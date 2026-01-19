import fitz
from PyPDF2 import PdfWriter

p = 'test_sample_pix.pdf'
writer = PdfWriter()
writer.add_blank_page(width=595, height=842)
with open(p, 'wb') as f:
    writer.write(f)

try:
    print('Opening with PyMuPDF...')
    doc = fitz.open(p)
    page = doc[0]
    mat = fitz.Matrix(0.2, 0.2)
    pix = page.get_pixmap(matrix=mat)
    try:
        png_bytes = pix.tobytes('png')
    except TypeError:
        png_bytes = pix.getPNGData()
    print('PNG bytes length:', len(png_bytes))
    with open('out_test.png', 'wb') as f:
        f.write(png_bytes)
    print('Wrote out_test.png')
    doc.close()
except Exception as e:
    import traceback
    traceback.print_exc()
