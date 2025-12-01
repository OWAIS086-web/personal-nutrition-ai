from datetime import datetime
from nutrition.extensions import db

class Meal(db.Model):
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    image_path = db.Column(db.String(255))
    
    # Totals (calculated from meal items)
    total_calories = db.Column(db.Float, default=0)
    total_protein = db.Column(db.Float, default=0)
    total_carbs = db.Column(db.Float, default=0)
    total_fat = db.Column(db.Float, default=0)
    
    # Timestamps
    meal_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('MealItem', backref='meal', lazy=True, cascade='all, delete-orphan')
    
    def calculate_totals(self):
        """Recalculate totals from meal items"""
        self.total_calories = round(sum(item.calories for item in self.items), 1)
        self.total_protein = round(sum(item.protein for item in self.items), 1)
        self.total_carbs = round(sum(item.carbs for item in self.items), 1)
        self.total_fat = round(sum(item.fat for item in self.items), 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'meal_type': self.meal_type,
            'meal_date': self.meal_date.isoformat() if self.meal_date else None,
            'total_calories': round(self.total_calories or 0, 1),
            'total_protein': round(self.total_protein or 0, 1),
            'total_carbs': round(self.total_carbs or 0, 1),
            'total_fat': round(self.total_fat or 0, 1),
            'items': [item.to_dict() for item in self.items]
        }

class MealItem(db.Model):
    __tablename__ = 'meal_items'
    
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    
    food_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False, default='serving')
    
    # Nutritional info per unit
    calories_per_unit = db.Column(db.Float, nullable=False)
    protein_per_unit = db.Column(db.Float, default=0)
    carbs_per_unit = db.Column(db.Float, default=0)
    fat_per_unit = db.Column(db.Float, default=0)
    
    @property
    def calories(self):
        return round(self.calories_per_unit * self.quantity, 1)
    
    @property
    def protein(self):
        return round(self.protein_per_unit * self.quantity, 1)
    
    @property
    def carbs(self):
        return round(self.carbs_per_unit * self.quantity, 1)
    
    @property
    def fat(self):
        return round(self.fat_per_unit * self.quantity, 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_name': self.food_name,
            'quantity': round(self.quantity, 1),
            'unit': self.unit,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat
        }
