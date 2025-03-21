from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
import json
import os
import time
from ..config import load_json_config, reload_config

bp = Blueprint('config', __name__, url_prefix='/config')

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_config():
    """Edit the website configuration."""
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung, diese Seite aufzurufen.', 'danger')
        return redirect(url_for('main.index'))
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
    
    if request.method == 'POST':
        try:
            # Get the current config
            current_config = load_json_config()
            
            # Update website settings
            current_config['website']['name'] = request.form.get('website_name', 'Veranstaltungsmanager')
            current_config['website']['title'] = request.form.get('website_title', 'Veranstaltungsverwaltung')
            current_config['website']['description'] = request.form.get('website_description', '')
            current_config['website']['welcome_heading'] = request.form.get('website_welcome_heading', 'Willkommen bei Event Management')
            current_config['website']['welcome_text'] = request.form.get('website_welcome_text', 'Durchstöbern und buchen Sie kommende Veranstaltungen.')
            
            # Update contact settings
            current_config['contact']['email'] = request.form.get('contact_email', '')
            current_config['contact']['phone'] = request.form.get('contact_phone', '')
            
            # Update appearance settings
            current_config['appearance']['primary_color'] = request.form.get('primary_color', '#212529')
            current_config['appearance']['secondary_color'] = request.form.get('secondary_color', '#6c757d')
            current_config['appearance']['logo_icon'] = request.form.get('logo_icon', 'bi-calendar-event')
            
            # Update last modified timestamp
            current_config['_last_modified'] = time.time()
            
            # Save the updated config - KORRIGIERT: fsync innerhalb des with-Blocks
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
                # Ensure file is written to disk before closing
                f.flush()
                os.fsync(f.fileno())
            
            # Wait a moment to ensure file is fully written
            time.sleep(0.1)
            
            # Reload the configuration
            success = reload_config()
            
            if success:
                flash('Konfiguration erfolgreich aktualisiert.', 'success')
            else:
                flash('Konfiguration gespeichert, aber Neuladen fehlgeschlagen. Bitte versuchen Sie es erneut.', 'warning')
                
            return redirect(url_for('config.edit_config'))
            
        except Exception as e:
            current_app.logger.error(f"Fehler beim Aktualisieren der Konfiguration: {str(e)}")
            flash(f'Fehler beim Aktualisieren der Konfiguration: {str(e)}', 'danger')
    
    # Load the current configuration
    config_data = load_json_config()
    
    # Remove internal tracking fields before passing to template
    config_to_render = config_data.copy()
    if '_last_modified' in config_to_render:
        del config_to_render['_last_modified']
    
    return render_template('config/edit.html', json_config=config_to_render)

@bp.route('/reload', methods=['GET'])
@login_required
def reload_configuration():
    """Reload the configuration without restarting the application."""
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung, diese Aktion durchzuführen.', 'danger')
        return redirect(url_for('main.index'))
    
    if reload_config():
        flash('Konfiguration erfolgreich neu geladen.', 'success')
    else:
        flash('Fehler beim Neuladen der Konfiguration.', 'danger')
    
    return redirect(url_for('config.edit_config'))

@bp.route('/debug', methods=['GET'])
@login_required
def debug_config():
    """Debug endpoint to view current configuration values."""
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung, diese Seite aufzurufen.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the current config file content
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        file_content = f"Error reading file: {str(e)}"
    
    # Get the current app config values
    app_config = {
        'WEBSITE_NAME': current_app.config.get('WEBSITE_NAME'),
        'WEBSITE_TITLE': current_app.config.get('WEBSITE_TITLE'),
        'WEBSITE_DESCRIPTION': current_app.config.get('WEBSITE_DESCRIPTION'),
        'WEBSITE_WELCOME_HEADING': current_app.config.get('WEBSITE_WELCOME_HEADING'),
        'WEBSITE_WELCOME_TEXT': current_app.config.get('WEBSITE_WELCOME_TEXT'),
        'CONTACT_EMAIL': current_app.config.get('CONTACT_EMAIL'),
        'CONTACT_PHONE': current_app.config.get('CONTACT_PHONE'),
        'PRIMARY_COLOR': current_app.config.get('PRIMARY_COLOR'),
        'SECONDARY_COLOR': current_app.config.get('SECONDARY_COLOR'),
        'LOGO_ICON': current_app.config.get('LOGO_ICON')
    }
    
    # Create debug template
    return render_template('config/debug.html', 
                          file_content=file_content,
                          app_config=app_config,
                          config_path=config_path)
