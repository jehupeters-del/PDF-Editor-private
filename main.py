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
        
        # Validation results panel (initially hidden)
        self.validation_panel = None
        self.last_validated_file = None
        
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
        
        # Extraction section
        self.extract_btn = ttk.Button(
            bottom_bar,
            text="✂️ Extract Questions Only",
            command=self.extract_question_pages
        )
        self.extract_btn.pack(side=tk.LEFT, padx=10)
        
        # Validation section
        validation_frame = ttk.Frame(bottom_bar)
        validation_frame.pack(side=tk.RIGHT, padx=10)
        
        self.validate_btn = ttk.Button(
            validation_frame,
            text="📋 Validate Questions",
            command=self.validate_questions
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.merge_btn = ttk.Button(
            validation_frame,
            text="Merge & Download PDF",
            command=self.merge_pdfs,
            state=tk.DISABLED
        )
        self.merge_btn.pack(side=tk.LEFT)
        
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
    
    def extract_question_pages(self):
        """Extract only pages with question numbers - offers single or batch mode"""
        # Ask user: single or multiple PDFs?
        choice = messagebox.askyesnocancel(
            "Extraction Mode",
            "Do you want to extract from multiple PDFs?\n\n"
            "Yes = Select multiple PDFs (batch)\n"
            "No = Select single PDF\n"
            "Cancel = Go back"
        )
        
        if choice is None:  # Cancelled
            return
        elif choice:  # Yes - batch extraction
            self.extract_batch()
        else:  # No - single extraction
            self.extract_single()
    
    def extract_single(self):
        """Extract questions from a single PDF"""
        # Select input PDF
        input_path = filedialog.askopenfilename(
            title="Select PDF to Extract Questions From",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not input_path:
            return
        
        # Generate smart filename
        smart_name = self.pdf_manager.generate_smart_filename(Path(input_path).name)
        
        # Select output location
        output_path = filedialog.asksaveasfilename(
            title="Save Extracted Questions PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            initialfile=smart_name
        )
        
        if not output_path:
            return
        
        # Run extraction in background thread
        def extract_worker():
            try:
                result = self.pdf_manager.extract_question_pages(input_path, output_path)
                orig_pages, new_pages, questions, is_valid, missing, max_q = result
                
                self.root.after(0, lambda: self.show_extraction_results(
                    input_path, output_path, orig_pages, new_pages, 
                    questions, is_valid, missing, max_q
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Extraction Error",
                    f"Failed to extract question pages:\n{str(e)}"
                ))
        
        # Show loading state
        self.extract_btn.config(state=tk.DISABLED, text="Extracting...")
        thread = threading.Thread(target=extract_worker, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(3000, lambda: self.extract_btn.config(
            state=tk.NORMAL,
            text="✂️ Extract Questions Only"
        ))
    
    def extract_batch(self):
        """Extract questions from multiple PDFs at once"""
        # Select input PDFs
        input_paths = filedialog.askopenfilenames(
            title="Select PDFs to Extract Questions From (Multiple Selection)",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not input_paths:
            return
        
        # Select output folder
        output_folder = filedialog.askdirectory(
            title="Select Output Folder for Extracted PDFs"
        )
        
        if not output_folder:
            return
        
        # Run batch extraction in background thread
        def batch_extract_worker():
            results = []
            
            for input_path in input_paths:
                # Generate smart output filename
                smart_name = self.pdf_manager.generate_smart_filename(Path(input_path).name)
                output_path = Path(output_folder) / smart_name
                
                try:
                    result = self.pdf_manager.extract_question_pages(input_path, str(output_path))
                    orig_pages, new_pages, questions, is_valid, missing, max_q = result
                    
                    results.append({
                        'input_path': input_path,
                        'input_name': Path(input_path).name,
                        'output_path': str(output_path),
                        'output_name': smart_name,
                        'orig_pages': orig_pages,
                        'new_pages': new_pages,
                        'questions': questions,
                        'is_valid': is_valid,
                        'missing': missing,
                        'max_question': max_q,
                        'error': None
                    })
                except Exception as e:
                    results.append({
                        'input_path': input_path,
                        'input_name': Path(input_path).name,
                        'output_path': '',
                        'output_name': '',
                        'orig_pages': 0,
                        'new_pages': 0,
                        'questions': [],
                        'is_valid': False,
                        'missing': [],
                        'max_question': 0,
                        'error': str(e)
                    })
            
            self.root.after(0, lambda: self.show_batch_extraction_results(results, output_folder))
        
        # Show loading state
        self.extract_btn.config(state=tk.DISABLED, text=f"Extracting {len(input_paths)} PDFs...")
        thread = threading.Thread(target=batch_extract_worker, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(5000, lambda: self.extract_btn.config(
            state=tk.NORMAL,
            text="✂️ Extract Questions Only"
        ))
    
    def show_extraction_results(self, input_path, output_path, orig_pages, 
                                new_pages, questions, is_valid, missing, max_q):
        """Display extraction results in a popup window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Question Extraction Results")
        results_window.geometry("700x600")
        results_window.transient(self.root)
        
        # Main frame
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            main_frame,
            text="✂️ Question Pages Extracted",
            font=("Arial", 16, "bold")
        )
        header_label.pack(pady=(0, 20))
        
        # File info
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        source_label = ttk.Label(
            info_frame,
            text=f"Source: {Path(input_path).name}",
            font=("Arial", 10)
        )
        source_label.pack(anchor=tk.W, pady=2)
        
        output_label = ttk.Label(
            info_frame,
            text=f"Output: {Path(output_path).name}",
            font=("Arial", 10)
        )
        output_label.pack(anchor=tk.W, pady=2)
        
        location_label = ttk.Label(
            info_frame,
            text=f"Saved to: {Path(output_path).parent}",
            font=("Arial", 9),
            foreground="gray"
        )
        location_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Extraction statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Extraction Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Pages reduced
        reduction = orig_pages - new_pages
        reduction_pct = (reduction / orig_pages * 100) if orig_pages > 0 else 0
        
        pages_label = ttk.Label(
            stats_frame,
            text=f"Pages: {orig_pages} → {new_pages} (removed {reduction} pages, {reduction_pct:.1f}% reduction)",
            font=("Arial", 11, "bold"),
            foreground="blue"
        )
        pages_label.pack(anchor=tk.W, pady=5)
        
        questions_label = ttk.Label(
            stats_frame,
            text=f"Questions found: {len(questions)} unique ({min(questions)} to {max(questions)})",
            font=("Arial", 10)
        )
        questions_label.pack(anchor=tk.W, pady=2)
        
        # List of extracted questions
        questions_list_label = ttk.Label(
            stats_frame,
            text=f"Question numbers: {self.format_number_list(questions)}",
            font=("Arial", 9),
            foreground="gray",
            wraplength=600
        )
        questions_list_label.pack(anchor=tk.W, pady=2)
        
        # Validation results
        validation_frame = ttk.LabelFrame(main_frame, text="Validation Check", padding=15)
        validation_frame.pack(fill=tk.X, pady=(0, 15))
        
        if is_valid:
            # Success
            icon_label = ttk.Label(validation_frame, text="✅", font=("Arial", 32))
            icon_label.pack(pady=5)
            
            status_label = ttk.Label(
                validation_frame,
                text="All questions present and accounted for!",
                font=("Arial", 12, "bold"),
                foreground="green"
            )
            status_label.pack(pady=5)
            
            detail_label = ttk.Label(
                validation_frame,
                text=f"No questions were lost during extraction. Questions 1-{max_q} all present.",
                font=("Arial", 10)
            )
            detail_label.pack(pady=2)
        else:
            # Warning - missing questions
            icon_label = ttk.Label(validation_frame, text="⚠️", font=("Arial", 32))
            icon_label.pack(pady=5)
            
            status_label = ttk.Label(
                validation_frame,
                text=f"WARNING: {len(missing)} question(s) missing!",
                font=("Arial", 12, "bold"),
                foreground="red"
            )
            status_label.pack(pady=5)
            
            detail_label = ttk.Label(
                validation_frame,
                text=f"Expected: 1-{max_q}  |  Missing: {', '.join(str(m) for m in missing[:20])}{'...' if len(missing) > 20 else ''}",
                font=("Arial", 10),
                foreground="red"
            )
            detail_label.pack(pady=2)
            
            note_label = ttk.Label(
                validation_frame,
                text="Some pages may not have had question numbers, or questions may be out of sequence.",
                font=("Arial", 9),
                foreground="gray",
                wraplength=600
            )
            note_label.pack(pady=(5, 2))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Open folder button
        open_folder_btn = ttk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=lambda: self.open_folder(Path(output_path).parent),
            width=20
        )
        open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=results_window.destroy,
            width=15
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")
    
    def format_number_list(self, numbers):
        """Format a list of numbers compactly"""
        if not numbers:
            return "None"
        if len(numbers) <= 30:
            return ", ".join(str(n) for n in numbers)
        else:
            first_20 = ", ".join(str(n) for n in numbers[:20])
            return f"{first_20}, ... and {len(numbers) - 20} more"
    
    def open_folder(self, folder_path):
        """Open a folder in the system file explorer"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                subprocess.run(['explorer', str(folder_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', str(folder_path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(folder_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
    
    def show_batch_extraction_results(self, results, output_folder):
        """Display batch extraction results in a comprehensive window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Batch Extraction Results - {len(results)} PDFs")
        results_window.geometry("900x700")
        results_window.transient(self.root)
        
        # Main frame with padding
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(
            header_frame,
            text=f"✂️ Batch Extraction Results - {len(results)} PDF(s)",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Summary statistics
        success_count = sum(1 for r in results if not r['error'])
        error_count = sum(1 for r in results if r['error'])
        valid_count = sum(1 for r in results if r['is_valid'] and not r['error'])
        warning_count = sum(1 for r in results if not r['is_valid'] and not r['error'])
        
        summary_label = ttk.Label(
            header_frame,
            text=f"✅ {success_count} Success  |  ✅ {valid_count} Valid  |  ⚠️ {warning_count} Warnings  |  ❌ {error_count} Errors",
            font=("Arial", 9)
        )
        summary_label.pack(side=tk.RIGHT)
        
        # Output folder info
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        folder_label = ttk.Label(
            folder_frame,
            text=f"Output folder: {output_folder}",
            font=("Arial", 10),
            foreground="gray"
        )
        folder_label.pack(side=tk.LEFT)
        
        open_folder_btn = ttk.Button(
            folder_frame,
            text="📁 Open Folder",
            command=lambda: self.open_folder(output_folder),
            width=15
        )
        open_folder_btn.pack(side=tk.RIGHT)
        
        # Scrollable results area
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display each result
        for idx, result in enumerate(results):
            self.create_extraction_card(scrollable_frame, result, idx)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=results_window.destroy,
            width=15
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def create_extraction_card(self, parent, result, index):
        """Create a card displaying extraction result for one PDF"""
        # Card frame with border
        card = ttk.LabelFrame(
            parent,
            text=f"#{index + 1}: {result['input_name']}",
            padding=15
        )
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Content frame
        content = ttk.Frame(card)
        content.pack(fill=tk.BOTH, expand=True)
        
        if result['error']:
            # Error case
            icon_label = ttk.Label(content, text="❌", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(
                info_frame,
                text="Extraction failed",
                font=("Arial", 11, "bold"),
                foreground="red"
            )
            status_label.pack(anchor=tk.W)
            
            error_label = ttk.Label(
                info_frame,
                text=f"Error: {result['error']}",
                font=("Arial", 9),
                foreground="gray",
                wraplength=700
            )
            error_label.pack(anchor=tk.W, pady=(2, 0))
            
        else:
            # Success case
            if result['is_valid']:
                icon_label = ttk.Label(content, text="✅", font=("Arial", 24))
            else:
                icon_label = ttk.Label(content, text="⚠️", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Output filename
            output_label = ttk.Label(
                info_frame,
                text=f"→ {result['output_name']}",
                font=("Arial", 11, "bold"),
                foreground="blue"
            )
            output_label.pack(anchor=tk.W)
            
            # Statistics
            reduction = result['orig_pages'] - result['new_pages']
            reduction_pct = (reduction / result['orig_pages'] * 100) if result['orig_pages'] > 0 else 0
            
            stats_text = f"Pages: {result['orig_pages']} → {result['new_pages']} (removed {reduction}, {reduction_pct:.1f}% reduction)"
            if result['questions']:
                stats_text += f"  |  Questions: {min(result['questions'])}-{max(result['questions'])}"
            
            stats_label = ttk.Label(
                info_frame,
                text=stats_text,
                font=("Arial", 9),
                foreground="gray"
            )
            stats_label.pack(anchor=tk.W, pady=(2, 0))
            
            # Validation status
            if result['is_valid']:
                validation_label = ttk.Label(
                    info_frame,
                    text="✓ All questions present",
                    font=("Arial", 9),
                    foreground="green"
                )
                validation_label.pack(anchor=tk.W, pady=(2, 0))
            else:
                validation_label = ttk.Label(
                    info_frame,
                    text=f"⚠ Missing {len(result['missing'])} question(s): {', '.join(str(m) for m in result['missing'][:10])}{'...' if len(result['missing']) > 10 else ''}",
                    font=("Arial", 9),
                    foreground="orange"
                )
                validation_label.pack(anchor=tk.W, pady=(2, 0))
    
    def validate_questions(self):
        """Validate question continuity - offers single or batch mode"""
        # Ask user: single or multiple PDFs?
        choice = messagebox.askyesnocancel(
            "Validation Mode",
            "Do you want to validate multiple PDFs?\n\n"
            "Yes = Select multiple PDFs\n"
            "No = Select single PDF\n"
            "Cancel = Go back"
        )
        
        if choice is None:  # Cancelled
            return
        elif choice:  # Yes - batch validation
            self.validate_batch()
        else:  # No - single validation
            self.validate_single()
    
    def validate_single(self):
        """Validate a single PDF"""
        file_path = filedialog.askopenfilename(
            title="Select PDF to Validate Questions",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Run validation in background thread
        def validate_worker():
            try:
                is_valid, missing, max_q = self.pdf_manager.validate_question_continuity(file_path)
                self.root.after(0, lambda: self.show_validation_results(
                    file_path, is_valid, missing, max_q
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Validation Error",
                    f"Failed to validate PDF:\n{str(e)}"
                ))
        
        # Show loading state
        self.validate_btn.config(state=tk.DISABLED, text="Validating...")
        thread = threading.Thread(target=validate_worker, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(2000, lambda: self.validate_btn.config(
            state=tk.NORMAL,
            text="📋 Validate Questions"
        ))
    
    def validate_batch(self):
        """Validate multiple PDFs at once"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDFs to Validate (Multiple Selection)",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
        
        # Run batch validation in background thread
        def batch_validate_worker():
            results = []
            
            for file_path in file_paths:
                try:
                    is_valid, missing, max_q = self.pdf_manager.validate_question_continuity(file_path)
                    results.append({
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'is_valid': is_valid,
                        'missing': missing,
                        'max_question': max_q,
                        'error': None
                    })
                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'is_valid': False,
                        'missing': [],
                        'max_question': 0,
                        'error': str(e)
                    })
            
            self.root.after(0, lambda: self.show_batch_validation_results(results))
        
        # Show loading state
        self.validate_btn.config(state=tk.DISABLED, text=f"Validating {len(file_paths)} PDFs...")
        thread = threading.Thread(target=batch_validate_worker, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(3000, lambda: self.validate_btn.config(
            state=tk.NORMAL,
            text="📋 Validate Questions"
        ))
    
    def show_validation_results(self, file_path, is_valid, missing, max_question):
        """Display validation results in a popup window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Question Validation Results")
        results_window.geometry("600x500")
        results_window.transient(self.root)
        
        # Main frame
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File name
        file_label = ttk.Label(
            main_frame,
            text=f"File: {Path(file_path).name}",
            font=("Arial", 11, "bold")
        )
        file_label.pack(pady=(0, 15))
        
        # Results section
        if max_question == 0:
            # No questions found
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(pady=10, fill=tk.X)
            
            icon_label = ttk.Label(
                status_frame,
                text="ℹ️",
                font=("Arial", 48)
            )
            icon_label.pack()
            
            message_label = ttk.Label(
                status_frame,
                text="No questions found in this PDF",
                font=("Arial", 12)
            )
            message_label.pack(pady=10)
            
            info_label = ttk.Label(
                status_frame,
                text='The validator searches for the pattern "Question {number}"\nin the PDF text.',
                font=("Arial", 10),
                foreground="gray"
            )
            info_label.pack()
            
        elif is_valid:
            # All questions present
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(pady=10, fill=tk.X)
            
            icon_label = ttk.Label(
                status_frame,
                text="✅",
                font=("Arial", 48)
            )
            icon_label.pack()
            
            message_label = ttk.Label(
                status_frame,
                text="All questions present!",
                font=("Arial", 14, "bold"),
                foreground="green"
            )
            message_label.pack(pady=10)
            
            range_label = ttk.Label(
                status_frame,
                text=f"Questions 1 to {max_question} are all accounted for.",
                font=("Arial", 11)
            )
            range_label.pack()
            
            total_label = ttk.Label(
                status_frame,
                text=f"Total questions: {max_question}",
                font=("Arial", 10),
                foreground="gray"
            )
            total_label.pack(pady=5)
            
        else:
            # Missing questions detected
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(pady=10, fill=tk.X)
            
            icon_label = ttk.Label(
                status_frame,
                text="⚠️",
                font=("Arial", 48)
            )
            icon_label.pack()
            
            message_label = ttk.Label(
                status_frame,
                text="Missing Questions Detected!",
                font=("Arial", 14, "bold"),
                foreground="red"
            )
            message_label.pack(pady=10)
            
            stats_frame = ttk.Frame(status_frame)
            stats_frame.pack(pady=10)
            
            expected_label = ttk.Label(
                stats_frame,
                text=f"Expected range: 1 to {max_question}",
                font=("Arial", 10)
            )
            expected_label.pack()
            
            missing_count_label = ttk.Label(
                stats_frame,
                text=f"Missing: {len(missing)} question(s)",
                font=("Arial", 10, "bold"),
                foreground="red"
            )
            missing_count_label.pack(pady=5)
            
            # Special warning for missing Question 1
            if 1 in missing:
                warning_label = ttk.Label(
                    stats_frame,
                    text="⚠️ Critical: Question 1 is missing!",
                    font=("Arial", 9, "bold"),
                    foreground="orange"
                )
                warning_label.pack(pady=5)
            
            # Missing questions list
            list_label = ttk.Label(
                main_frame,
                text="Missing Question Numbers:",
                font=("Arial", 10, "bold")
            )
            list_label.pack(pady=(15, 5), anchor=tk.W)
            
            # Scrollable text widget for missing numbers
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            missing_text = tk.Text(
                text_frame,
                height=10,
                font=("Arial", 10),
                yscrollcommand=scrollbar.set,
                wrap=tk.WORD,
                relief=tk.SUNKEN,
                borderwidth=2
            )
            missing_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=missing_text.yview)
            
            # Format missing numbers in columns
            missing_str = self.format_missing_numbers(missing)
            missing_text.insert("1.0", missing_str)
            missing_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=results_window.destroy,
            width=15
        )
        close_btn.pack(pady=(20, 0))
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")
    
    def format_missing_numbers(self, missing):
        """Format missing numbers into columns for display"""
        if not missing:
            return "None"
        
        # Group numbers into rows of 10
        result = []
        for i in range(0, len(missing), 10):
            row = missing[i:i+10]
            row_str = ", ".join(str(num) for num in row)
            result.append(row_str)
        
        return "\n".join(result)
    
    def show_batch_validation_results(self, results):
        """Display batch validation results in a comprehensive window"""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Batch Validation Results - {len(results)} PDFs")
        results_window.geometry("900x700")
        results_window.transient(self.root)
        
        # Main frame with padding
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(
            header_frame,
            text=f"Validation Results for {len(results)} PDF(s)",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Summary statistics
        valid_count = sum(1 for r in results if r['is_valid'] and not r['error'])
        invalid_count = sum(1 for r in results if not r['is_valid'] and not r['error'])
        error_count = sum(1 for r in results if r['error'])
        
        summary_label = ttk.Label(
            header_frame,
            text=f"✅ {valid_count} Valid  |  ⚠️ {invalid_count} Issues  |  ❌ {error_count} Errors",
            font=("Arial", 10)
        )
        summary_label.pack(side=tk.RIGHT)
        
        # Scrollable results area
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display each result
        for idx, result in enumerate(results):
            self.create_result_card(scrollable_frame, result, idx)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Export button
        export_btn = ttk.Button(
            button_frame,
            text="💾 Export to Text File",
            command=lambda: self.export_batch_results(results),
            width=20
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy to clipboard button
        copy_btn = ttk.Button(
            button_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self.copy_batch_results(results),
            width=20
        )
        copy_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=results_window.destroy,
            width=15
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def create_result_card(self, parent, result, index):
        """Create a card displaying validation result for one PDF"""
        # Card frame with border
        card = ttk.LabelFrame(
            parent,
            text=f"#{index + 1}: {result['file_name']}",
            padding=15
        )
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Content frame
        content = ttk.Frame(card)
        content.pack(fill=tk.BOTH, expand=True)
        
        if result['error']:
            # Error case
            icon_label = ttk.Label(content, text="❌", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(
                info_frame,
                text="Error during validation",
                font=("Arial", 11, "bold"),
                foreground="red"
            )
            status_label.pack(anchor=tk.W)
            
            error_label = ttk.Label(
                info_frame,
                text=f"Error: {result['error']}",
                font=("Arial", 9),
                foreground="gray"
            )
            error_label.pack(anchor=tk.W, pady=(2, 0))
            
        elif result['max_question'] == 0:
            # No questions found
            icon_label = ttk.Label(content, text="ℹ️", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(
                info_frame,
                text="No questions found",
                font=("Arial", 11),
                foreground="gray"
            )
            status_label.pack(anchor=tk.W)
            
        elif result['is_valid']:
            # Valid - all questions present
            icon_label = ttk.Label(content, text="✅", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(
                info_frame,
                text=f"All questions present (1-{result['max_question']})",
                font=("Arial", 11, "bold"),
                foreground="green"
            )
            status_label.pack(anchor=tk.W)
            
            count_label = ttk.Label(
                info_frame,
                text=f"Total: {result['max_question']} questions",
                font=("Arial", 9),
                foreground="gray"
            )
            count_label.pack(anchor=tk.W, pady=(2, 0))
            
        else:
            # Invalid - missing questions
            icon_label = ttk.Label(content, text="⚠️", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            info_frame = ttk.Frame(content)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            status_label = ttk.Label(
                info_frame,
                text=f"Missing {len(result['missing'])} question(s)",
                font=("Arial", 11, "bold"),
                foreground="red"
            )
            status_label.pack(anchor=tk.W)
            
            range_label = ttk.Label(
                info_frame,
                text=f"Expected: 1-{result['max_question']}  |  Missing: {self.format_missing_list_compact(result['missing'])}",
                font=("Arial", 9),
                foreground="gray"
            )
            range_label.pack(anchor=tk.W, pady=(2, 0))
            
            # Special warning for missing Q1
            if 1 in result['missing']:
                warning_label = ttk.Label(
                    info_frame,
                    text="⚠️ Critical: Question 1 missing!",
                    font=("Arial", 9, "bold"),
                    foreground="orange"
                )
                warning_label.pack(anchor=tk.W, pady=(2, 0))
    
    def format_missing_list_compact(self, missing):
        """Format missing numbers compactly for card display"""
        if not missing:
            return "None"
        if len(missing) <= 10:
            return ", ".join(str(n) for n in missing)
        else:
            # Show first 10 and indicate there are more
            first_ten = ", ".join(str(n) for n in missing[:10])
            return f"{first_ten}, ... ({len(missing)} total)"
    
    def export_batch_results(self, results):
        """Export batch validation results to a text file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Validation Results",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"validation_results_{len(results)}_pdfs.txt"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"PDF QUESTION VALIDATION REPORT\n")
                f.write(f"Generated: {Path(file_path).name}\n")
                f.write(f"Total PDFs Validated: {len(results)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Summary
                valid_count = sum(1 for r in results if r['is_valid'] and not r['error'])
                invalid_count = sum(1 for r in results if not r['is_valid'] and not r['error'])
                error_count = sum(1 for r in results if r['error'])
                
                f.write("SUMMARY:\n")
                f.write(f"  ✓ Valid: {valid_count}\n")
                f.write(f"  ⚠ Issues Found: {invalid_count}\n")
                f.write(f"  ✗ Errors: {error_count}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                
                # Individual results
                for idx, result in enumerate(results, 1):
                    f.write(f"[{idx}] {result['file_name']}\n")
                    f.write(f"    Path: {result['file_path']}\n")
                    
                    if result['error']:
                        f.write(f"    Status: ERROR\n")
                        f.write(f"    Error: {result['error']}\n")
                    elif result['max_question'] == 0:
                        f.write(f"    Status: NO QUESTIONS FOUND\n")
                    elif result['is_valid']:
                        f.write(f"    Status: VALID ✓\n")
                        f.write(f"    Questions: 1 to {result['max_question']} (all present)\n")
                        f.write(f"    Total: {result['max_question']} questions\n")
                    else:
                        f.write(f"    Status: INVALID ⚠\n")
                        f.write(f"    Expected Range: 1 to {result['max_question']}\n")
                        f.write(f"    Missing Count: {len(result['missing'])}\n")
                        f.write(f"    Missing Questions: {', '.join(str(n) for n in result['missing'])}\n")
                        if 1 in result['missing']:
                            f.write(f"    WARNING: Question 1 is missing!\n")
                    
                    f.write("\n" + "-" * 80 + "\n\n")
            
            messagebox.showinfo(
                "Export Successful",
                f"Results exported to:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Failed to export results:\n{str(e)}"
            )
    
    def copy_batch_results(self, results):
        """Copy batch validation results to clipboard"""
        try:
            # Generate text summary
            text = f"PDF QUESTION VALIDATION RESULTS ({len(results)} PDFs)\n"
            text += "=" * 60 + "\n\n"
            
            for idx, result in enumerate(results, 1):
                text += f"{idx}. {result['file_name']}\n"
                
                if result['error']:
                    text += f"   ERROR: {result['error']}\n"
                elif result['max_question'] == 0:
                    text += f"   No questions found\n"
                elif result['is_valid']:
                    text += f"   ✓ Valid: Questions 1-{result['max_question']}\n"
                else:
                    text += f"   ⚠ Missing {len(result['missing'])}: {', '.join(str(n) for n in result['missing'][:20])}{'...' if len(result['missing']) > 20 else ''}\n"
                
                text += "\n"
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            
            messagebox.showinfo(
                "Copied",
                f"Results for {len(results)} PDFs copied to clipboard!"
            )
        except Exception as e:
            messagebox.showerror(
                "Copy Error",
                f"Failed to copy to clipboard:\n{str(e)}"
            )


def main():
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
