from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class MealUploadForm(FlaskForm):
    meal_name = StringField('Meal Name', validators=[Optional(), Length(max=100)])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], validators=[DataRequired()])
    
    meal_image = FileField('Meal Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class MealItemForm(FlaskForm):
    food_name = StringField('Food Name', validators=[DataRequired(), Length(max=100)])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.1, max=1000)])
    unit = SelectField('Unit', choices=[
        ('g', 'Grams'),
        ('serving', 'Serving'),
        ('cup', 'Cup'),
        ('piece', 'Piece'),
        ('slice', 'Slice'),
        ('tbsp', 'Tablespoon'),
        ('tsp', 'Teaspoon')
    ], default='g')
    
    calories_per_unit = FloatField('Calories per Unit', validators=[DataRequired(), NumberRange(min=0)])
    protein_per_unit = FloatField('Protein per Unit (g)', validators=[Optional(), NumberRange(min=0)])
    carbs_per_unit = FloatField('Carbs per Unit (g)', validators=[Optional(), NumberRange(min=0)])
    fat_per_unit = FloatField('Fat per Unit (g)', validators=[Optional(), NumberRange(min=0)])

class FoodSearchForm(FlaskForm):
    query = StringField('Search Food', validators=[DataRequired(), Length(min=2, max=50)])

class MealEditForm(FlaskForm):
    meal_name = StringField('Meal Name', validators=[DataRequired(), Length(max=100)])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
