from datetime import datetime
from nutrition.extensions import db

class FitbitToken(db.Model):
    __tablename__ = 'fitbit_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HealthImport(db.Model):
    __tablename__ = 'health_imports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    source = db.Column(db.String(20), nullable=False)  # apple_health, fitbit, manual
    import_type = db.Column(db.String(20), nullable=False)  # steps, calories, heart_rate
    
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'source', 'import_type', 'date', name='unique_health_data'),
    )
