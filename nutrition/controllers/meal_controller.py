import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from nutrition.extensions import db
from nutrition.models.meal import Meal, MealItem
from nutrition.forms.meal_forms import MealUploadForm, MealItemForm, FoodSearchForm, MealEditForm
from nutrition.services.food_vision import FoodVisionService
from nutrition.services.nutrition_calc import NutritionCalculator

meal_bp = Blueprint('meal', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_meal_image(file):
    """Save uploaded meal image and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None

@meal_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = MealUploadForm()
    
    if form.validate_on_submit():
        # Save image if provided
        image_filename = None
        if form.meal_image.data:
            image_filename = save_meal_image(form.meal_image.data)
        
        # Create new meal with temporary name (will be updated after AI analysis)
        meal = Meal(
            user_id=current_user.id,
            name=form.meal_name.data or f"{form.meal_type.data.title()} Meal",
            meal_type=form.meal_type.data,
            image_path=image_filename,
            meal_date=date.today()
        )
        
        db.session.add(meal)
        db.session.flush()  # Get meal ID
        
        # If image was uploaded, analyze it
        detected_foods = []
        if image_filename:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
            analysis_result = FoodVisionService.analyze_image(image_path)
            
            if analysis_result['success']:
                detected_foods = analysis_result['foods']
                
                # Auto-generate meal name from detected foods
                if detected_foods:
                    # Take up to 3 food names for the meal name
                    food_names = [food['food_name'] for food in detected_foods[:3]]
                    if len(food_names) == 1:
                        meal.name = food_names[0]
                    elif len(food_names) == 2:
                        meal.name = f"{food_names[0]} & {food_names[1]}"
                    else:
                        meal.name = f"{food_names[0]}, {food_names[1]} & more"
                else:
                    # Fallback if no foods detected
                    meal.name = f"{form.meal_type.data.title()} Meal"
                
                flash(analysis_result['message'], 'success')
            else:
                # Fallback if analysis failed
                meal.name = f"{form.meal_type.data.title()} Meal"
                flash(analysis_result['message'], 'warning')
        else:
            # No image uploaded, use meal type as name
            meal.name = f"{form.meal_type.data.title()} Meal"
        
        db.session.commit()
        
        # Redirect to edit page with detected foods
        return redirect(url_for('meal.edit', meal_id=meal.id, detected_foods=len(detected_foods)))
    
    return render_template('meals/upload.html', form=form)

@meal_bp.route('/edit/<int:meal_id>')
@login_required
def edit(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    
    # Get detected foods if coming from upload
    detected_foods = []
    if request.args.get('detected_foods'):
        if meal.image_path:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], meal.image_path)
            analysis_result = FoodVisionService.analyze_image(image_path)
            if analysis_result['success']:
                detected_foods = analysis_result['foods']
                
                # Check if meal already has items
                existing_items_count = MealItem.query.filter_by(meal_id=meal.id).count()
                print(f"DEBUG: Meal {meal.id} has {existing_items_count} existing items")
                
                # Auto-add detected foods to meal if no items exist yet
                if existing_items_count == 0 and detected_foods:
                    print(f"DEBUG: Adding {len(detected_foods)} detected foods to meal {meal.id}")
                    
                    for food in detected_foods:
                        # Calculate nutrition per gram
                        nutrition_per_gram = {
                            'calories': food['nutrition_per_100g']['calories'] / 100,
                            'protein': food['nutrition_per_100g']['protein'] / 100,
                            'carbs': food['nutrition_per_100g']['carbs'] / 100,
                            'fat': food['nutrition_per_100g']['fat'] / 100
                        }
                        
                        print(f"DEBUG: Adding food: {food['food_name']}, {food['estimated_grams']}g")
                        print(f"DEBUG: Nutrition per gram: {nutrition_per_gram}")
                        
                        item = MealItem(
                            meal_id=meal.id,
                            food_name=food['food_name'],
                            quantity=float(food['estimated_grams']),
                            unit='g',
                            calories_per_unit=nutrition_per_gram['calories'],
                            protein_per_unit=nutrition_per_gram['protein'],
                            carbs_per_unit=nutrition_per_gram['carbs'],
                            fat_per_unit=nutrition_per_gram['fat']
                        )
                        db.session.add(item)
                    
                    # Commit items to database first
                    db.session.commit()
                    
                    print(f"DEBUG: After commit, meal has {len(meal.items)} items")
                    
                    # Now calculate totals after items are in the database
                    meal.calculate_totals()
                    
                    print(f"DEBUG: After calculate_totals:")
                    print(f"  Calories: {meal.total_calories}")
                    print(f"  Protein: {meal.total_protein}")
                    print(f"  Carbs: {meal.total_carbs}")
                    print(f"  Fat: {meal.total_fat}")
                    
                    # Commit the updated totals
                    db.session.commit()
                    
                    print(f"DEBUG: After final commit:")
                    print(f"  Calories: {meal.total_calories}")
                    print(f"  Protein: {meal.total_protein}")
                    print(f"  Carbs: {meal.total_carbs}")
                    print(f"  Fat: {meal.total_fat}")
                    
                    flash('AI detected foods have been added to your meal!', 'success')
    
    form = MealEditForm(obj=meal)
    item_form = MealItemForm()
    search_form = FoodSearchForm()
    
    return render_template('meals/edit.html', 
                         meal=meal, 
                         form=form,
                         item_form=item_form, 
                         search_form=search_form,
                         detected_foods=detected_foods)

@meal_bp.route('/save/<int:meal_id>', methods=['POST'])
@login_required
def save_meal(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    
    # Update meal details
    data = request.get_json()
    meal.name = data.get('name', meal.name)
    meal.meal_type = data.get('meal_type', meal.meal_type)
    
    # Clear existing items
    MealItem.query.filter_by(meal_id=meal.id).delete()
    
    # Add new items
    for item_data in data.get('items', []):
        item = MealItem(
            meal_id=meal.id,
            food_name=item_data['food_name'],
            quantity=float(item_data['quantity']),
            unit=item_data['unit'],
            calories_per_unit=float(item_data['calories_per_unit']),
            protein_per_unit=float(item_data.get('protein_per_unit', 0)),
            carbs_per_unit=float(item_data.get('carbs_per_unit', 0)),
            fat_per_unit=float(item_data.get('fat_per_unit', 0))
        )
        db.session.add(item)
    
    # Recalculate meal totals
    meal.calculate_totals()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Meal saved successfully!'})

@meal_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    meals = Meal.query.filter_by(user_id=current_user.id)\
                     .order_by(Meal.meal_date.desc(), Meal.created_at.desc())\
                     .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('meals/history.html', meals=meals)

@meal_bp.route('/view/<int:meal_id>')
@login_required
def view(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    return render_template('meals/view.html', meal=meal)

@meal_bp.route('/delete/<int:meal_id>', methods=['POST'])
@login_required
def delete(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    
    # Delete image file if exists
    if meal.image_path:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], meal.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(meal)
    db.session.commit()
    
    flash('Meal deleted successfully!', 'success')
    return redirect(url_for('meal.history'))

# API Routes
@meal_bp.route('/api/search-food', methods=['POST'])
@login_required
def api_search_food():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify({'foods': []})
    
    foods = FoodVisionService.search_food(query)
    return jsonify({'foods': foods})

@meal_bp.route('/api/add-item', methods=['POST'])
@login_required
def api_add_item():
    data = request.get_json()
    meal_id = data.get('meal_id')
    
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    
    # Create new meal item
    item = MealItem(
        meal_id=meal.id,
        food_name=data['food_name'],
        quantity=float(data['quantity']),
        unit=data['unit'],
        calories_per_unit=float(data['calories_per_unit']),
        protein_per_unit=float(data.get('protein_per_unit', 0)),
        carbs_per_unit=float(data.get('carbs_per_unit', 0)),
        fat_per_unit=float(data.get('fat_per_unit', 0))
    )
    
    db.session.add(item)
    meal.calculate_totals()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'item': item.to_dict(),
        'meal_totals': {
            'calories': meal.total_calories,
            'protein': meal.total_protein,
            'carbs': meal.total_carbs,
            'fat': meal.total_fat
        }
    })

@meal_bp.route('/api/update-item/<int:item_id>', methods=['POST'])
@login_required
def api_update_item(item_id):
    item = MealItem.query.join(Meal).filter(
        MealItem.id == item_id,
        Meal.user_id == current_user.id
    ).first_or_404()
    
    data = request.get_json()
    
    item.quantity = float(data['quantity'])
    item.unit = data['unit']
    item.calories_per_unit = float(data['calories_per_unit'])
    item.protein_per_unit = float(data.get('protein_per_unit', 0))
    item.carbs_per_unit = float(data.get('carbs_per_unit', 0))
    item.fat_per_unit = float(data.get('fat_per_unit', 0))
    
    item.meal.calculate_totals()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'item': item.to_dict(),
        'meal_totals': {
            'calories': item.meal.total_calories,
            'protein': item.meal.total_protein,
            'carbs': item.meal.total_carbs,
            'fat': item.meal.total_fat
        }
    })

@meal_bp.route('/api/delete-item/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_item(item_id):
    item = MealItem.query.join(Meal).filter(
        MealItem.id == item_id,
        Meal.user_id == current_user.id
    ).first_or_404()
    
    meal = item.meal
    db.session.delete(item)
    meal.calculate_totals()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'meal_totals': {
            'calories': meal.total_calories,
            'protein': meal.total_protein,
            'carbs': meal.total_carbs,
            'fat': meal.total_fat
        }
    })

@meal_bp.route('/api/recent')
@login_required
def api_recent_meals():
    """Get recent meals for dashboard"""
    limit = request.args.get('limit', 5, type=int)
    
    meals = Meal.query.filter_by(user_id=current_user.id)\
                     .order_by(Meal.meal_date.desc(), Meal.created_at.desc())\
                     .limit(limit).all()
    
    return jsonify({
        'success': True,
        'meals': [meal.to_dict() for meal in meals]
    })
