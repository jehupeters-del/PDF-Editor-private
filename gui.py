"""
PDF Editor - Local GUI Application

A clean desktop interface for PDF manipulation:
  - Merge multiple PDFs
  - Extract question pages (single / batch)
  - Validate question continuity (single / batch)
  - View PDF info and smart-rename files

Launch:  python gui.py
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from pdf_manager import PDFManager
from pdf_viewer import PDFViewer


# ── Colour palette ──────────────────────────────────────────────────────────
BG       = "#f5f5f5"
CARD_BG  = "#ffffff"
ACCENT   = "#2563eb"
SUCCESS  = "#16a34a"
FAIL     = "#dc2626"
MUTED    = "#6b7280"


# ═════════════════════════════════════════════════════════════════════════════
#  Main Application
# ═════════════════════════════════════════════════════════════════════════════

class PDFEditorGUI:
    """Lightweight tabbed GUI wrapping PDFManager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("820x620")
        self.root.minsize(700, 500)
        self.root.configure(bg=BG)

        # Shared PDFManager for the Merge tab (others create their own)
        self.manager = PDFManager()

        self._apply_styles()
        self._build_ui()

    # ── Styles ──────────────────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", padding=[14, 6], font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", CARD_BG), ("!selected", "#e5e7eb")],
                  foreground=[("selected", ACCENT)])

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD_BG, relief="solid", borderwidth=1)
        style.configure("TLabel", background=BG, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Sub.TLabel", foreground=MUTED, font=("Segoe UI", 9))

        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=[10, 4])

    # ── Layout ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=16, pady=(12, 4))
        ttk.Label(title_frame, text="PDF Editor", style="Header.TLabel").pack(side="left")
        ttk.Label(title_frame, text="Merge · Extract · Validate · Info",
                  style="Sub.TLabel").pack(side="left", padx=12)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self._build_merge_tab()
        self._build_extract_tab()
        self._build_validate_tab()
        self._build_info_tab()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 1 — Merge
    # ════════════════════════════════════════════════════════════════════════
    def _build_merge_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Merge  ")

        # --- top controls ---
        ctrl = ttk.Frame(tab)
        ctrl.pack(fill="x")
        ttk.Button(ctrl, text="Add PDFs…", command=self._merge_add).pack(side="left")
        ttk.Button(ctrl, text="Remove Selected", command=self._merge_remove).pack(side="left", padx=6)
        ttk.Button(ctrl, text="▲ Up", width=5, command=lambda: self._merge_move(-1)).pack(side="left")
        ttk.Button(ctrl, text="▼ Down", width=5, command=lambda: self._merge_move(1)).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Clear All", command=self._merge_clear).pack(side="left")

        # --- file list ---
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill="both", expand=True, pady=8)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.merge_listbox = tk.Listbox(
            list_frame, font=("Segoe UI", 10), selectmode="extended",
            activestyle="none", bg=CARD_BG, relief="solid", bd=1,
            yscrollcommand=scrollbar.set,
        )
        self.merge_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.merge_listbox.yview)

        # Internal parallel list of (pdf_id, display_text, path)
        self.merge_items: list = []

        # --- bottom bar ---
        bot = ttk.Frame(tab)
        bot.pack(fill="x")
        self.merge_status = ttk.Label(bot, text="No files loaded", style="Sub.TLabel")
        self.merge_status.pack(side="left")
        ttk.Button(bot, text="Merge & Save…", style="Accent.TButton",
                   command=self._merge_save).pack(side="right")

    def _merge_refresh_list(self):
        self.merge_listbox.delete(0, "end")
        for _, display, _ in self.merge_items:
            self.merge_listbox.insert("end", display)
        total = sum(
            self.manager.get_pdf_info(pid)["page_count"]
            for pid, _, _ in self.merge_items
            if self.manager.get_pdf_info(pid)
        )
        n = len(self.merge_items)
        self.merge_status.config(text=f"{n} file{'s' if n != 1 else ''}, {total} total pages")

    def _merge_add(self):
        paths = filedialog.askopenfilenames(
            title="Select PDFs to merge",
            filetypes=[("PDF files", "*.pdf")],
        )
        for p in paths:
            try:
                pid = self.manager.add_pdf(p)
                info = self.manager.get_pdf_info(pid)
                display = f"{info['name']}  ({info['page_count']} pages)"
                self.merge_items.append((pid, display, p))
            except Exception as e:
                messagebox.showerror("Error", f"Could not load {Path(p).name}:\n{e}")
        self._merge_refresh_list()

    def _merge_remove(self):
        sel = list(self.merge_listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            pid, _, _ = self.merge_items.pop(idx)
            self.manager.remove_pdf(pid)
        self._merge_refresh_list()

    def _merge_move(self, direction: int):
        sel = list(self.merge_listbox.curselection())
        if len(sel) != 1:
            return
        idx = sel[0]
        new = idx + direction
        if 0 <= new < len(self.merge_items):
            self.merge_items[idx], self.merge_items[new] = self.merge_items[new], self.merge_items[idx]
            # Also reorder the pages inside PDFManager so merge_all respects order
            all_pages = []
            for pid, _, _ in self.merge_items:
                all_pages.extend(self.manager.get_pages_for_pdf(pid))
            self.manager.all_pages = all_pages
            self._merge_refresh_list()
            self.merge_listbox.selection_set(new)

    def _merge_clear(self):
        for pid, _, _ in self.merge_items:
            self.manager.remove_pdf(pid)
        self.merge_items.clear()
        self._merge_refresh_list()

    def _merge_save(self):
        if not self.merge_items:
            messagebox.showinfo("Merge", "Add at least one PDF first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged.pdf",
        )
        if not path:
            return
        try:
            self.manager.merge_all(path)
            messagebox.showinfo("Merge", f"Saved merged PDF:\n{path}")
        except Exception as e:
            messagebox.showerror("Merge Error", str(e))

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 2 — Extract
    # ════════════════════════════════════════════════════════════════════════
    def _build_extract_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Extract  ")

        ttk.Label(tab, text="Extract question pages from PDFs",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Keeps the title page + every page containing \"Question N\"",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        # Controls
        ctrl = ttk.Frame(tab)
        ctrl.pack(fill="x")
        ttk.Button(ctrl, text="Select PDFs…", command=self._extract_pick).pack(side="left")
        self.extract_outdir_var = tk.StringVar()
        ttk.Button(ctrl, text="Output Folder…", command=self._extract_outdir).pack(side="left", padx=6)
        self.extract_outdir_label = ttk.Label(ctrl, text="(same as source)", style="Sub.TLabel")
        self.extract_outdir_label.pack(side="left")

        # Results
        self.extract_text = self._scrolled_text(tab)

        # Run button
        bot = ttk.Frame(tab)
        bot.pack(fill="x")
        self.extract_files: list = []
        self.extract_status = ttk.Label(bot, text="No files selected", style="Sub.TLabel")
        self.extract_status.pack(side="left")
        ttk.Button(bot, text="Extract All", style="Accent.TButton",
                   command=self._extract_run).pack(side="right")

    def _extract_pick(self):
        paths = filedialog.askopenfilenames(
            title="Select PDFs to extract", filetypes=[("PDF files", "*.pdf")]
        )
        if paths:
            self.extract_files = list(paths)
            self.extract_status.config(text=f"{len(paths)} file{'s' if len(paths) != 1 else ''} selected")
            self.extract_text.delete("1.0", "end")

    def _extract_outdir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.extract_outdir_var.set(d)
            self.extract_outdir_label.config(text=d)

    def _extract_run(self):
        if not self.extract_files:
            messagebox.showinfo("Extract", "Select PDFs first.")
            return
        self.extract_text.delete("1.0", "end")
        self._run_threaded(self._extract_work)

    def _extract_work(self):
        mgr = PDFManager()
        out_dir = self.extract_outdir_var.get() or None
        for fp in self.extract_files:
            name = Path(fp).name
            smart = PDFManager.generate_smart_filename(name)
            if out_dir:
                out_path = str(Path(out_dir) / smart)
            else:
                out_path = str(Path(fp).parent / smart)
            try:
                orig, ext, questions, valid, missing, max_q = mgr.extract_question_pages(fp, out_path)
                status = "PASS" if valid else f"FAIL — missing {missing}"
                line = f"✓  {name}:  {orig} → {ext} pages  |  Q1–{max_q}  |  {status}\n   → {out_path}\n\n"
            except Exception as e:
                line = f"✗  {name}:  ERROR — {e}\n\n"
            self._append(self.extract_text, line)
        self._append(self.extract_text, "— Done —\n")

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 3 — Validate
    # ════════════════════════════════════════════════════════════════════════
    def _build_validate_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Validate  ")

        ttk.Label(tab, text="Validate question continuity",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Checks that questions 1 through N are all present in each PDF",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill="x")
        ttk.Button(ctrl, text="Select PDFs…", command=self._validate_pick).pack(side="left")

        self.validate_text = self._scrolled_text(tab)

        bot = ttk.Frame(tab)
        bot.pack(fill="x")
        self.validate_files: list = []
        self.validate_status = ttk.Label(bot, text="No files selected", style="Sub.TLabel")
        self.validate_status.pack(side="left")
        ttk.Button(bot, text="Validate All", style="Accent.TButton",
                   command=self._validate_run).pack(side="right")

    def _validate_pick(self):
        paths = filedialog.askopenfilenames(
            title="Select PDFs to validate", filetypes=[("PDF files", "*.pdf")]
        )
        if paths:
            self.validate_files = list(paths)
            self.validate_status.config(text=f"{len(paths)} file{'s' if len(paths) != 1 else ''} selected")
            self.validate_text.delete("1.0", "end")

    def _validate_run(self):
        if not self.validate_files:
            messagebox.showinfo("Validate", "Select PDFs first.")
            return
        self.validate_text.delete("1.0", "end")
        self._run_threaded(self._validate_work)

    def _validate_work(self):
        mgr = PDFManager()
        passes = fails = 0
        for fp in self.validate_files:
            name = Path(fp).name
            try:
                valid, missing, max_q = mgr.validate_question_continuity(fp)
                if max_q == 0:
                    line = f"—  {name}:  no questions found\n"
                elif valid:
                    line = f"✓  {name}:  PASS  (Q1–{max_q})\n"
                    passes += 1
                else:
                    line = f"✗  {name}:  FAIL — missing {missing}\n"
                    fails += 1
            except Exception as e:
                line = f"✗  {name}:  ERROR — {e}\n"
                fails += 1
            self._append(self.validate_text, line)
        self._append(self.validate_text, f"\n— Done: {passes} passed, {fails} failed —\n")

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 4 — Info / Rename
    # ════════════════════════════════════════════════════════════════════════
    def _build_info_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Info / Rename  ")

        ttk.Label(tab, text="PDF information & smart rename",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="View page count, detected questions, and generate smart filenames",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill="x")
        ttk.Button(ctrl, text="Select PDF…", command=self._info_pick).pack(side="left")
        ttk.Button(ctrl, text="Generate Thumbnail…", command=self._info_thumbnail).pack(side="left", padx=6)

        self.info_text = self._scrolled_text(tab)

        bot = ttk.Frame(tab)
        bot.pack(fill="x")
        self.info_file: str = ""
        self.info_status = ttk.Label(bot, text="No file selected", style="Sub.TLabel")
        self.info_status.pack(side="left")
        ttk.Button(bot, text="Apply Rename", style="Accent.TButton",
                   command=self._info_rename).pack(side="right")

    def _info_pick(self):
        path = filedialog.askopenfilename(
            title="Select a PDF", filetypes=[("PDF files", "*.pdf")]
        )
        if not path:
            return
        self.info_file = path
        self.info_text.delete("1.0", "end")
        self.info_status.config(text=Path(path).name)

        mgr = PDFManager()
        try:
            pid = mgr.add_pdf(path)
            info = mgr.get_pdf_info(pid)
            lines = [
                f"File:      {info['name']}",
                f"Path:      {info['path']}",
                f"Pages:     {info['page_count']}",
            ]
            valid, missing, max_q = mgr.validate_question_continuity(path)
            if max_q > 0:
                lines.append(f"Questions: 1–{max_q} ({max_q} total)")
                if not valid:
                    lines.append(f"Missing:   {missing}")
            else:
                lines.append("Questions: none detected")

            smart = PDFManager.generate_smart_filename(info["name"])
            lines.append(f"\nSmart rename suggestion:")
            lines.append(f"  {info['name']}  →  {smart}")

            self.info_text.insert("end", "\n".join(lines) + "\n")
        except Exception as e:
            self.info_text.insert("end", f"ERROR: {e}\n")

    def _info_rename(self):
        if not self.info_file or not Path(self.info_file).exists():
            messagebox.showinfo("Rename", "Select a PDF first.")
            return
        original = Path(self.info_file)
        smart = PDFManager.generate_smart_filename(original.name)
        new_path = original.parent / smart

        if new_path.exists():
            messagebox.showerror("Rename", f"Target already exists:\n{new_path}")
            return

        if messagebox.askyesno("Confirm Rename",
                               f"Rename:\n  {original.name}\n  →  {smart}"):
            try:
                original.rename(new_path)
                self.info_file = str(new_path)
                self.info_status.config(text=smart)
                self._append(self.info_text, f"\n✓ Renamed to: {new_path}\n")
            except Exception as e:
                messagebox.showerror("Rename Error", str(e))

    def _info_thumbnail(self):
        if not self.info_file or not Path(self.info_file).exists():
            messagebox.showinfo("Thumbnail", "Select a PDF first.")
            return
        out = filedialog.asksaveasfilename(
            title="Save thumbnail",
            defaultextension=".png",
            filetypes=[("PNG images", "*.png")],
            initialfile="thumbnail.png",
        )
        if not out:
            return
        ok = PDFViewer.generate_thumbnail(self.info_file, 0, out, width=300)
        if ok:
            self._append(self.info_text, f"\n✓ Thumbnail saved: {out}\n")
        else:
            messagebox.showerror("Thumbnail", "Failed to generate thumbnail.")

    # ── Utilities ───────────────────────────────────────────────────────────
    def _scrolled_text(self, parent) -> tk.Text:
        """Create a scrolled, read-only-ish text widget inside a frame."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=8)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame, font=("Consolas", 10), wrap="word",
            bg=CARD_BG, relief="solid", bd=1, padx=8, pady=8,
            yscrollcommand=scrollbar.set,
        )
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)
        return text

    def _append(self, widget: tk.Text, line: str):
        """Thread-safe append to a Text widget."""
        widget.after(0, lambda: self._do_append(widget, line))

    @staticmethod
    def _do_append(widget: tk.Text, line: str):
        widget.insert("end", line)
        widget.see("end")

    def _run_threaded(self, target):
        """Run a function in a background thread so the UI stays responsive."""
        threading.Thread(target=target, daemon=True).start()


# ═════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    PDFEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
