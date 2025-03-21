from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import json
import os
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
            
            # Save the updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            
            # Reload the configuration
            reload_config()
            
            flash('Konfiguration erfolgreich aktualisiert.', 'success')
            return redirect(url_for('config.edit_config'))
            
        except Exception as e:
            current_app.logger.error(f"Fehler beim Aktualisieren der Konfiguration: {str(e)}")
            flash(f'Fehler beim Aktualisieren der Konfiguration: {str(e)}', 'danger')
    
    # Load the current configuration
    config_data = load_json_config()
    
    return render_template('config/edit.html', config=config_data)

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
    
    return redirect(url_for('main.index'))
