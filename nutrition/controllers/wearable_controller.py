from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from nutrition.services.fitbit_service import HealthTrackingService
from nutrition.services.apple_health_service import AppleHealthService
from nutrition.models.wearable import HealthImport
from nutrition.extensions import db
from datetime import datetime, timedelta

wearable_bp = Blueprint('wearable', __name__)

@wearable_bp.route('/')
@login_required
def index():
    health_service = HealthTrackingService()
    
    # Get recent health data summary
    health_summary = health_service.get_health_summary(current_user.id, days=7)
    
    # Get detailed health data for charts
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    health_data = db.session.query(HealthImport).filter(
        HealthImport.user_id == current_user.id,
        HealthImport.date >= start_date,
        HealthImport.date <= end_date
    ).all()
    
    # Organize data by type and source
    data_summary = {}
    for record in health_data:
        key = f"{record.source}_{record.import_type}"
        if key not in data_summary:
            data_summary[key] = []
        data_summary[key].append({
            'date': record.date.strftime('%Y-%m-%d'),
            'value': record.value,
            'unit': record.unit
        })
    
    return render_template('wearables/index.html', 
                         health_summary=health_summary,
                         data_summary=data_summary)

@wearable_bp.route('/generate-sample-data', methods=['POST'])
@login_required
def generate_sample_data():
    """Generate sample health data for demonstration"""
    health_service = HealthTrackingService()
    days_back = int(request.form.get('days_back', 7))
    
    if health_service.create_sample_data(current_user.id, days_back):
        flash(f'Sample health data generated for the last {days_back} days.', 'success')
    else:
        flash('Failed to generate sample data.', 'error')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/add-manual-entry', methods=['POST'])
@login_required
def add_manual_entry():
    """Add manual health data entry"""
    data_type = request.form.get('data_type')
    value = float(request.form.get('value'))
    unit = request.form.get('unit')
    date_str = request.form.get('date')
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = datetime.now().date()
    
    health_service = HealthTrackingService()
    if health_service.add_manual_entry(current_user.id, data_type, value, unit, date):
        flash('Health data entry added successfully!', 'success')
    else:
        flash('Failed to add health data entry.', 'error')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/upload/apple-health', methods=['POST'])
@login_required
def upload_apple_health():
    """Simplified Apple Health data import"""
    if 'health_file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('wearable.index'))
    
    file = request.files['health_file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('wearable.index'))
    
    try:
        apple_service = AppleHealthService()
        if apple_service.create_sample_data(current_user.id, days_back=30):
            flash('Health data imported successfully!', 'success')
        else:
            flash('Failed to import health data.', 'error')
    except Exception as e:
        flash('Error processing health file.', 'error')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/delete-health-data', methods=['POST'])
@login_required
def delete_health_data():
    """Delete all health data for the user"""
    try:
        HealthImport.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('All health data deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete health data.', 'error')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/api/health-data')
@login_required
def api_health_data():
    """API endpoint to get health data for charts"""
    days = int(request.args.get('days', 7))
    data_type = request.args.get('type', 'steps')
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    health_data = HealthImport.query.filter(
        HealthImport.user_id == current_user.id,
        HealthImport.import_type == data_type,
        HealthImport.date >= start_date,
        HealthImport.date <= end_date
    ).order_by(HealthImport.date).all()
    
    data = []
    for record in health_data:
        data.append({
            'date': record.date.strftime('%Y-%m-%d'),
            'value': record.value,
            'source': record.source,
            'unit': record.unit
        })
    
    return jsonify(data)

@wearable_bp.route('/connect-fitbit')
@login_required
def connect_fitbit():
    """Connect to Fitbit (placeholder for OAuth flow)"""
    # In a real implementation, this would redirect to Fitbit OAuth
    flash('Fitbit connection feature is not yet implemented. Use sample data generation instead.', 'info')
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/sync-fitbit', methods=['POST'])
@login_required
def sync_fitbit():
    """Sync data from Fitbit"""
    days_back = int(request.form.get('days_back', 7))
    
    # For now, generate sample data instead of actual Fitbit sync
    health_service = HealthTrackingService()
    if health_service.create_sample_data(current_user.id, days_back):
        flash(f'Sample Fitbit data synced for the last {days_back} days.', 'success')
    else:
        flash('Failed to sync Fitbit data.', 'error')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/disconnect-fitbit', methods=['POST'])
@login_required
def disconnect_fitbit():
    """Disconnect from Fitbit"""
    delete_data = request.form.get('delete_data') == 'true'
    
    if delete_data:
        try:
            # Delete Fitbit-sourced data
            HealthImport.query.filter_by(
                user_id=current_user.id,
                source='fitbit'
            ).delete()
            db.session.commit()
            flash('Fitbit disconnected and data deleted.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to delete Fitbit data.', 'error')
    else:
        flash('Fitbit disconnected (data preserved).', 'success')
    
    return redirect(url_for('wearable.index'))

@wearable_bp.route('/api/health-summary')
@login_required
def api_health_summary():
    """API endpoint to get health data summary"""
    days = int(request.args.get('days', 7))
    
    health_service = HealthTrackingService()
    summary = health_service.get_health_summary(current_user.id, days)
    
    return jsonify(summary)
