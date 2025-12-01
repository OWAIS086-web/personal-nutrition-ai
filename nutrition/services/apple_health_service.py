from datetime import datetime, timedelta
from nutrition.models.wearable import HealthImport
from nutrition.extensions import db
import json

class AppleHealthService:
    """
    Apple Health integration service
    Note: This is a simplified implementation. In production, you would need
    to use HealthKit on iOS or process exported Health data files.
    """
    
    def __init__(self):
        pass
    
    def process_health_export(self, user_id, export_data):
        """Process Apple Health export XML/JSON data"""
        # This would parse the actual Health export file
        # For now, we'll simulate processing
        
        try:
            if isinstance(export_data, str):
                data = json.loads(export_data)
            else:
                data = export_data
            
            success = True
            
            # Process different health metrics
            for record in data.get('health_records', []):
                if not self._import_health_record(user_id, record):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"Apple Health processing error: {e}")
            return False
    
    def _import_health_record(self, user_id, record):
        """Import individual health record"""
        try:
            # Map Apple Health types to our system
            type_mapping = {
                'HKQuantityTypeIdentifierStepCount': 'steps',
                'HKQuantityTypeIdentifierActiveEnergyBurned': 'calories',
                'HKQuantityTypeIdentifierDistanceWalkingRunning': 'distance',
                'HKQuantityTypeIdentifierHeartRate': 'heart_rate',
                'HKQuantityTypeIdentifierSleepAnalysis': 'sleep_minutes'
            }
            
            health_type = type_mapping.get(record.get('type'))
            if not health_type:
                return True  # Skip unknown types
            
            date = datetime.strptime(record['date'], '%Y-%m-%d').date()
            value = float(record['value'])
            unit = record.get('unit', '')
            
            # Check if record already exists
            existing = HealthImport.query.filter_by(
                user_id=user_id,
                source='apple_health',
                import_type=health_type,
                date=date
            ).first()
            
            if existing:
                existing.value = value
                existing.unit = unit
            else:
                health_import = HealthImport(
                    user_id=user_id,
                    source='apple_health',
                    import_type=health_type,
                    date=date,
                    value=value,
                    unit=unit
                )
                db.session.add(health_import)
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Health record import error: {e}")
            db.session.rollback()
            return False
    
    def create_sample_data(self, user_id, days_back=7):
        """Create sample Apple Health data for testing"""
        import random
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        data_types = [
            ('steps', 'steps', lambda: random.randint(4000, 12000)),
            ('calories', 'calories', lambda: random.randint(1600, 2200)),
            ('distance', 'km', lambda: round(random.uniform(2.5, 8.0), 2)),
            ('heart_rate', 'bpm', lambda: random.randint(55, 95)),
            ('sleep_minutes', 'minutes', lambda: random.randint(300, 480))
        ]
        
        current_date = start_date
        while current_date <= end_date:
            for data_type, unit, value_func in data_types:
                existing = HealthImport.query.filter_by(
                    user_id=user_id,
                    source='apple_health',
                    import_type=data_type,
                    date=current_date
                ).first()
                
                if not existing:
                    health_import = HealthImport(
                        user_id=user_id,
                        source='apple_health',
                        import_type=data_type,
                        date=current_date,
                        value=value_func(),
                        unit=unit
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
