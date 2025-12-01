#!/usr/bin/env python3
"""
Script to populate comprehensive dummy data for Muhammad saeed's dashboard
"""

from datetime import datetime, date, timedelta
import random
from nutrition import create_app
from nutrition.extensions import db
from nutrition.models import User, Meal, MealItem, HealthImport, AILog

def populate_muhammad_dashboard():
    """Populate comprehensive data for Muhammad saeed"""
    app = create_app()
    
    with app.app_context():
        # Find Muhammad's user account
        muhammad = User.query.filter_by(email='awaissaeedsaib@gmail.com').first()
        if not muhammad:
            print("Muhammad's account not found!")
            return
        
        print(f"Found user: {muhammad.full_name}")
        
        # Update Muhammad's profile with complete data
        muhammad.calorie_goal = 2200
        muhammad.protein_goal = 165
        muhammad.carbs_goal = 275
        muhammad.fat_goal = 75
        muhammad.height = 175.0
        muhammad.weight = 70.0
        muhammad.activity_level = 'active'
        muhammad.date_of_birth = date(1995, 3, 10)
        muhammad.set_dietary_preferences(['halal'])
        muhammad.set_allergies([])
        muhammad.set_health_goals(['weight_gain', 'muscle_building', 'improve_energy'])
        
        # Clear existing meals for Muhammad
        Meal.query.filter_by(user_id=muhammad.id).delete()
        HealthImport.query.filter_by(user_id=muhammad.id).delete()
        AILog.query.filter_by(user_id=muhammad.id).delete()
        
        print("Cleared existing data for Muhammad")
        
        # Comprehensive food database with Pakistani/Halal foods
        foods_data = {
            # Pakistani/Desi Foods
            'Chicken Karahi': {'calories': 180, 'protein': 25, 'carbs': 8, 'fat': 6},
            'Basmati Rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
            'Chapati': {'calories': 104, 'protein': 3.1, 'carbs': 18, 'fat': 2.5},
            'Dal (Lentils)': {'calories': 116, 'protein': 9, 'carbs': 20, 'fat': 0.4},
            'Chicken Biryani': {'calories': 200, 'protein': 12, 'carbs': 35, 'fat': 3},
            'Seekh Kebab': {'calories': 250, 'protein': 20, 'carbs': 2, 'fat': 18},
            'Naan': {'calories': 262, 'protein': 9, 'carbs': 45, 'fat': 5},
            'Raita': {'calories': 35, 'protein': 2, 'carbs': 4, 'fat': 1},
            
            # Common Halal Foods
            'Grilled Chicken': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
            'Beef Steak': {'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 19},
            'Fish Curry': {'calories': 150, 'protein': 22, 'carbs': 5, 'fat': 5},
            'Mutton Curry': {'calories': 294, 'protein': 25, 'carbs': 3, 'fat': 21},
            
            # Healthy Options
            'Brown Rice': {'calories': 111, 'protein': 2.6, 'carbs': 23, 'fat': 0.9},
            'Quinoa': {'calories': 120, 'protein': 4.4, 'carbs': 22, 'fat': 1.9},
            'Sweet Potato': {'calories': 86, 'protein': 1.6, 'carbs': 20, 'fat': 0.1},
            'Broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4},
            'Spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4},
            'Almonds': {'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50},
            'Greek Yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
            'Eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11},
            'Banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
            'Oats': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4},
            'Milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1},
            'Dates': {'calories': 282, 'protein': 2.5, 'carbs': 75, 'fat': 0.4},
            'Honey': {'calories': 304, 'protein': 0.3, 'carbs': 82, 'fat': 0},
        }
        
        # Meal templates for different times
        meal_templates = {
            'breakfast': [
                ['Oats', 'Milk', 'Banana', 'Honey'],
                ['Eggs', 'Chapati', 'Milk'],
                ['Greek Yogurt', 'Dates', 'Almonds'],
                ['Chapati', 'Eggs', 'Milk']
            ],
            'lunch': [
                ['Chicken Karahi', 'Basmati Rice', 'Raita'],
                ['Chicken Biryani', 'Raita'],
                ['Grilled Chicken', 'Brown Rice', 'Broccoli'],
                ['Dal (Lentils)', 'Chapati', 'Spinach'],
                ['Fish Curry', 'Basmati Rice']
            ],
            'dinner': [
                ['Seekh Kebab', 'Naan', 'Raita'],
                ['Mutton Curry', 'Basmati Rice'],
                ['Grilled Chicken', 'Sweet Potato', 'Broccoli'],
                ['Beef Steak', 'Quinoa', 'Spinach'],
                ['Dal (Lentils)', 'Chapati']
            ],
            'snack': [
                ['Almonds'],
                ['Greek Yogurt', 'Honey'],
                ['Dates'],
                ['Banana', 'Milk']
            ]
        }
        
        # Create meals for the past 14 days (2 weeks)
        meals_created = 0
        for days_ago in range(14):
            meal_date = date.today() - timedelta(days=days_ago)
            
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                # Skip some snacks randomly
                if meal_type == 'snack' and random.random() > 0.7:
                    continue
                
                # Choose a meal template
                food_items = random.choice(meal_templates[meal_type])
                
                # Create meal
                meal = Meal(
                    user_id=muhammad.id,
                    name=f"{meal_type.title()} - {', '.join(food_items)}",
                    meal_type=meal_type,
                    meal_date=meal_date,
                    created_at=datetime.combine(meal_date, datetime.min.time()) + timedelta(
                        hours=get_meal_hour(meal_type), minutes=random.randint(0, 59)
                    )
                )
                
                db.session.add(meal)
                db.session.flush()
                
                # Add meal items
                for food_name in food_items:
                    food_data = foods_data[food_name]
                    
                    # Realistic serving sizes
                    serving_size = get_serving_size(food_name, meal_type)
                    quantity = serving_size / 100  # Convert to per-100g units
                    
                    meal_item = MealItem(
                        meal_id=meal.id,
                        food_name=food_name,
                        quantity=quantity,
                        unit='100g',
                        calories_per_unit=food_data['calories'],
                        protein_per_unit=food_data['protein'],
                        carbs_per_unit=food_data['carbs'],
                        fat_per_unit=food_data['fat']
                    )
                    
                    db.session.add(meal_item)
                
                # Calculate totals
                db.session.flush()
                meal.calculate_totals()
                meals_created += 1
        
        print(f"Created {meals_created} meals")
        
        # Create comprehensive health data for 30 days
        health_data_created = 0
        for days_ago in range(30):
            data_date = date.today() - timedelta(days=days_ago)
            
            # Steps (varied by day type)
            is_weekend = data_date.weekday() >= 5
            base_steps = 6000 if is_weekend else 8000
            steps = base_steps + random.randint(-2000, 4000)
            
            health_import = HealthImport(
                user_id=muhammad.id,
                source='fitbit',
                import_type='steps',
                date=data_date,
                value=steps,
                unit='steps'
            )
            db.session.add(health_import)
            health_data_created += 1
            
            # Calories burned (correlated with steps)
            calories_burned = 1800 + (steps * 0.04) + random.randint(-200, 300)
            health_import = HealthImport(
                user_id=muhammad.id,
                source='fitbit',
                import_type='calories_burned',
                date=data_date,
                value=calories_burned,
                unit='calories'
            )
            db.session.add(health_import)
            health_data_created += 1
            
            # Heart rate
            heart_rate = random.randint(65, 80)
            health_import = HealthImport(
                user_id=muhammad.id,
                source='fitbit',
                import_type='heart_rate',
                date=data_date,
                value=heart_rate,
                unit='bpm'
            )
            db.session.add(health_import)
            health_data_created += 1
            
            # Weight tracking (slight variations)
            weight_variation = random.uniform(-0.5, 0.5)
            weight = 70.0 + weight_variation
            health_import = HealthImport(
                user_id=muhammad.id,
                source='manual',
                import_type='weight',
                date=data_date,
                value=weight,
                unit='kg'
            )
            db.session.add(health_import)
            health_data_created += 1
        
        print(f"Created {health_data_created} health data points")
        
        # Create AI interaction logs
        ai_responses = [
            "Great job maintaining your calorie goals! Your protein intake is excellent for muscle building.",
            "I notice you're eating well-balanced meals. Consider adding more vegetables to increase fiber intake.",
            "Your Pakistani cuisine choices are nutritious! The combination of dal and rice provides complete proteins.",
            "Excellent work on your fitness goals. Your step count shows consistent activity levels.",
            "Your meal timing is good for metabolism. Keep up the regular eating schedule!",
            "The variety in your diet is impressive. This helps ensure you get all essential nutrients.",
            "Your weight gain progress is steady and healthy. Continue with your current nutrition plan.",
            "Great choice with grilled chicken and vegetables. This supports your muscle-building goals.",
            "Your hydration and meal balance look good. Consider adding more healthy fats like nuts.",
            "Consistent meal logging helps track progress. You're doing great with nutrition awareness!"
        ]
        
        request_types = ['meal_analysis', 'coach_tip', 'nutrition_advice', 'goal_check', 'progress_review']
        
        ai_logs_created = 0
        for _ in range(15):  # Create 15 AI interactions
            ai_log = AILog(
                user_id=muhammad.id,
                request_type=random.choice(request_types),
                prompt="User requested personalized nutrition guidance",
                response=random.choice(ai_responses),
                created_at=datetime.now() - timedelta(days=random.randint(0, 14))
            )
            db.session.add(ai_log)
            ai_logs_created += 1
        
        print(f"Created {ai_logs_created} AI interaction logs")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Dashboard data population complete for {muhammad.full_name}!")
        print(f"📊 Summary:")
        print(f"   - Profile: Updated with complete information")
        print(f"   - Meals: {meals_created} meals over 14 days")
        print(f"   - Health Data: {health_data_created} data points over 30 days")
        print(f"   - AI Logs: {ai_logs_created} interaction logs")
        print(f"\n🔑 Login: awaissaeedsaib@gmail.com")

def get_meal_hour(meal_type):
    """Get appropriate hour for meal type"""
    hours = {
        'breakfast': random.randint(7, 9),
        'lunch': random.randint(12, 14),
        'dinner': random.randint(19, 21),
        'snack': random.randint(15, 17)
    }
    return hours.get(meal_type, 12)

def get_serving_size(food_name, meal_type):
    """Get realistic serving size based on food type and meal"""
    # Base serving sizes in grams
    base_sizes = {
        # Grains/Carbs
        'Basmati Rice': 150,
        'Brown Rice': 150,
        'Quinoa': 100,
        'Chapati': 50,
        'Naan': 80,
        'Oats': 50,
        
        # Proteins
        'Grilled Chicken': 120,
        'Chicken Karahi': 150,
        'Seekh Kebab': 100,
        'Beef Steak': 120,
        'Mutton Curry': 120,
        'Fish Curry': 120,
        'Eggs': 100,
        
        # Vegetables
        'Broccoli': 100,
        'Spinach': 80,
        
        # Dairy
        'Greek Yogurt': 150,
        'Milk': 200,
        'Raita': 50,
        
        # Others
        'Dal (Lentils)': 100,
        'Almonds': 30,
        'Banana': 120,
        'Dates': 40,
        'Honey': 20,
        'Sweet Potato': 150,
        'Chicken Biryani': 200
    }
    
    base_size = base_sizes.get(food_name, 100)
    
    # Adjust for meal type
    if meal_type == 'snack':
        return int(base_size * 0.6)
    elif meal_type == 'breakfast':
        return int(base_size * 0.8)
    else:
        return base_size

if __name__ == '__main__':
    populate_muhammad_dashboard()