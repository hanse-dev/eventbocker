"""File management routes."""
from flask import Blueprint, render_template, send_from_directory, redirect, url_for
from flask import request, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from datetime import datetime
import mimetypes
from functools import wraps

bp = Blueprint('files', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('files.file_list_page'))
        return f(*args, **kwargs)
    return decorated_function

def get_file_info(file_path: Path) -> dict:
    """Get file metadata."""
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'size': get_human_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'type': mimetypes.guess_type(file_path.name)[0] or 'application/octet-stream'
    }

def get_human_size(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_all_files():
    """Get list of all files with their info."""
    files_dir = Path(current_app.config['UPLOAD_FOLDER'])
    files = []
    
    if files_dir.exists():
        for file_path in files_dir.glob('*'):
            if file_path.is_file():
                files.append(get_file_info(file_path))
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

@bp.route('/files')
def file_list_page():
    """Render the file list page."""
    files = get_all_files()
    return render_template(
        'files/list.html',
        files=files,
        is_admin=current_user.is_authenticated and current_user.is_admin
    )

@bp.route('/files/upload', methods=['POST'])
@login_required
@admin_required
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        flash('No file provided', 'error')
        return redirect(url_for('files.file_list_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('files.file_list_page'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_folder / filename
        file.save(str(file_path))
        flash('File uploaded successfully', 'success')
    
    return redirect(url_for('files.file_list_page'))

@bp.route('/files/delete/<filename>', methods=['POST'])
@login_required
@admin_required
def delete_file_route(filename):
    """Handle file deletion."""
    file_path = Path(current_app.config['UPLOAD_FOLDER']) / secure_filename(filename)
    
    if file_path.exists():
        file_path.unlink()
        flash('File deleted successfully', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('files.file_list_page'))

@bp.route('/files/download/<filename>')
def download_file(filename):
    """Download a specific file."""
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )
