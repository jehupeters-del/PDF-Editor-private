"""
Flask Web Application for PDF Editor
Migrated from Tkinter desktop application to stateless web app
"""
import os
import uuid
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename

from pdf_manager import PDFManager
from pdf_viewer_web import PDFViewerWeb


# Application factory
def create_app(config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
    app.config['UPLOAD_FOLDER'] = Path('instance/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    
    # Ensure upload directory exists
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    
    if config:
        app.config.update(config)
    
    # Helper functions
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    def get_session_folder():
        """Get or create session-specific upload folder"""
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_folder = app.config['UPLOAD_FOLDER'] / session['session_id']
        session_folder.mkdir(parents=True, exist_ok=True)
        
        # Track creation time for cleanup
        timestamp_file = session_folder / '.timestamp'
        if not timestamp_file.exists():
            timestamp_file.write_text(str(datetime.now().timestamp()))
        
        return session_folder
    
    def get_pdf_manager():
        """Get or create PDF manager for current session"""
        session_folder = get_session_folder()
        
        # Initialize manager state if not in session
        if 'pdf_files' not in session:
            session['pdf_files'] = []  # List of file paths
            session['all_pages'] = []
        
        # Reconstruct PDFManager from saved file paths
        manager = PDFManager()
        
        # Re-add all PDFs from saved paths
        for pdf_path in session.get('pdf_files', []):
            if os.path.exists(pdf_path):
                manager.add_pdf(pdf_path)
        
        # Restore page deletion state
        saved_pages = session.get('all_pages', [])
        if saved_pages:
            manager.all_pages = saved_pages
        
        return manager, session_folder
    
    def save_pdf_manager(manager):
        """Save PDF manager state to session (only paths and page data)"""
        # Store only file paths, not PdfReader objects
        session['pdf_files'] = [info['path'] for info in manager.pdfs.values()]
        session['all_pages'] = manager.all_pages
        session.modified = True
    
    # Routes
    @app.route('/')
    def index():
        """Landing page with upload interface"""
        # Clear any existing session data for fresh start
        session.clear()
        return render_template('upload.html')
    
    @app.route('/upload', methods=['POST'])
    def upload():
        """Handle PDF file uploads"""
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        manager, session_folder = get_pdf_manager()
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename):
                    errors.append(f"{file.filename}: Only PDF files are allowed")
                    continue
                
                try:
                    # Secure filename and save
                    filename = secure_filename(file.filename)
                    filepath = session_folder / filename
                    file.save(str(filepath))
                    
                    # Add to PDF manager
                    pdf_id = manager.add_pdf(str(filepath))
                    uploaded_files.append({
                        'id': pdf_id,
                        'name': filename
                    })
                    
                except Exception as e:
                    errors.append(f"{file.filename}: {str(e)}")
        
        save_pdf_manager(manager)
        
        if uploaded_files:
            return jsonify({
                'success': True,
                'files': uploaded_files,
                'errors': errors,
                'redirect': url_for('editor')
            })
        else:
            return jsonify({'error': 'No files uploaded successfully', 'details': errors}), 400
    
    @app.route('/editor')
    def editor():
        """Main editor interface with page grid"""
        manager, session_folder = get_pdf_manager()
        
        if not manager.all_pages:
            return redirect(url_for('index'))
        
        # Generate thumbnails for all pages
        pages_data = []
        for page in manager.all_pages:
            pdf_info = manager.get_pdf_info(page['pdf_id'])
            if pdf_info:
                pdf_path = pdf_info['path']
                thumbnail_b64 = PDFViewerWeb.generate_thumbnail_base64(
                    pdf_path, 
                    page['page_index'],
                    width=200
                )
                
                pages_data.append({
                    'id': page['id'],
                    'pdf_id': page['pdf_id'],
                    'pdf_name': pdf_info['name'],
                    'page_num': page['page_num'],
                    'page_index': page['page_index'],
                    'thumbnail': thumbnail_b64
                })
        
        return render_template('editor.html', 
                             pages=pages_data,
                             total_pages=len(pages_data))
    
    @app.route('/api/delete_page', methods=['POST'])
    def delete_page():
        """API endpoint to delete a specific page"""
        data = request.get_json()
        page_id = data.get('page_id')
        
        if not page_id:
            return jsonify({'error': 'No page_id provided'}), 400
        
        manager, _ = get_pdf_manager()
        manager.remove_page(page_id)
        save_pdf_manager(manager)
        
        return jsonify({
            'success': True,
            'remaining_pages': manager.get_total_page_count()
        })
    
    @app.route('/api/validate', methods=['POST'])
    def validate():
        """Validate question continuity in merged PDF"""
        manager, session_folder = get_pdf_manager()
        
        if not manager.all_pages:
            return jsonify({'error': 'No pages to validate'}), 400
        
        try:
            # Create temporary merged file for validation
            temp_merge = session_folder / 'temp_validation.pdf'
            manager.merge_all(str(temp_merge))
            
            # Run validation
            is_valid, missing, max_q = manager.validate_question_continuity(str(temp_merge))
            
            # Clean up temp file
            temp_merge.unlink(missing_ok=True)
            
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'missing_questions': missing,
                'max_question': max_q,
                'total_pages': manager.get_total_page_count()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/extract', methods=['POST'])
    def extract():
        """Extract question pages from merged PDF"""
        manager, session_folder = get_pdf_manager()
        
        if not manager.all_pages:
            return jsonify({'error': 'No pages to extract'}), 400
        
        try:
            # Create temporary merged file
            temp_merge = session_folder / 'temp_merge.pdf'
            manager.merge_all(str(temp_merge))
            
            # Extract question pages
            temp_extracted = session_folder / 'temp_extracted.pdf'
            result = manager.extract_question_pages(str(temp_merge), str(temp_extracted))
            
            orig_pages, new_pages, questions, is_valid, missing, max_q = result
            
            # Generate report
            report_lines = [
                f"Extraction Complete",
                f"=" * 50,
                f"Original Pages: {orig_pages}",
                f"Extracted Pages: {new_pages}",
                f"Questions Found: {questions}",
                f"Max Question Number: {max_q}",
                f"",
                f"Validation: {'PASS' if is_valid else 'FAIL'}",
            ]
            
            if missing:
                report_lines.append(f"Missing Questions: {missing}")
            
            report = '\n'.join(report_lines)
            
            # Clean up temp files
            temp_merge.unlink(missing_ok=True)
            temp_extracted.unlink(missing_ok=True)
            
            return jsonify({
                'success': True,
                'report': report,
                'original_pages': orig_pages,
                'extracted_pages': new_pages,
                'questions': questions,
                'is_valid': is_valid,
                'missing_questions': missing,
                'max_question': max_q
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/download')
    def download():
        """Merge all pages and download the result"""
        manager, session_folder = get_pdf_manager()
        
        if not manager.all_pages:
            return redirect(url_for('index'))
        
        try:
            # Generate output filename
            output_filename = 'merged_exam.pdf'
            if manager.pdfs:
                first_pdf = next(iter(manager.pdfs.values()))
                output_filename = PDFManager.generate_smart_filename(first_pdf['name'])
            
            # Create merged PDF
            output_path = session_folder / output_filename
            manager.merge_all(str(output_path))
            
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            return f"Error creating merged PDF: {str(e)}", 500
    
    @app.route('/reset')
    def reset():
        """Clear session and start over"""
        session.clear()
        return redirect(url_for('index'))
    
    return app


# For development
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
