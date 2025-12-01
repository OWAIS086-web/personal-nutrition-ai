from datetime import datetime, timedelta
from nutrition.models.wearable import HealthImport
from nutrition.extensions import db
import random

class HealthTrackingService:
    """Simplified health tracking service without third-party integrations"""
    
    def __init__(self):
        pass
    
    def create_sample_data(self, user_id, days_back=7):
        """Create sample health data for demonstration"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        # Sample data types with realistic ranges
        data_types = {
            'steps': {'min': 5000, 'max': 15000, 'unit': 'steps'},
            'calories_burned': {'min': 1800, 'max': 2500, 'unit': 'calories'},
            'active_minutes': {'min': 20, 'max': 120, 'unit': 'minutes'},
            'sleep_hours': {'min': 6, 'max': 9, 'unit': 'hours'}
        }
        
        current_date = start_date
        while current_date <= end_date:
            for data_type, config in data_types.items():
                # Check if data already exists
                existing = HealthImport.query.filter_by(
                    user_id=user_id,
                    source='manual',
                    import_type=data_type,
                    date=current_date
                ).first()
                
                if not existing:
                    # Generate realistic sample data
                    if data_type == 'sleep_hours':
                        value = round(random.uniform(config['min'], config['max']), 1)
                    else:
                        value = random.randint(config['min'], config['max'])
                    
                    health_import = HealthImport(
                        user_id=user_id,
                        source='manual',
                        import_type=data_type,
                        date=current_date,
                        value=value,
                        unit=config['unit']
                    )
                    db.session.add(health_import)
            
            current_date += timedelta(days=1)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating sample data: {e}")
            return False
    
    def get_health_summary(self, user_id, days=7):
        """Get health data summary for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        health_data = HealthImport.query.filter(
            HealthImport.user_id == user_id,
            HealthImport.date >= start_date,
            HealthImport.date <= end_date
        ).all()
        
        # Group by type and calculate averages
        summary = {}
        data_by_type = {}
        
        for item in health_data:
            if item.import_type not in data_by_type:
                data_by_type[item.import_type] = []
            data_by_type[item.import_type].append(item.value)
        
        for data_type, values in data_by_type.items():
            if values:
                summary[data_type] = {
                    'average': round(sum(values) / len(values), 1),
                    'total': sum(values) if data_type in ['steps', 'calories_burned'] else None,
                    'count': len(values)
                }
        
        return summary
    
    def add_manual_entry(self, user_id, data_type, value, unit, date=None):
        """Add manual health data entry"""
        if date is None:
            date = datetime.now().date()
        
        # Remove existing entry for the same date and type
        existing = HealthImport.query.filter_by(
            user_id=user_id,
            source='manual',
            import_type=data_type,
            date=date
        ).first()
        
        if existing:
            existing.value = value
            existing.unit = unit
        else:
            health_import = HealthImport(
                user_id=user_id,
                source='manual',
                import_type=data_type,
                date=date,
                value=value,
                unit=unit
            )
            db.session.add(health_import)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error adding manual entry: {e}")
            return False
