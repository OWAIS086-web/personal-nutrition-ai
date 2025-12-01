from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from nutrition.models.meal import Meal, MealItem
from nutrition.models.wearable import HealthImport
from nutrition.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/api/nutrition-stats')
@login_required
def nutrition_stats():
    """Get nutrition statistics for specified time period"""
    days = int(request.args.get('days', 7))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get meals in date range using meal_date field
    meals = db.session.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.meal_date >= start_date,
        Meal.meal_date <= end_date
    ).all()
    
    # Calculate daily totals
    daily_stats = {}
    for meal in meals:
        date_key = meal.meal_date.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'meals': 0
            }
        
        daily_stats[date_key]['calories'] += meal.total_calories or 0
        daily_stats[date_key]['protein'] += meal.total_protein or 0
        daily_stats[date_key]['carbs'] += meal.total_carbs or 0
        daily_stats[date_key]['fat'] += meal.total_fat or 0
        daily_stats[date_key]['meals'] += 1
    
    # Fill in missing dates with zeros
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'meals': 0
            }
        current_date += timedelta(days=1)
    
    # Calculate averages, highest, and lowest
    total_days = len(daily_stats)
    totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'meals': 0}
    
    # Get non-zero values for calculating highest/lowest
    non_zero_values = {
        'calories': [stats['calories'] for stats in daily_stats.values() if stats['calories'] > 0],
        'protein': [stats['protein'] for stats in daily_stats.values() if stats['protein'] > 0],
        'carbs': [stats['carbs'] for stats in daily_stats.values() if stats['carbs'] > 0],
        'fat': [stats['fat'] for stats in daily_stats.values() if stats['fat'] > 0]
    }
    
    for stats in daily_stats.values():
        for key in totals:
            totals[key] += stats[key]
    
    averages = {key: round(totals[key] / total_days, 1) if total_days > 0 else 0.0 
                for key in totals}
    
    highest = {key: round(max(values), 1) if values else 0.0 
               for key, values in non_zero_values.items()}
    
    lowest = {key: round(min(values), 1) if values else 0.0 
              for key, values in non_zero_values.items()}
    
    return jsonify({
        'success': True,
        'daily_stats': daily_stats,
        'totals': totals,
        'averages': averages,
        'highest': highest,
        'lowest': lowest,
        'period': f'{days} days'
    })

@dashboard_bp.route('/api/goal-progress')
@login_required
def goal_progress():
    """Get progress towards user's nutrition goals"""
    # Get user's daily targets using correct field names
    daily_calories = current_user.calorie_goal or 2000
    daily_protein = current_user.protein_goal or 120
    daily_carbs = current_user.carbs_goal or 250
    daily_fat = current_user.fat_goal or 67
    
    # Get today's totals using meal_date
    today = datetime.now().date()
    today_meals = db.session.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.meal_date == today
    ).all()
    
    today_totals = {
        'calories': sum(meal.total_calories or 0 for meal in today_meals),
        'protein': sum(meal.total_protein or 0 for meal in today_meals),
        'carbs': sum(meal.total_carbs or 0 for meal in today_meals),
        'fat': sum(meal.total_fat or 0 for meal in today_meals)
    }
    
    # Calculate progress percentages
    progress = {
        'calories': round((today_totals['calories'] / daily_calories) * 100, 1) if daily_calories > 0 else 0.0,
        'protein': round((today_totals['protein'] / daily_protein) * 100, 1) if daily_protein > 0 else 0.0,
        'carbs': round((today_totals['carbs'] / daily_carbs) * 100, 1) if daily_carbs > 0 else 0.0,
        'fat': round((today_totals['fat'] / daily_fat) * 100, 1) if daily_fat > 0 else 0.0
    }
    
    # Round today's totals to 1 decimal place
    today_totals = {
        'calories': round(today_totals['calories'], 1),
        'protein': round(today_totals['protein'], 1),
        'carbs': round(today_totals['carbs'], 1),
        'fat': round(today_totals['fat'], 1)
    }
    
    return jsonify({
        'success': True,
        'current': today_totals,
        'targets': {
            'calories': daily_calories,
            'protein': daily_protein,
            'carbs': daily_carbs,
            'fat': daily_fat
        },
        'progress': progress
    })

@dashboard_bp.route('/api/meal-frequency')
@login_required
def meal_frequency():
    """Get meal frequency analysis"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    meals = db.session.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.meal_date >= start_date,
        Meal.meal_date <= end_date
    ).all()
    
    # Analyze meal timing
    meal_times = {'breakfast': 0, 'lunch': 0, 'dinner': 0, 'snack': 0}
    hourly_distribution = {str(i): 0 for i in range(24)}
    
    for meal in meals:
        meal_type = meal.meal_type or 'snack'
        if meal_type in meal_times:
            meal_times[meal_type] += 1
        
        # Use created_at for hour analysis since meal_date doesn't have time
        hour = meal.created_at.hour
        hourly_distribution[str(hour)] += 1
    
    return jsonify({
        'success': True,
        'meal_types': meal_times,
        'hourly_distribution': hourly_distribution,
        'total_meals': len(meals),
        'period_days': days
    })

@dashboard_bp.route('/api/wearable-integration')
@login_required
def wearable_integration():
    """Get integrated wearable data for dashboard"""
    days = int(request.args.get('days', 7))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get health data from wearables
    health_data = db.session.query(HealthImport).filter(
        HealthImport.user_id == current_user.id,
        HealthImport.date >= start_date,
        HealthImport.date <= end_date
    ).all()
    
    # Organize by type and date
    organized_data = {}
    for record in health_data:
        data_type = record.import_type
        date_key = record.date.strftime('%Y-%m-%d')
        
        if data_type not in organized_data:
            organized_data[data_type] = {}
        
        organized_data[data_type][date_key] = {
            'value': record.value,
            'unit': record.unit,
            'source': record.source
        }
    
    return jsonify({
        'success': True,
        'health_data': organized_data,
        'period': f'{days} days'
    })

@dashboard_bp.route('/api/export-data')
@login_required
def export_data():
    """Export user's nutrition data"""
    format_type = request.args.get('format', 'json')
    days = int(request.args.get('days', 30))
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get all user data
    meals = db.session.query(Meal).filter(
        Meal.user_id == current_user.id,
        Meal.meal_date >= start_date,
        Meal.meal_date <= end_date
    ).all()
    
    export_data = []
    for meal in meals:
        meal_items = db.session.query(MealItem).filter(
            MealItem.meal_id == meal.id
        ).all()
        
        export_data.append({
            'date': meal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'meal_type': meal.meal_type,
            'total_calories': meal.total_calories,
            'total_protein': meal.total_protein,
            'total_carbs': meal.total_carbs,
            'total_fat': meal.total_fat,
            'items': [{
                'food_name': item.food_name,
                'quantity': item.quantity,
                'unit': item.unit,
                'calories': item.calories,
                'protein': item.protein,
                'carbs': item.carbs,
                'fat': item.fat
            } for item in meal_items]
        })
    
    if format_type == 'csv':
        # For CSV, flatten the data structure
        csv_data = []
        for meal in export_data:
            for item in meal['items']:
                csv_data.append({
                    'date': meal['date'],
                    'meal_type': meal['meal_type'],
                    'food_name': item['food_name'],
                    'quantity': item['quantity'],
                    'unit': item['unit'],
                    'calories': item['calories'],
                    'protein': item['protein'],
                    'carbs': item['carbs'],
                    'fat': item['fat']
                })
        return jsonify({
            'success': True,
            'format': 'csv',
            'data': csv_data
        })
    
    return jsonify({
        'success': True,
        'format': 'json',
        'data': export_data,
        'period': f'{days} days',
        'total_meals': len(export_data)
    })
