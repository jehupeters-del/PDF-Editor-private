"""
PDF Editor - Main Application
A desktop application for loading, viewing, manipulating, and merging PDF files.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional
import threading

from pdf_manager import PDFManager
from pdf_viewer import PDFViewer


class PDFEditorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1200x800")
        
        self.pdf_manager = PDFManager()
        self.selected_pdf_id: Optional[str] = None
        self.selected_pages = set()  # Track selected page widgets
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for PDF list
        self.setup_sidebar(main_frame)
        
        # Right side for page grid
        self.setup_main_area(main_frame)
        
        # Bottom bar for merge button
        self.setup_bottom_bar()
        
    def setup_sidebar(self, parent):
        """Create left sidebar with PDF list"""
        sidebar = ttk.Frame(parent, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        sidebar.pack_propagate(False)
        
        # Title
        title = ttk.Label(sidebar, text="PDF Documents", font=("Arial", 12, "bold"))
        title.pack(pady=(5, 10))
        
        # New and Load buttons
        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(pady=5, fill=tk.X, padx=5)
        
        new_btn = ttk.Button(
            btn_frame,
            text="New",
            command=self.new_project,
            width=9
        )
        new_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        load_btn = ttk.Button(
            btn_frame, 
            text="Load PDFs", 
            command=self.load_pdfs,
            width=9
        )
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        # PDF list
        list_frame = ttk.Frame(sidebar)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for list
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pdf_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=("Arial", 10)
        )
        self.pdf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pdf_listbox.yview)
        
        self.pdf_listbox.bind('<<ListboxSelect>>', self.on_pdf_selected)
        
        # Remove PDF button
        remove_btn = ttk.Button(
            sidebar,
            text="Remove Selected PDF",
            command=self.remove_selected_pdf,
            width=20
        )
        remove_btn.pack(pady=5)
        
    def setup_main_area(self, parent):
        """Create main area for displaying page thumbnails"""
        main_area = ttk.Frame(parent)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title label
        self.main_title = ttk.Label(
            main_area, 
            text="Select a PDF to view pages", 
            font=("Arial", 14, "bold")
        )
        self.main_title.pack(pady=10)
        
        # Canvas with scrollbar for page grid
        canvas_frame = ttk.Frame(main_area)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.page_canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.page_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.page_canvas.yview)
        h_scrollbar.config(command=self.page_canvas.xview)
        
        # Frame inside canvas for page grid
        self.page_frame = ttk.Frame(self.page_canvas)
        self.canvas_window = self.page_canvas.create_window(
            (0, 0), 
            window=self.page_frame, 
            anchor=tk.NW
        )
        
        self.page_frame.bind('<Configure>', self.on_frame_configure)
        self.page_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mousewheel for scrolling - bind to root window for global scroll
        self.root.bind_all('<MouseWheel>', self.on_mousewheel)
        self.root.bind_all('<Button-4>', self.on_mousewheel)  # Linux scroll up
        self.root.bind_all('<Button-5>', self.on_mousewheel)  # Linux scroll down
        
    def setup_bottom_bar(self):
        """Create bottom bar with merge button"""
        bottom_bar = ttk.Frame(self.root)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.page_count_label = ttk.Label(
            bottom_bar, 
            text="0 pages total", 
            font=("Arial", 10)
        )
        self.page_count_label.pack(side=tk.LEFT, padx=10)
        
        self.remove_selected_btn = ttk.Button(
            bottom_bar,
            text="Remove Selected Pages",
            command=self.remove_selected_pages,
            state=tk.DISABLED
        )
        self.remove_selected_btn.pack(side=tk.LEFT, padx=10)
        
        self.merge_btn = ttk.Button(
            bottom_bar,
            text="Merge & Download PDF",
            command=self.merge_pdfs,
            state=tk.DISABLED
        )
        self.merge_btn.pack(side=tk.RIGHT, padx=10)
        
    def on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """Update canvas window width when canvas is resized"""
        canvas_width = event.width
        self.page_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        if event.num == 5 or event.delta < 0:
            self.page_canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.page_canvas.yview_scroll(-1, "units")
            
    def new_project(self):
        """Clear all PDFs and start fresh"""
        if self.pdf_manager.get_total_page_count() > 0:
            if not messagebox.askyesno("Confirm", "Clear all PDFs and start new?"):
                return
                
        # Clear all data
        self.pdf_manager.pdfs.clear()
        self.pdf_manager.all_pages.clear()
        self.selected_pdf_id = None
        self.selected_pages.clear()
        
        # Clear UI
        self.pdf_listbox.delete(0, tk.END)
        for widget in self.page_frame.winfo_children():
            widget.destroy()
        self.main_title.config(text="Select a PDF to view pages")
        self.update_page_count()
        
    def load_pdfs(self):
        """Open file dialog to load PDF files"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
            
        # Load PDFs in background thread
        def load_worker():
            for file_path in file_paths:
                try:
                    self.pdf_manager.add_pdf(file_path)
                except Exception as e:
                    self.root.after(0, lambda msg=str(e), path=file_path: 
                        messagebox.showerror("Error", f"Failed to load {Path(path).name}:\n{msg}"))
            
            self.root.after(0, self.refresh_pdf_list)
            
        thread = threading.Thread(target=load_worker, daemon=True)
        thread.start()
        
    def refresh_pdf_list(self):
        """Refresh the PDF list in the sidebar"""
        self.pdf_listbox.delete(0, tk.END)
        
        for pdf_id, pdf_info in self.pdf_manager.get_all_pdfs().items():
            display_text = f"{pdf_info['name']} ({pdf_info['page_count']} pages)"
            self.pdf_listbox.insert(tk.END, display_text)
            
        self.update_page_count()
        
        # Select first PDF if none selected
        if not self.selected_pdf_id and self.pdf_manager.get_all_pdfs():
            self.pdf_listbox.selection_set(0)
            self.on_pdf_selected()
            
    def on_pdf_selected(self, event=None):
        """Handle PDF selection from listbox"""
        selection = self.pdf_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        pdf_ids = list(self.pdf_manager.get_all_pdfs().keys())
        
        if index < len(pdf_ids):
            self.selected_pdf_id = pdf_ids[index]
            self.display_pages()
            
    def display_pages(self):
        """Display page thumbnails for selected PDF"""
        if not self.selected_pdf_id:
            return
            
        # Clear existing pages
        for widget in self.page_frame.winfo_children():
            widget.destroy()
            
        pdf_info = self.pdf_manager.get_pdf_info(self.selected_pdf_id)
        if not pdf_info:
            return
            
        self.main_title.config(text=f"{pdf_info['name']}")
        
        # Create page thumbnails in grid
        pages = self.pdf_manager.get_pages_for_pdf(self.selected_pdf_id)
        
        # Clear selection
        self.selected_pages.clear()
        
        cols = 5  # Number of columns in grid
        for idx, page in enumerate(pages):
            row = idx // cols
            col = idx % cols
            
            # Pass PDF path to enable thumbnail generation
            page_widget = PDFViewer.create_page_widget(
                self.page_frame,
                page,
                pdf_info['path'],  # Pass the PDF file path
                lambda p=page: self.remove_page(p),
                lambda w=None, p=page: self.toggle_page_selection(w, p)
            )
            page_widget.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
        # Make grid responsive
        for i in range(cols):
            self.page_frame.grid_columnconfigure(i, weight=1)
            
    def remove_page(self, page):
        """Remove a single page"""
        self.pdf_manager.remove_page(page['id'])
        self.display_pages()
        self.update_page_count()
        
    def toggle_page_selection(self, widget, page):
        """Toggle page selection for multi-select"""
        page_id = page['id']
        
        if page_id in self.selected_pages:
            self.selected_pages.remove(page_id)
            widget.configure(relief=tk.RAISED, borderwidth=2)
        else:
            self.selected_pages.add(page_id)
            widget.configure(relief=tk.SUNKEN, borderwidth=4)
            
        self.update_page_count()
            
    def remove_selected_pages(self):
        """Remove all selected pages"""
        if not self.selected_pages:
            return
            
        for page_id in list(self.selected_pages):
            self.pdf_manager.remove_page(page_id)
            
        self.selected_pages.clear()
        self.display_pages()
        self.update_page_count()
            
    def remove_selected_pdf(self):
        """Remove the selected PDF"""
        if not self.selected_pdf_id:
            messagebox.showwarning("Warning", "No PDF selected")
            return
            
        pdf_info = self.pdf_manager.get_pdf_info(self.selected_pdf_id)
        if messagebox.askyesno("Confirm", f"Remove {pdf_info['name']}?"):
            self.pdf_manager.remove_pdf(self.selected_pdf_id)
            self.selected_pdf_id = None
            
            # Clear page display
            for widget in self.page_frame.winfo_children():
                widget.destroy()
            self.main_title.config(text="Select a PDF to view pages")
            
            self.refresh_pdf_list()
            
    def update_page_count(self):
        """Update the total page count label"""
        total_pages = self.pdf_manager.get_total_page_count()
        self.page_count_label.config(text=f"{total_pages} pages total")
        
        # Enable/disable merge button
        if total_pages > 0:
            self.merge_btn.config(state=tk.NORMAL)
        else:
            self.merge_btn.config(state=tk.DISABLED)
            
        # Enable/disable remove selected button
        if self.selected_pages:
            self.remove_selected_btn.config(state=tk.NORMAL)
        else:
            self.remove_selected_btn.config(state=tk.DISABLED)
            
    def merge_pdfs(self):
        """Merge all PDFs and save to file"""
        if self.pdf_manager.get_total_page_count() == 0:
            messagebox.showwarning("Warning", "No pages to merge")
            return
            
        # Ask for save location
        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            initialfile="merged.pdf"
        )
        
        if not output_path:
            return
            
        # Merge in background thread
        def merge_worker():
            try:
                self.pdf_manager.merge_all(output_path)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"PDF saved successfully to:\n{output_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Failed to merge PDFs:\n{str(e)}"
                ))
                
        self.merge_btn.config(state=tk.DISABLED, text="Merging...")
        thread = threading.Thread(target=merge_worker, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(2000, lambda: self.merge_btn.config(
            state=tk.NORMAL, 
            text="Merge & Download PDF"
        ))


def main():
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
