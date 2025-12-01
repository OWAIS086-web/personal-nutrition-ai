from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from nutrition.extensions import limiter
from nutrition.services.ai_coach import AICoachService
from nutrition.models.meal import Meal, MealItem
from nutrition.models.user import User
from sqlalchemy import func
from datetime import datetime, timedelta
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/update-theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    theme = data.get('theme')
    
    if theme in ['light', 'dark']:
        current_user.theme = theme
        from nutrition.extensions import db
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid theme'}), 400

@api_bp.route('/nutrition-stats', methods=['GET'])
@login_required
def get_nutrition_stats():
    """Get nutrition statistics for charts"""
    days = request.args.get('days', 7, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        Meal.created_at >= start_date,
        Meal.created_at <= end_date
    ).all()
    
    # Calculate daily totals
    daily_stats = {}
    for meal in meals:
        date_key = meal.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'date': date_key,
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0
            }
        
        daily_stats[date_key]['calories'] += meal.total_calories or 0
        daily_stats[date_key]['protein'] += meal.total_protein or 0
        daily_stats[date_key]['carbs'] += meal.total_carbs or 0
        daily_stats[date_key]['fat'] += meal.total_fat or 0
    
    return jsonify({
        'daily_stats': list(daily_stats.values()),
        'total_meals': len(meals),
        'avg_calories': sum(meal.total_calories or 0 for meal in meals) / max(len(meals), 1)
    })

@api_bp.route('/goal-progress', methods=['GET'])
@login_required
def get_goal_progress():
    """Get goal progress data"""
    today = datetime.utcnow().date()
    today_meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        func.date(Meal.created_at) == today
    ).all()
    
    today_calories = sum(meal.total_calories or 0 for meal in today_meals)
    today_protein = sum(meal.total_protein or 0 for meal in today_meals)
    today_carbs = sum(meal.total_carbs or 0 for meal in today_meals)
    today_fat = sum(meal.total_fat or 0 for meal in today_meals)
    
    calorie_goal = current_user.calorie_goal or 2000
    protein_goal = current_user.protein_goal or 150
    carb_goal = current_user.carbs_goal or 250   # ✅ fixed here
    fat_goal = current_user.fat_goal or 65
    
    return jsonify({
        'calories': {
            'current': today_calories,
            'goal': calorie_goal,
            'percentage': min((today_calories / calorie_goal) * 100, 100) if calorie_goal > 0 else 0
        },
        'protein': {
            'current': today_protein,
            'goal': protein_goal,
            'percentage': min((today_protein / protein_goal) * 100, 100) if protein_goal > 0 else 0
        },
        'carbs': {
            'current': today_carbs,
            'goal': carb_goal,
            'percentage': min((today_carbs / carb_goal) * 100, 100) if carb_goal > 0 else 0
        },
        'fat': {
            'current': today_fat,
            'goal': fat_goal,
            'percentage': min((today_fat / fat_goal) * 100, 100) if fat_goal > 0 else 0
        }
    })


@api_bp.route('/meal-frequency', methods=['GET'])
@login_required
def get_meal_frequency():
    """Get meal frequency analysis"""
    days = request.args.get('days', 7, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        Meal.created_at >= start_date,
        Meal.created_at <= end_date
    ).all()
    
    # Count meals by type
    meal_types = {}
    for meal in meals:
        meal_type = meal.meal_type or 'Other'
        meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
    
    # Count meals by hour
    hourly_frequency = {}
    for meal in meals:
        hour = meal.created_at.hour
        hourly_frequency[hour] = hourly_frequency.get(hour, 0) + 1
    
    return jsonify({
        'meal_types': meal_types,
        'hourly_frequency': hourly_frequency,
        'total_meals': len(meals),
        'avg_meals_per_day': len(meals) / max(days, 1)
    })

@api_bp.route('/wearable-integration', methods=['GET'])
@login_required
def get_wearable_integration():
    """Get wearable integration data (simplified without Fitbit)"""
    return jsonify({
        'connected_devices': [],
        'health_data': {
            'steps': 0,
            'calories_burned': 0,
            'active_minutes': 0,
            'sleep_hours': 0
        },
        'message': 'Wearable integrations have been simplified. Focus on nutrition tracking.'
    })

@api_bp.route('/analyze', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def analyze_meal():
    """Analyze meal with AI coaching feedback"""
    data = request.get_json()
    
    if not data or 'meal_id' not in data:
        return jsonify({'error': 'Meal ID required'}), 400
    
    # Get meal data
    meal = Meal.query.filter_by(id=data['meal_id'], user_id=current_user.id).first()
    if not meal:
        return jsonify({'error': 'Meal not found'}), 404
    
    # Prepare meal data for AI analysis
    meal_data = {
        'name': meal.name,
        'meal_type': meal.meal_type,
        'calories': meal.total_calories,
        'protein': meal.total_protein,
        'carbs': meal.total_carbs,
        'fat': meal.total_fat,
        'foods': [item.food_name for item in meal.items]
    }
    
    # Get AI analysis
    ai_coach = AICoachService()
    result = ai_coach.get_meal_analysis(current_user, meal_data)
    
    return jsonify(result)

@api_bp.route('/coach', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def get_coach_tip():
    """Get personalized coaching tip"""
    data = request.get_json()
    tip_type = data.get('type', 'daily') if data else 'daily'
    
    ai_coach = AICoachService()
    
    if tip_type == 'daily':
        result = ai_coach.get_daily_tip(current_user)
    elif tip_type == 'weekly':
        result = ai_coach.get_weekly_insights(current_user)
    elif tip_type == 'goals':
        result = ai_coach.get_goal_coaching(current_user)
    else:
        result = ai_coach.get_daily_tip(current_user)
    
    return jsonify(result)

@api_bp.route('/coach/daily-tip', methods=['GET'])
@login_required
@limiter.limit("20 per hour")
def get_daily_tip():
    """Get daily nutrition tip"""
    ai_coach = AICoachService()
    result = ai_coach.get_daily_tip(current_user)
    return jsonify(result)

@api_bp.route('/coach/weekly-insights', methods=['GET'])
@login_required
@limiter.limit("10 per hour")
def get_weekly_insights():
    """Get weekly nutrition insights"""
    ai_coach = AICoachService()
    result = ai_coach.get_weekly_insights(current_user)
    return jsonify(result)

@api_bp.route('/coach/goal-coaching', methods=['GET'])
@login_required
@limiter.limit("10 per hour")
def get_goal_coaching():
    """Get goal-specific coaching"""
    ai_coach = AICoachService()
    result = ai_coach.get_goal_coaching(current_user)
    return jsonify(result)

@api_bp.route('/coach/meal-feedback', methods=['POST'])
@login_required
@limiter.limit("15 per hour")
def get_meal_feedback():
    """Get AI feedback on a specific meal"""
    data = request.get_json()
    
    if not data or 'meal_id' not in data:
        return jsonify({'error': 'Meal ID required'}), 400
    
    meal = Meal.query.filter_by(id=data['meal_id'], user_id=current_user.id).first()
    if not meal:
        return jsonify({'error': 'Meal not found'}), 404
    
    meal_data = {
        'name': meal.name,
        'meal_type': meal.meal_type,
        'calories': meal.total_calories,
        'protein': meal.total_protein,
        'carbs': meal.total_carbs,
        'fat': meal.total_fat,
        'foods': [item.food_name for item in meal.items]
    }
    
    ai_coach = AICoachService()
    result = ai_coach.get_meal_analysis(current_user, meal_data)
    
    return jsonify(result)
