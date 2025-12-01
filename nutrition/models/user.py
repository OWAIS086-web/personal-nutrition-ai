from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from nutrition.extensions import db
import secrets
import json

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
     # Nutrition goals
    calorie_goal = db.Column(db.Integer, default=2000)
    protein_goal = db.Column(db.Integer, default=150)
    carbs_goal = db.Column(db.Integer, default=250)
    fat_goal = db.Column(db.Integer, default=70)
    
    # Preferences
    units = db.Column(db.String(10), default='metric')  # metric or imperial
    dietary_preferences = db.Column(db.Text)  # JSON string of preferences
    theme = db.Column(db.String(10), default='light')  # light or dark
    
    # Profile
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    activity_level = db.Column(db.String(20), default='moderate')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    meals = db.relationship('Meal', backref='user', lazy=True, cascade='all, delete-orphan')
    fitbit_tokens = db.relationship('FitbitToken', backref='user', lazy=True, cascade='all, delete-orphan')
    health_imports = db.relationship('HealthImport', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_logs = db.relationship('AILog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    
    allergies = db.Column(db.Text)  # JSON array of allergies
    health_goals = db.Column(db.Text)  # JSON array of goals
    notification_preferences = db.Column(db.Text)  # JSON object of notification settings
    
    data_export_requested = db.Column(db.DateTime)
    account_deletion_requested = db.Column(db.DateTime)
    privacy_settings = db.Column(db.Text)  # JSON object
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a secure password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if the reset token is valid and not expired"""
        return (self.reset_token == token and 
                self.reset_token_expires and 
                self.reset_token_expires > datetime.utcnow())
    
    def clear_reset_token(self):
        """Clear the reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def get_dietary_preferences(self):
        """Get dietary preferences as a list"""
        if self.dietary_preferences:
            return json.loads(self.dietary_preferences)
        return []
    
    def set_dietary_preferences(self, preferences):
        """Set dietary preferences from a list"""
        self.dietary_preferences = json.dumps(preferences)
    
    def get_allergies(self):
        """Get allergies as a list"""
        if self.allergies:
            return json.loads(self.allergies)
        return []
    
    def set_allergies(self, allergies):
        """Set allergies from a list"""
        self.allergies = json.dumps(allergies)
    
    def get_health_goals(self):
        """Get health goals as a list"""
        if self.health_goals:
            try:
                parsed = json.loads(self.health_goals)
                # Handle case where it's stored as a string instead of array
                if isinstance(parsed, str):
                    return [parsed]
                elif isinstance(parsed, list):
                    return parsed
                else:
                    return []
            except (json.JSONDecodeError, TypeError):
                # If JSON parsing fails, treat as empty
                return []
        return []
    
    def set_health_goals(self, goals):
        """Set health goals from a list"""
        self.health_goals = json.dumps(goals)
    
    def get_notification_preferences(self):
        """Get notification preferences as a dict"""
        if self.notification_preferences:
            return json.loads(self.notification_preferences)
        return {
            'daily_tips': True,
            'meal_reminders': True,
            'weekly_reports': True,
            'goal_achievements': True
        }
    
    def set_notification_preferences(self, preferences):
        """Set notification preferences from a dict"""
        self.notification_preferences = json.dumps(preferences)
    
    def get_privacy_settings(self):
        """Get privacy settings as a dict"""
        if self.privacy_settings:
            return json.loads(self.privacy_settings)
        return {
            'data_sharing': False,
            'analytics': True,
            'marketing_emails': False
        }
    
    def set_privacy_settings(self, settings):
        """Set privacy settings from a dict"""
        self.privacy_settings = json.dumps(settings)
    
    def request_data_export(self):
        """Mark account for data export"""
        self.data_export_requested = datetime.utcnow()
    
    def request_account_deletion(self):
        """Mark account for deletion (30-day grace period)"""
        self.account_deletion_requested = datetime.utcnow()
        self.is_active = False
    
    def cancel_account_deletion(self):
        """Cancel account deletion request"""
        self.account_deletion_requested = None
        self.is_active = True
    
    @property
    def deletion_deadline(self):
        """Get the deadline for account deletion"""
        if self.account_deletion_requested:
            return self.account_deletion_requested + timedelta(days=30)
        return None
    
    def export_user_data(self):
        """Export all user data for GDPR compliance"""
        data = {
            'profile': {
                'email': self.email,
                'name': self.full_name,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_login': self.last_login.isoformat() if self.last_login else None,
            },
            'preferences': {
                'units': self.units,
                'theme': self.theme,
                'dietary_preferences': self.get_dietary_preferences(),
                'allergies': self.get_allergies(),
                'health_goals': self.get_health_goals(),
                'notification_preferences': self.get_notification_preferences(),
                'privacy_settings': self.get_privacy_settings(),
            },
            'physical_stats': {
                'height': self.height,
                'weight': self.weight,
                'activity_level': self.activity_level,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            },
            'meals': [meal.to_dict() for meal in self.meals],
            'ai_interactions': [log.to_dict() for log in self.ai_logs],
        }
        return data
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'units': self.units,
            'theme': self.theme,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
