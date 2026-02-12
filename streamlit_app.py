from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

from pdf_manager import PDFManager
from pdf_viewer import PDFViewer

APP_TITLE = "PDF Editor"
BASE_UPLOAD_DIR = Path("./uploads")
BASE_THUMBNAIL_DIR = Path("./static/temp")
MAIN_VIEWS = ["Editor", "Extract Questions", "Validate Questions"]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f7f8fb 0%, #ffffff 35%);
        }
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .app-hero {
            padding: 1rem 1.1rem;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid rgba(49, 51, 63, 0.12);
            margin-bottom: 0.8rem;
        }
        .app-hero h1 {
            font-size: 1.55rem;
            margin: 0;
        }
        .app-hero p {
            margin: 0.25rem 0 0 0;
            color: #4b5563;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 600;
        }
        .stSegmentedControl {
            margin-bottom: 0.65rem;
        }
        .stFileUploader {
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_base_dirs() -> None:
    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    BASE_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "manager" not in st.session_state:
        st.session_state.manager = PDFManager()

    if "selected_pdf_id" not in st.session_state:
        st.session_state.selected_pdf_id = None

    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = set()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "merged_output" not in st.session_state:
        st.session_state.merged_output = None

    if "extract_result_single" not in st.session_state:
        st.session_state.extract_result_single = None

    if "extract_results_batch" not in st.session_state:
        st.session_state.extract_results_batch = None

    if "validate_result_single" not in st.session_state:
        st.session_state.validate_result_single = None

    if "validate_results_batch" not in st.session_state:
        st.session_state.validate_results_batch = None

    if "main_view" not in st.session_state:
        st.session_state.main_view = "Editor"


def get_session_folder() -> Path:
    folder = BASE_UPLOAD_DIR / st.session_state.session_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_thumbnail_folder() -> Path:
    folder = BASE_THUMBNAIL_DIR / st.session_state.session_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def queue_message(level: str, text: str) -> None:
    st.session_state.messages.append((level, text))


def flush_messages() -> None:
    for level, text in st.session_state.messages:
        if level == "success":
            st.success(text)
        elif level == "warning":
            st.warning(text)
        elif level == "error":
            st.error(text)
        else:
            st.info(text)
    st.session_state.messages = []


def save_uploaded_file(uploaded_file: Any, prefix: str | None = None) -> Path:
    safe_name = os.path.basename(uploaded_file.name)
    if prefix:
        filename = f"{prefix}_{safe_name}"
    else:
        filename = safe_name

    output_path = get_session_folder() / filename
    with output_path.open("wb") as f:
        f.write(uploaded_file.getbuffer())
    return output_path


def cleanup_session_files() -> None:
    for base in (BASE_UPLOAD_DIR, BASE_THUMBNAIL_DIR):
        folder = base / st.session_state.session_id
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)


def new_project() -> None:
    cleanup_session_files()
    st.session_state.manager = PDFManager()
    st.session_state.selected_pdf_id = None
    st.session_state.selected_pages = set()
    st.session_state.merged_output = None
    st.session_state.extract_result_single = None
    st.session_state.extract_results_batch = None
    st.session_state.validate_result_single = None
    st.session_state.validate_results_batch = None
    queue_message("success", "Started new project")


def add_uploaded_pdfs(uploaded_files: list[Any]) -> None:
    manager: PDFManager = st.session_state.manager
    success_count = 0
    error_count = 0

    for uploaded_file in uploaded_files:
        if not uploaded_file.name.lower().endswith(".pdf"):
            error_count += 1
            queue_message("error", f"Skipped non-PDF file: {uploaded_file.name}")
            continue

        try:
            file_path = save_uploaded_file(uploaded_file)
            pdf_id = manager.add_pdf(str(file_path))
            success_count += 1
            if st.session_state.selected_pdf_id is None:
                st.session_state.selected_pdf_id = pdf_id
        except Exception as e:
            error_count += 1
            queue_message("error", f"Failed to load {uploaded_file.name}: {e}")

    if success_count:
        queue_message("success", f"Successfully loaded {success_count} PDF(s)")
    if error_count:
        queue_message("warning", f"Failed to load {error_count} file(s)")


def remove_pdf(pdf_id: str) -> None:
    manager: PDFManager = st.session_state.manager
    manager.remove_pdf(pdf_id)
    pages_to_remove = {p for p in st.session_state.selected_pages if p.startswith(f"{pdf_id}-page-")}
    st.session_state.selected_pages -= pages_to_remove

    if st.session_state.selected_pdf_id == pdf_id:
        st.session_state.selected_pdf_id = None

    queue_message("success", "PDF removed")


def remove_single_page(page_id: str) -> None:
    manager: PDFManager = st.session_state.manager
    manager.remove_page(page_id)
    st.session_state.selected_pages.discard(page_id)


def remove_selected_pages() -> None:
    manager: PDFManager = st.session_state.manager
    selected_page_ids = list(st.session_state.selected_pages)

    for page_id in selected_page_ids:
        manager.remove_page(page_id)

    st.session_state.selected_pages = set()
    queue_message("success", f"Removed {len(selected_page_ids)} page(s)")


def prepare_merge_download() -> None:
    manager: PDFManager = st.session_state.manager

    if manager.get_total_page_count() == 0:
        queue_message("warning", "No pages to merge")
        return

    output_name = "merged.pdf"
    output_path = get_session_folder() / f"merged_{uuid.uuid4().hex[:8]}.pdf"

    manager.merge_all(str(output_path))
    st.session_state.merged_output = {
        "filename": output_name,
        "bytes": output_path.read_bytes(),
    }
    queue_message("success", "Merged PDF is ready to download")


def get_thumbnail_for_page(pdf_path: str, page_id: str, page_index: int) -> Path | None:
    thumbnail_path = get_thumbnail_folder() / f"page_{page_id}.png"

    if not thumbnail_path.exists():
        ok = PDFViewer.generate_thumbnail(pdf_path, page_index, str(thumbnail_path))
        if not ok:
            return None

    return thumbnail_path


def render_sidebar() -> None:
    manager: PDFManager = st.session_state.manager

    with st.sidebar:
        st.header("PDF Documents")

        if st.button("New Project", use_container_width=True):
            new_project()
            st.rerun()

        uploaded_files = st.file_uploader(
            "Load PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="sidebar_loader",
        )

        if st.button("Add Loaded PDFs", use_container_width=True):
            if uploaded_files:
                add_uploaded_pdfs(uploaded_files)
                st.rerun()
            else:
                queue_message("warning", "No files selected")
                st.rerun()

        st.markdown("---")

        pdfs = manager.get_all_pdfs()
        if not pdfs:
            st.info("No PDFs loaded. Use Load PDFs to start.")
        else:
            for pdf_id, pdf_info in pdfs.items():
                selected = st.session_state.selected_pdf_id == pdf_id
                row_left, row_right = st.columns([4, 1])
                with row_left:
                    label = f"📄 {pdf_info['name']} ({pdf_info['page_count']} pages)"
                    if st.button(label, key=f"select_pdf_{pdf_id}", use_container_width=True, type="primary" if selected else "secondary"):
                        st.session_state.selected_pdf_id = pdf_id
                        st.rerun()
                with row_right:
                    if st.button("🗑", key=f"remove_pdf_{pdf_id}", help="Remove PDF"):
                        remove_pdf(pdf_id)
                        st.rerun()


def render_editor_page() -> None:
    st.subheader("Editor")
    manager: PDFManager = st.session_state.manager

    total_pages = manager.get_total_page_count()
    total_pdfs = len(manager.get_all_pdfs())
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Loaded PDFs", total_pdfs)
    with metric_col2:
        st.metric("Total Pages", total_pages)
    with metric_col3:
        st.metric("Selected Pages", len(st.session_state.selected_pages))

    if total_pages > 0:
        action_col1, action_col2 = st.columns([1, 1])
        with action_col1:
            if st.button("Prepare Merged PDF", use_container_width=True):
                try:
                    prepare_merge_download()
                except Exception as e:
                    queue_message("error", f"Failed to merge PDFs: {e}")
                st.rerun()
        with action_col2:
            merged = st.session_state.merged_output
            if merged:
                st.download_button(
                    "Download Merged PDF",
                    data=merged["bytes"],
                    file_name=merged["filename"],
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_merged_pdf",
                )

    selected_pdf_id = st.session_state.selected_pdf_id
    if not selected_pdf_id:
        st.info("Select a PDF from the sidebar to view and edit pages.")
        return

    pdf_info = manager.get_pdf_info(selected_pdf_id)
    if not pdf_info:
        st.warning("Selected PDF was not found. Pick another PDF from the sidebar.")
        st.session_state.selected_pdf_id = None
        return

    pages = manager.get_pages_for_pdf(selected_pdf_id)
    current_page_ids = {p["id"] for p in pages}
    st.session_state.selected_pages = {p for p in st.session_state.selected_pages if p in current_page_ids}

    st.markdown(f"### {pdf_info['name']}")

    selected_count = len(st.session_state.selected_pages)
    header_col1, header_col2 = st.columns([2, 1])
    with header_col1:
        if selected_count:
            st.info(f"{selected_count} page(s) selected")
    with header_col2:
        disabled = selected_count == 0
        if st.button("Remove Selected", disabled=disabled, use_container_width=True):
            remove_selected_pages()
            st.rerun()

    if not pages:
        st.info("No pages available in this PDF")
        return

    grid_columns = st.columns(4)
    for idx, page in enumerate(pages):
        with grid_columns[idx % 4]:
            thumb_path = get_thumbnail_for_page(pdf_info["path"], page["id"], page["page_index"])
            if thumb_path and thumb_path.exists():
                st.image(str(thumb_path), use_container_width=True)
            else:
                st.caption("Thumbnail unavailable")

            st.caption(f"Page {page['page_num']}")

            is_selected = page["id"] in st.session_state.selected_pages
            toggle_label = "Deselect" if is_selected else "Select"
            if st.button(toggle_label, key=f"toggle_{page['id']}", use_container_width=True):
                if is_selected:
                    st.session_state.selected_pages.discard(page["id"])
                else:
                    st.session_state.selected_pages.add(page["id"])
                st.rerun()

            if st.button("Remove Page", key=f"remove_page_{page['id']}", use_container_width=True):
                remove_single_page(page["id"])
                st.rerun()


def render_extract_single() -> None:
    st.markdown("#### Single PDF")
    uploaded = st.file_uploader("Select PDF File", type=["pdf"], key="extract_single_pdf")

    if st.button("Extract Questions", key="extract_single_button", use_container_width=True):
        if uploaded is None:
            st.error("No file selected")
            return

        task_id = str(uuid.uuid4())
        input_path = save_uploaded_file(uploaded, prefix=f"extract_input_{task_id}")

        manager = PDFManager()
        smart_name = manager.generate_smart_filename(uploaded.name)
        output_path = get_session_folder() / f"extract_output_{task_id}.pdf"

        with st.spinner("Extracting question pages..."):
            try:
                orig_pages, new_pages, questions, is_valid, missing, max_question = manager.extract_question_pages(
                    str(input_path),
                    str(output_path),
                )

                st.session_state.extract_result_single = {
                    "input_name": uploaded.name,
                    "output_name": smart_name,
                    "orig_pages": orig_pages,
                    "new_pages": new_pages,
                    "questions": list(questions),
                    "is_valid": is_valid,
                    "missing": list(missing),
                    "max_question": max_question,
                    "bytes": output_path.read_bytes(),
                }
                queue_message("success", "Question extraction completed")
            except Exception as e:
                st.session_state.extract_result_single = {"error": str(e)}
                queue_message("error", f"Extraction failed: {e}")

        st.rerun()

    result = st.session_state.extract_result_single
    if not result:
        return

    if result.get("error"):
        st.error(result["error"])
        return

    st.success("Question Pages Extracted")
    reduction = result["orig_pages"] - result["new_pages"]
    reduction_pct = (reduction / result["orig_pages"] * 100) if result["orig_pages"] > 0 else 0.0

    st.write(f"Source: {result['input_name']}")
    st.write(f"Output: {result['output_name']}")
    st.write(f"Pages: {result['orig_pages']} → {result['new_pages']} (removed {reduction} pages, {reduction_pct:.1f}% reduction)")

    if result["questions"]:
        st.write(f"Questions found: {len(result['questions'])} unique ({min(result['questions'])} to {max(result['questions'])})")
    else:
        st.write("Questions found: 0")

    if result["is_valid"]:
        st.success(f"Validation passed: Questions 1-{result['max_question']} are present")
    else:
        missing_preview = ", ".join(str(m) for m in result["missing"][:20])
        suffix = "..." if len(result["missing"]) > 20 else ""
        st.warning(
            f"Validation warning: {len(result['missing'])} question(s) missing. "
            f"Expected 1-{result['max_question']}; missing {missing_preview}{suffix}"
        )

    st.download_button(
        "Download Extracted PDF",
        data=result["bytes"],
        file_name=result["output_name"],
        mime="application/pdf",
        use_container_width=True,
        key="download_extract_single",
    )


def render_extract_batch() -> None:
    st.markdown("#### Batch Mode")
    uploaded_files = st.file_uploader("Select Multiple PDF Files", type=["pdf"], accept_multiple_files=True, key="extract_batch_pdfs")

    if st.button("Extract All", key="extract_batch_button", use_container_width=True):
        if not uploaded_files:
            st.error("No files selected")
            return

        manager = PDFManager()
        results = []
        progress = st.progress(0, text="Starting batch extraction")

        for idx, uploaded in enumerate(uploaded_files):
            progress_text = f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded.name}"
            progress.progress((idx + 1) / len(uploaded_files), text=progress_text)

            task_id = str(uuid.uuid4())
            input_path = save_uploaded_file(uploaded, prefix=f"batch_input_{task_id}_{idx}")
            output_path = get_session_folder() / f"batch_output_{task_id}_{idx}.pdf"

            try:
                smart_name = manager.generate_smart_filename(uploaded.name)
                orig_pages, new_pages, questions, is_valid, missing, max_question = manager.extract_question_pages(
                    str(input_path),
                    str(output_path),
                )
                results.append({
                    "input_name": uploaded.name,
                    "output_name": smart_name,
                    "orig_pages": orig_pages,
                    "new_pages": new_pages,
                    "questions": list(questions),
                    "is_valid": is_valid,
                    "missing": list(missing),
                    "max_question": max_question,
                    "bytes": output_path.read_bytes(),
                    "error": None,
                })
            except Exception as e:
                results.append({
                    "input_name": uploaded.name,
                    "output_name": "",
                    "orig_pages": 0,
                    "new_pages": 0,
                    "questions": [],
                    "is_valid": False,
                    "missing": [],
                    "max_question": 0,
                    "bytes": None,
                    "error": str(e),
                })

        st.session_state.extract_results_batch = results
        queue_message("success", f"Batch extraction finished for {len(uploaded_files)} file(s)")
        st.rerun()

    results = st.session_state.extract_results_batch
    if not results:
        return

    success_count = len([r for r in results if not r["error"]])
    error_count = len([r for r in results if r["error"]])
    valid_count = len([r for r in results if (not r["error"]) and r["is_valid"]])

    st.info(f"✅ {success_count} Success | ✅ {valid_count} Valid | ⚠️ {success_count - valid_count} Warnings | ❌ {error_count} Errors")

    for index, result in enumerate(results):
        title = f"#{index + 1}: {result['input_name']}"
        with st.expander(title, expanded=index == 0):
            if result["error"]:
                st.error(result["error"])
                continue

            reduction = result["orig_pages"] - result["new_pages"]
            reduction_pct = (reduction / result["orig_pages"] * 100) if result["orig_pages"] > 0 else 0.0

            st.write(f"Output: {result['output_name']}")
            st.write(f"Pages: {result['orig_pages']} → {result['new_pages']} ({reduction_pct:.1f}% reduction)")
            if result["is_valid"]:
                st.success(f"All questions present (1-{result['max_question']})")
            else:
                st.warning(f"Missing {len(result['missing'])} question(s)")

            if result["bytes"]:
                st.download_button(
                    f"Download {result['output_name']}",
                    data=result["bytes"],
                    file_name=result["output_name"],
                    mime="application/pdf",
                    key=f"download_extract_batch_{index}",
                )


def render_extract_page() -> None:
    st.subheader("Extract Question Pages")
    st.caption('Extract only pages containing "Question {number}" pattern.')

    mode = st.radio("Mode", ["Single PDF", "Batch Mode"], horizontal=True, key="extract_mode")
    if mode == "Single PDF":
        render_extract_single()
    else:
        render_extract_batch()


def render_validate_single() -> None:
    st.markdown("#### Single PDF")
    uploaded = st.file_uploader("Select PDF File", type=["pdf"], key="validate_single_pdf")

    if st.button("Validate Questions", key="validate_single_button", use_container_width=True):
        if uploaded is None:
            st.error("No file selected")
            return

        task_id = str(uuid.uuid4())
        input_path = save_uploaded_file(uploaded, prefix=f"validate_{task_id}")

        with st.spinner("Validating questions..."):
            try:
                manager = PDFManager()
                is_valid, missing, max_question = manager.validate_question_continuity(str(input_path))
                st.session_state.validate_result_single = {
                    "file_name": uploaded.name,
                    "is_valid": is_valid,
                    "missing": list(missing),
                    "max_question": max_question,
                    "error": None,
                }
                queue_message("success", "Validation completed")
            except Exception as e:
                st.session_state.validate_result_single = {
                    "file_name": uploaded.name,
                    "is_valid": False,
                    "missing": [],
                    "max_question": 0,
                    "error": str(e),
                }
                queue_message("error", f"Validation failed: {e}")

        st.rerun()

    result = st.session_state.validate_result_single
    if not result:
        return

    if result["error"]:
        st.error(result["error"])
        return

    st.write(f"File: {result['file_name']}")
    if result["max_question"] == 0:
        st.info('No questions found matching "Question {number}"')
    elif result["is_valid"]:
        st.success(f"All questions present (1-{result['max_question']})")
    else:
        missing_preview = ", ".join(str(m) for m in result["missing"][:50])
        suffix = "..." if len(result["missing"]) > 50 else ""
        st.error(f"Missing {len(result['missing'])} question(s). Expected 1-{result['max_question']}.")
        st.write(f"Missing question numbers: {missing_preview}{suffix}")
        if 1 in result["missing"]:
            st.warning("Critical: Question 1 is missing")


def render_validate_batch() -> None:
    st.markdown("#### Batch Mode")
    uploaded_files = st.file_uploader("Select Multiple PDF Files", type=["pdf"], accept_multiple_files=True, key="validate_batch_pdfs")

    if st.button("Validate All", key="validate_batch_button", use_container_width=True):
        if not uploaded_files:
            st.error("No files selected")
            return

        manager = PDFManager()
        results = []
        progress = st.progress(0, text="Starting batch validation")

        for idx, uploaded in enumerate(uploaded_files):
            progress_text = f"Validating {idx + 1}/{len(uploaded_files)}: {uploaded.name}"
            progress.progress((idx + 1) / len(uploaded_files), text=progress_text)

            task_id = str(uuid.uuid4())
            input_path = save_uploaded_file(uploaded, prefix=f"validate_batch_{task_id}_{idx}")

            try:
                is_valid, missing, max_question = manager.validate_question_continuity(str(input_path))
                results.append({
                    "file_name": uploaded.name,
                    "is_valid": is_valid,
                    "missing": list(missing),
                    "max_question": max_question,
                    "error": None,
                })
            except Exception as e:
                results.append({
                    "file_name": uploaded.name,
                    "is_valid": False,
                    "missing": [],
                    "max_question": 0,
                    "error": str(e),
                })

        st.session_state.validate_results_batch = results
        queue_message("success", f"Batch validation finished for {len(uploaded_files)} file(s)")
        st.rerun()

    results = st.session_state.validate_results_batch
    if not results:
        return

    valid_count = len([r for r in results if (not r["error"]) and r["is_valid"]])
    invalid_count = len([r for r in results if (not r["error"]) and (not r["is_valid"])])
    error_count = len([r for r in results if r["error"]])

    st.info(f"✅ {valid_count} Valid | ⚠️ {invalid_count} Issues | ❌ {error_count} Errors")

    for idx, result in enumerate(results):
        with st.expander(f"#{idx + 1}: {result['file_name']}", expanded=idx == 0):
            if result["error"]:
                st.error(result["error"])
            elif result["max_question"] == 0:
                st.info("No questions found in this PDF")
            elif result["is_valid"]:
                st.success(f"All questions present (1-{result['max_question']})")
            else:
                missing_preview = ", ".join(str(m) for m in result["missing"][:10])
                suffix = "..." if len(result["missing"]) > 10 else ""
                st.warning(f"Missing {len(result['missing'])} question(s)")
                st.write(f"Expected 1-{result['max_question']} | Missing: {missing_preview}{suffix}")
                if 1 in result["missing"]:
                    st.warning("Critical: Question 1 missing")


def render_validate_page() -> None:
    st.subheader("Validate Question Continuity")
    st.caption('Check if all question numbers from 1 to N are present in your PDF.')

    mode = st.radio("Mode", ["Single PDF", "Batch Mode"], horizontal=True, key="validate_mode")
    if mode == "Single PDF":
        render_validate_single()
    else:
        render_validate_batch()


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="wide")

    inject_styles()
    ensure_base_dirs()
    init_state()

    st.markdown(
        """
        <div class="app-hero">
            <h1>PDF Editor</h1>
            <p>Fast PDF editing, extraction, and validation in one workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_sidebar()
    flush_messages()

    selected_view = st.segmented_control(
        "Workspace",
        options=MAIN_VIEWS,
        default=st.session_state.main_view,
        key="main_view_selector",
    )

    if selected_view is None:
        selected_view = st.session_state.main_view

    st.session_state.main_view = selected_view

    if selected_view == "Editor":
        render_editor_page()
    elif selected_view == "Extract Questions":
        render_extract_page()
    else:
        render_validate_page()


if __name__ == "__main__":
    main()
