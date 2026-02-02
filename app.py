"""
PDF Editor - Flask Web Application
A web application for loading, viewing, manipulating, and merging PDF files.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
from typing import Dict, Any, Optional

from pdf_manager import PDFManager
from pdf_viewer import PDFViewer

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2 hours

# Initialize Flask-Session
Session(app)

# Global task storage (in production, use Redis or database)
background_tasks: Dict[str, Dict[str, Any]] = {}

# Ensure required directories exist
os.makedirs('./flask_session', exist_ok=True)
os.makedirs('./static/temp', exist_ok=True)
os.makedirs('./uploads', exist_ok=True)


def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def get_session_folder():
    """Get folder for current session's uploads"""
    session_id = get_session_id()
    folder = Path('./uploads') / session_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_thumbnail_folder():
    """Get folder for current session's thumbnails"""
    session_id = get_session_id()
    folder = Path('./static/temp') / session_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_pdf_manager():
    """Get or create PDF manager for current session"""
    session_id = get_session_id()
    
    # Initialize session storage if needed
    if 'pdf_data' not in session:
        session['pdf_data'] = {
            'pdfs': {},
            'all_pages': [],
            'selected_pdf_id': None,
            'selected_pages': []
        }
    
    # Create PDF manager and restore state
    manager = PDFManager()
    manager.pdfs = session['pdf_data']['pdfs'].copy()
    manager.all_pages = session['pdf_data']['all_pages'].copy()
    
    return manager


def save_pdf_manager(manager: PDFManager):
    """Save PDF manager state to session"""
    session['pdf_data'] = {
        'pdfs': manager.pdfs.copy(),
        'all_pages': manager.all_pages.copy(),
        'selected_pdf_id': session['pdf_data'].get('selected_pdf_id'),
        'selected_pages': session['pdf_data'].get('selected_pages', [])
    }
    session.modified = True


@app.route('/')
def index():
    """Main page"""
    manager = get_pdf_manager()
    pdfs = manager.get_all_pdfs()
    total_pages = manager.get_total_page_count()
    
    return render_template('index.html', 
                          pdfs=pdfs, 
                          total_pages=total_pages,
                          selected_pdf_id=session['pdf_data'].get('selected_pdf_id'))


@app.route('/upload', methods=['POST'])
def upload_pdfs():
    """Upload PDF files"""
    if 'pdfs' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('pdfs')
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('index'))
    
    manager = get_pdf_manager()
    session_folder = get_session_folder()
    
    success_count = 0
    error_count = 0
    
    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                filepath = session_folder / filename
                file.save(str(filepath))
                
                # Add to manager
                manager.add_pdf(str(filepath))
                success_count += 1
            except Exception as e:
                error_count += 1
                flash(f'Failed to load {file.filename}: {str(e)}', 'error')
    
    save_pdf_manager(manager)
    
    if success_count > 0:
        flash(f'Successfully loaded {success_count} PDF(s)', 'success')
    if error_count > 0:
        flash(f'Failed to load {error_count} file(s)', 'warning')
    
    return redirect(url_for('index'))


@app.route('/new', methods=['POST'])
def new_project():
    """Clear all PDFs and start fresh"""
    # Clear session data
    session['pdf_data'] = {
        'pdfs': {},
        'all_pages': [],
        'selected_pdf_id': None,
        'selected_pages': []
    }
    
    # Clean up uploaded files and thumbnails
    session_id = get_session_id()
    upload_folder = Path('./uploads') / session_id
    thumbnail_folder = Path('./static/temp') / session_id
    
    # Remove files (simple cleanup)
    for folder in [upload_folder, thumbnail_folder]:
        if folder.exists():
            for file in folder.iterdir():
                try:
                    file.unlink()
                except:
                    pass
    
    flash('Started new project', 'success')
    return redirect(url_for('index'))


@app.route('/pdf/<pdf_id>')
def view_pdf(pdf_id):
    """View pages of a specific PDF"""
    manager = get_pdf_manager()
    pdf_info = manager.get_pdf_info(pdf_id)
    
    if not pdf_info:
        flash('PDF not found', 'error')
        return redirect(url_for('index'))
    
    # Update selected PDF
    session['pdf_data']['selected_pdf_id'] = pdf_id
    session.modified = True
    
    # Get pages for this PDF
    pages = manager.get_pages_for_pdf(pdf_id)
    
    # Generate thumbnails
    thumbnail_folder = get_thumbnail_folder()
    session_id = get_session_id()
    
    pages_with_thumbnails = []
    for page in pages:
        thumbnail_filename = f"page_{page['id']}.png"
        thumbnail_path = thumbnail_folder / thumbnail_filename
        
        # Generate thumbnail if it doesn't exist
        if not thumbnail_path.exists():
            try:
                PDFViewer.generate_thumbnail(
                    pdf_info['path'],
                    page['page_index'],
                    str(thumbnail_path)
                )
            except Exception as e:
                print(f"Error generating thumbnail: {e}")
                thumbnail_filename = None
        
        pages_with_thumbnails.append({
            **page,
            'thumbnail': f'/static/temp/{session_id}/{thumbnail_filename}' if thumbnail_filename else None,
            'selected': page['id'] in session['pdf_data'].get('selected_pages', [])
        })
    
    return render_template('pdf_view.html',
                          pdf_info=pdf_info,
                          pages=pages_with_thumbnails,
                          total_pages=manager.get_total_page_count())


@app.route('/remove-pdf/<pdf_id>', methods=['POST'])
def remove_pdf(pdf_id):
    """Remove a PDF"""
    manager = get_pdf_manager()
    manager.remove_pdf(pdf_id)
    save_pdf_manager(manager)
    
    # Clear selected PDF if it was removed
    if session['pdf_data'].get('selected_pdf_id') == pdf_id:
        session['pdf_data']['selected_pdf_id'] = None
        session.modified = True
    
    flash('PDF removed', 'success')
    return redirect(url_for('index'))


@app.route('/remove-page/<page_id>', methods=['POST'])
def remove_page(page_id):
    """Remove a single page"""
    manager = get_pdf_manager()
    manager.remove_page(page_id)
    save_pdf_manager(manager)
    
    # Remove from selected pages
    selected_pages = session['pdf_data'].get('selected_pages', [])
    if page_id in selected_pages:
        selected_pages.remove(page_id)
        session['pdf_data']['selected_pages'] = selected_pages
        session.modified = True
    
    # Get current PDF ID to redirect back
    pdf_id = session['pdf_data'].get('selected_pdf_id')
    if pdf_id:
        return redirect(url_for('view_pdf', pdf_id=pdf_id))
    return redirect(url_for('index'))


@app.route('/toggle-page/<page_id>', methods=['POST'])
def toggle_page_selection(page_id):
    """Toggle page selection"""
    selected_pages = session['pdf_data'].get('selected_pages', [])
    
    if page_id in selected_pages:
        selected_pages.remove(page_id)
    else:
        selected_pages.append(page_id)
    
    session['pdf_data']['selected_pages'] = selected_pages
    session.modified = True
    
    return jsonify({'success': True, 'selected': page_id in selected_pages})


@app.route('/remove-selected-pages', methods=['POST'])
def remove_selected_pages():
    """Remove all selected pages"""
    manager = get_pdf_manager()
    selected_pages = session['pdf_data'].get('selected_pages', [])
    
    for page_id in selected_pages:
        manager.remove_page(page_id)
    
    session['pdf_data']['selected_pages'] = []
    save_pdf_manager(manager)
    
    flash(f'Removed {len(selected_pages)} page(s)', 'success')
    
    pdf_id = session['pdf_data'].get('selected_pdf_id')
    if pdf_id:
        return redirect(url_for('view_pdf', pdf_id=pdf_id))
    return redirect(url_for('index'))


@app.route('/merge', methods=['POST'])
def merge_pdfs():
    """Merge all PDFs"""
    manager = get_pdf_manager()
    
    if manager.get_total_page_count() == 0:
        flash('No pages to merge', 'warning')
        return redirect(url_for('index'))
    
    # Create output file
    output_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
    output_path = get_session_folder() / output_filename
    
    try:
        manager.merge_all(str(output_path))
        
        # Send file for download
        return send_file(
            str(output_path),
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Failed to merge PDFs: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/extract', methods=['GET', 'POST'])
def extract_questions():
    """Extract question pages - single or batch mode"""
    if request.method == 'GET':
        return render_template('extract.html')
    
    # Handle file upload
    mode = request.form.get('mode', 'single')
    
    if mode == 'single':
        return extract_single()
    else:
        return extract_batch()


def extract_single():
    """Extract from single PDF"""
    if 'pdf' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('extract_questions'))
    
    file = request.files['pdf']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('extract_questions'))
    
    if not file.filename.lower().endswith('.pdf'):
        flash('Please upload a PDF file', 'error')
        return redirect(url_for('extract_questions'))
    
    # Save file BEFORE starting thread (to avoid request context issues)
    task_id = str(uuid.uuid4())
    session_folder = get_session_folder()
    input_filename = secure_filename(file.filename)
    input_path = session_folder / f"extract_input_{task_id}.pdf"
    file.save(str(input_path))
    
    # Generate output filename
    manager = PDFManager()
    smart_name = manager.generate_smart_filename(input_filename)
    output_path = session_folder / f"extract_output_{task_id}.pdf"
    
    # Now start background task with file paths (not file objects)
    def extract_worker():
        try:
            # Extract
            background_tasks[task_id]['status'] = 'processing'
            result = manager.extract_question_pages(str(input_path), str(output_path))
            orig_pages, new_pages, questions, is_valid, missing, max_q = result
            
            background_tasks[task_id].update({
                'status': 'completed',
                'input_name': input_filename,
                'output_name': smart_name,
                'output_path': str(output_path),
                'orig_pages': orig_pages,
                'new_pages': new_pages,
                'questions': list(questions),  # Convert to list for JSON
                'is_valid': is_valid,
                'missing': list(missing),  # Convert to list for JSON
                'max_question': max_q
            })
        except Exception as e:
            background_tasks[task_id]['status'] = 'error'
            background_tasks[task_id]['error'] = str(e)
    
    background_tasks[task_id] = {'status': 'starting', 'mode': 'extract_single'}
    thread = threading.Thread(target=extract_worker, daemon=True)
    thread.start()
    
    return redirect(url_for('task_status', task_id=task_id))


def extract_batch():
    """Extract from multiple PDFs"""
    if 'pdfs' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('extract_questions'))
    
    files = request.files.getlist('pdfs')
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('extract_questions'))
    
    # Save all files BEFORE starting thread
    task_id = str(uuid.uuid4())
    session_folder = get_session_folder()
    
    # Prepare file info list
    file_infos = []
    for idx, file in enumerate(files):
        input_filename = secure_filename(file.filename)
        input_path = session_folder / f"batch_input_{task_id}_{idx}.pdf"
        file.save(str(input_path))
        
        file_infos.append({
            'input_filename': input_filename,
            'input_path': str(input_path),
            'idx': idx
        })
    
    # Now start background task with file info (not file objects)
    def batch_extract_worker():
        results = []
        manager = PDFManager()
        
        for file_info in file_infos:
            idx = file_info['idx']
            input_filename = file_info['input_filename']
            input_path = file_info['input_path']
            
            background_tasks[task_id]['progress'] = f"{idx + 1}/{len(file_infos)}"
            
            try:
                smart_name = manager.generate_smart_filename(input_filename)
                output_path = session_folder / f"batch_output_{task_id}_{idx}.pdf"
                
                result = manager.extract_question_pages(input_path, str(output_path))
                orig_pages, new_pages, questions, is_valid, missing, max_q = result
                
                results.append({
                    'input_name': input_filename,
                    'output_name': smart_name,
                    'output_path': str(output_path),
                    'orig_pages': orig_pages,
                    'new_pages': new_pages,
                    'questions': list(questions),  # Convert to list for JSON
                    'is_valid': is_valid,
                    'missing': list(missing),  # Convert to list for JSON
                    'max_question': max_q,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'input_name': input_filename,
                    'output_name': '',
                    'output_path': '',
                    'orig_pages': 0,
                    'new_pages': 0,
                    'questions': [],
                    'is_valid': False,
                    'missing': [],
                    'max_question': 0,
                    'error': str(e)
                })
        
        background_tasks[task_id]['status'] = 'completed'
        background_tasks[task_id]['results'] = results
    
    background_tasks[task_id] = {
        'status': 'starting',
        'mode': 'extract_batch',
        'progress': f"0/{len(file_infos)}"
    }
    thread = threading.Thread(target=batch_extract_worker, daemon=True)
    thread.start()
    
    return redirect(url_for('task_status', task_id=task_id))


@app.route('/validate', methods=['GET', 'POST'])
def validate_questions():
    """Validate question continuity"""
    if request.method == 'GET':
        return render_template('validate.html')
    
    mode = request.form.get('mode', 'single')
    
    if mode == 'single':
        return validate_single()
    else:
        return validate_batch()


def validate_single():
    """Validate single PDF"""
    if 'pdf' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('validate_questions'))
    
    file = request.files['pdf']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('validate_questions'))
    
    # Save file BEFORE starting thread
    task_id = str(uuid.uuid4())
    session_folder = get_session_folder()
    input_filename = file.filename
    input_path = session_folder / f"validate_{task_id}.pdf"
    file.save(str(input_path))
    
    # Now start background task with file path (not file object)
    def validate_worker():
        try:
            manager = PDFManager()
            background_tasks[task_id]['status'] = 'processing'
            is_valid, missing, max_q = manager.validate_question_continuity(str(input_path))
            
            background_tasks[task_id].update({
                'status': 'completed',
                'file_name': input_filename,
                'is_valid': is_valid,
                'missing': list(missing),  # Convert to list for JSON
                'max_question': max_q
            })
        except Exception as e:
            background_tasks[task_id]['status'] = 'error'
            background_tasks[task_id]['error'] = str(e)
    
    background_tasks[task_id] = {'status': 'starting', 'mode': 'validate_single'}
    thread = threading.Thread(target=validate_worker, daemon=True)
    thread.start()
    
    return redirect(url_for('task_status', task_id=task_id))


def validate_batch():
    """Validate multiple PDFs"""
    if 'pdfs' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('validate_questions'))
    
    files = request.files.getlist('pdfs')
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('validate_questions'))
    
    # Save all files BEFORE starting thread
    task_id = str(uuid.uuid4())
    session_folder = get_session_folder()
    
    # Prepare file info list
    file_infos = []
    for idx, file in enumerate(files):
        input_filename = file.filename
        input_path = session_folder / f"validate_batch_{task_id}_{idx}.pdf"
        file.save(str(input_path))
        
        file_infos.append({
            'input_filename': input_filename,
            'input_path': str(input_path),
            'idx': idx
        })
    
    # Now start background task with file info (not file objects)
    def batch_validate_worker():
        results = []
        manager = PDFManager()
        
        for file_info in file_infos:
            idx = file_info['idx']
            input_filename = file_info['input_filename']
            input_path = file_info['input_path']
            
            background_tasks[task_id]['progress'] = f"{idx + 1}/{len(file_infos)}"
            
            try:
                is_valid, missing, max_q = manager.validate_question_continuity(input_path)
                
                results.append({
                    'file_name': input_filename,
                    'is_valid': is_valid,
                    'missing': list(missing),  # Convert to list for JSON
                    'max_question': max_q,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'file_name': input_filename,
                    'is_valid': False,
                    'missing': [],
                    'max_question': 0,
                    'error': str(e)
                })
        
        background_tasks[task_id]['status'] = 'completed'
        background_tasks[task_id]['results'] = results
    
    background_tasks[task_id] = {
        'status': 'starting',
        'mode': 'validate_batch',
        'progress': f"0/{len(file_infos)}"
    }
    thread = threading.Thread(target=batch_validate_worker, daemon=True)
    thread.start()
    
    return redirect(url_for('task_status', task_id=task_id))
    
    background_tasks[task_id] = {
        'status': 'starting',
        'mode': 'validate_batch',
        'progress': f"0/{len(files)}"
    }
    thread = threading.Thread(target=batch_validate_worker, daemon=True)
    thread.start()
    
    return redirect(url_for('task_status', task_id=task_id))


@app.route('/task/<task_id>')
def task_status(task_id):
    """Show task status page with polling"""
    if task_id not in background_tasks:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('task_status.html', task_id=task_id)


@app.route('/api/task/<task_id>')
def api_task_status(task_id):
    """API endpoint for task status polling"""
    if task_id not in background_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(background_tasks[task_id])


@app.route('/download/<task_id>/<int:file_index>')
def download_extracted(task_id, file_index):
    """Download extracted/validated file"""
    if task_id not in background_tasks:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = background_tasks[task_id]
    
    if task['mode'] == 'extract_single':
        output_path = task.get('output_path')
        output_name = task.get('output_name', 'extracted.pdf')
        
        if output_path and Path(output_path).exists():
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_name,
                mimetype='application/pdf'
            )
    elif task['mode'] == 'extract_batch':
        results = task.get('results', [])
        if file_index < len(results):
            result = results[file_index]
            output_path = result.get('output_path')
            output_name = result.get('output_name', 'extracted.pdf')
            
            if output_path and Path(output_path).exists():
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=output_name,
                    mimetype='application/pdf'
                )
    
    flash('File not found', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
