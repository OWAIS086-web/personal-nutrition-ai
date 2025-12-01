#!/usr/bin/env python3
"""
Script to populate the database with dummy data for frontend development
"""

from datetime import datetime, date, timedelta
import random
from nutrition import create_app
from nutrition.extensions import db
from nutrition.models import User, Meal, MealItem, HealthImport, AILog

def create_dummy_users():
    """Create dummy users with varied profiles"""
    users_data = [
        {
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'calorie_goal': 2200,
            'protein_goal': 165,
            'carbs_goal': 275,
            'fat_goal': 75,
            'height': 180.0,
            'weight': 75.0,
            'activity_level': 'active',
            'date_of_birth': date(1990, 5, 15),
            'dietary_preferences': ['vegetarian'],
            'allergies': ['nuts'],
            'health_goals': ['weight_loss', 'muscle_gain']
        },
        {
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'calorie_goal': 1800,
            'protein_goal': 120,
            'carbs_goal': 200,
            'fat_goal': 60,
            'height': 165.0,
            'weight': 60.0,
            'activity_level': 'moderate',
            'date_of_birth': date(1985, 8, 22),
            'dietary_preferences': ['gluten_free'],
            'allergies': ['dairy'],
            'health_goals': ['maintain_weight', 'improve_energy']
        },
        {
            'email': 'mike.wilson@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'calorie_goal': 2500,
            'protein_goal': 200,
            'carbs_goal': 300,
            'fat_goal': 85,
            'height': 185.0,
            'weight': 85.0,
            'activity_level': 'very_active',
            'date_of_birth': date(1992, 12, 3),
            'dietary_preferences': ['keto'],
            'allergies': [],
            'health_goals': ['muscle_gain', 'improve_performance']
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            calorie_goal=user_data['calorie_goal'],
            protein_goal=user_data['protein_goal'],
            carbs_goal=user_data['carbs_goal'],
            fat_goal=user_data['fat_goal'],
            height=user_data['height'],
            weight=user_data['weight'],
            activity_level=user_data['activity_level'],
            date_of_birth=user_data['date_of_birth'],
            email_verified=True,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
        )
        user.set_password('password123')  # Default password for all dummy users
        user.set_dietary_preferences(user_data['dietary_preferences'])
        user.set_allergies(user_data['allergies'])
        user.set_health_goals(user_data['health_goals'])
        
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    return users

def create_dummy_meals(users):
    """Create dummy meals for the past week for each user"""
    
    # Common foods with nutritional data (per 100g)
    foods_data = {
        'Chicken Breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
        'Brown Rice': {'calories': 111, 'protein': 2.6, 'carbs': 23, 'fat': 0.9},
        'Broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4},
        'Salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13},
        'Sweet Potato': {'calories': 86, 'protein': 1.6, 'carbs': 20, 'fat': 0.1},
        'Greek Yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
        'Oatmeal': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4},
        'Banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
        'Eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11},
        'Avocado': {'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15},
        'Spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4},
        'Quinoa': {'calories': 120, 'protein': 4.4, 'carbs': 22, 'fat': 1.9},
        'Almonds': {'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50},
        'Turkey': {'calories': 135, 'protein': 30, 'carbs': 0, 'fat': 1},
        'Pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1}
    }
    
    meal_templates = {
        'breakfast': [
            ['Oatmeal', 'Banana', 'Almonds'],
            ['Eggs', 'Spinach', 'Avocado'],
            ['Greek Yogurt', 'Banana', 'Almonds']
        ],
        'lunch': [
            ['Chicken Breast', 'Brown Rice', 'Broccoli'],
            ['Salmon', 'Quinoa', 'Spinach'],
            ['Turkey', 'Sweet Potato', 'Broccoli']
        ],
        'dinner': [
            ['Salmon', 'Sweet Potato', 'Spinach'],
            ['Chicken Breast', 'Pasta', 'Broccoli'],
            ['Turkey', 'Quinoa', 'Avocado']
        ],
        'snack': [
            ['Greek Yogurt', 'Banana'],
            ['Almonds'],
            ['Avocado']
        ]
    }
    
    for user in users:
        # Create meals for the past 7 days
        for days_ago in range(7):
            meal_date = date.today() - timedelta(days=days_ago)
            
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                if meal_type == 'snack' and random.random() > 0.6:  # Skip some snacks
                    continue
                
                # Choose a random meal template
                food_items = random.choice(meal_templates[meal_type])
                
                meal = Meal(
                    user_id=user.id,
                    name=f"{meal_type.title()} - {', '.join(food_items)}",
                    meal_type=meal_type,
                    meal_date=meal_date,
                    created_at=datetime.combine(meal_date, datetime.min.time()) + timedelta(
                        hours=random.randint(6, 22), minutes=random.randint(0, 59)
                    )
                )
                
                db.session.add(meal)
                db.session.flush()  # Get the meal ID
                
                # Add meal items
                for food_name in food_items:
                    food_data = foods_data[food_name]
                    
                    # Random serving size (50g to 200g)
                    serving_size = random.randint(50, 200)
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
                
                # Calculate meal totals
                db.session.flush()
                meal.calculate_totals()
    
    db.session.commit()

def create_dummy_health_data(users):
    """Create dummy health import data"""
    
    for user in users:
        # Create health data for the past 30 days
        for days_ago in range(30):
            data_date = date.today() - timedelta(days=days_ago)
            
            # Steps data
            steps = random.randint(3000, 15000)
            health_import = HealthImport(
                user_id=user.id,
                source='fitbit',
                import_type='steps',
                date=data_date,
                value=steps,
                unit='steps'
            )
            db.session.add(health_import)
            
            # Calories burned
            calories_burned = random.randint(1800, 3000)
            health_import = HealthImport(
                user_id=user.id,
                source='fitbit',
                import_type='calories_burned',
                date=data_date,
                value=calories_burned,
                unit='calories'
            )
            db.session.add(health_import)
            
            # Heart rate (average)
            heart_rate = random.randint(60, 85)
            health_import = HealthImport(
                user_id=user.id,
                source='fitbit',
                import_type='heart_rate',
                date=data_date,
                value=heart_rate,
                unit='bpm'
            )
            db.session.add(health_import)
    
    db.session.commit()

def create_dummy_ai_logs(users):
    """Create dummy AI interaction logs"""
    
    ai_responses = [
        "Great job on hitting your protein goal today! Consider adding some healthy fats to your next meal.",
        "Your calorie intake looks good. Try to include more vegetables for better micronutrient balance.",
        "You're doing well with your nutrition goals. Keep up the consistent eating pattern!",
        "Consider having a post-workout snack with protein and carbs for better recovery.",
        "Your meal timing is excellent. This helps maintain steady energy levels throughout the day."
    ]
    
    request_types = ['meal_analysis', 'coach_tip', 'nutrition_advice', 'goal_check']
    
    for user in users:
        # Create 5-10 AI interactions for each user
        for _ in range(random.randint(5, 10)):
            ai_log = AILog(
                user_id=user.id,
                request_type=random.choice(request_types),
                prompt="User requested nutrition advice",
                response=random.choice(ai_responses),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(ai_log)
    
    db.session.commit()

def main():
    """Main function to populate dummy data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Creating dummy users...")
        users = create_dummy_users()
        print(f"Created {len(users)} users")
        
        print("Creating dummy meals...")
        create_dummy_meals(users)
        print("Created meals for all users")
        
        print("Creating dummy health data...")
        create_dummy_health_data(users)
        print("Created health data for all users")
        
        print("Creating dummy AI logs...")
        create_dummy_ai_logs(users)
        print("Created AI interaction logs")
        
        print("\nDummy data population complete!")
        print("\nTest user credentials:")
        print("Email: john.doe@example.com | Password: password123")
        print("Email: jane.smith@example.com | Password: password123")
        print("Email: mike.wilson@example.com | Password: password123")

if __name__ == '__main__':
    main()