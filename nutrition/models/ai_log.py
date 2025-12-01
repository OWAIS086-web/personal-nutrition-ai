from datetime import datetime
from nutrition.extensions import db

class AILog(db.Model):
    __tablename__ = 'ai_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    request_type = db.Column(db.String(50), nullable=False)  # coach_tip, meal_analysis, etc.
    prompt = db.Column(db.Text)
    response = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_type': self.request_type,
            'response': self.response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
