#!/usr/bin/env python3
"""
Script to verify the dummy data that was populated
"""

from nutrition import create_app
from nutrition.extensions import db
from nutrition.models import User, Meal, MealItem, HealthImport, AILog

def verify_data():
    """Verify the populated dummy data"""
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE VERIFICATION ===\n")
        
        # Check users
        users = User.query.all()
        print(f"👥 Users: {len(users)}")
        for user in users:
            print(f"   - {user.full_name} ({user.email})")
            print(f"     Goals: {user.calorie_goal} cal, {user.protein_goal}g protein")
            print(f"     Profile: {user.height}cm, {user.weight}kg, {user.activity_level}")
        
        print()
        
        # Check meals
        meals = Meal.query.all()
        print(f"🍽️  Total Meals: {len(meals)}")
        
        # Group by user
        for user in users:
            user_meals = Meal.query.filter_by(user_id=user.id).all()
            print(f"   {user.first_name}: {len(user_meals)} meals")
            
            # Show recent meals
            recent_meals = Meal.query.filter_by(user_id=user.id).order_by(Meal.meal_date.desc()).limit(3).all()
            for meal in recent_meals:
                print(f"     - {meal.meal_date}: {meal.name} ({meal.total_calories:.0f} cal)")
        
        print()
        
        # Check meal items
        meal_items = MealItem.query.all()
        print(f"🥗 Total Meal Items: {len(meal_items)}")
        
        print()
        
        # Check health data
        health_imports = HealthImport.query.all()
        print(f"📊 Health Data Points: {len(health_imports)}")
        
        # Show data types
        import_types = db.session.query(HealthImport.import_type).distinct().all()
        for import_type in import_types:
            count = HealthImport.query.filter_by(import_type=import_type[0]).count()
            print(f"   - {import_type[0]}: {count} entries")
        
        print()
        
        # Check AI logs
        ai_logs = AILog.query.all()
        print(f"🤖 AI Interaction Logs: {len(ai_logs)}")
        
        # Show request types
        request_types = db.session.query(AILog.request_type).distinct().all()
        for request_type in request_types:
            count = AILog.query.filter_by(request_type=request_type[0]).count()
            print(f"   - {request_type[0]}: {count} entries")
        
        print("\n=== SAMPLE DATA ===\n")
        
        # Show a sample meal with items
        sample_meal = Meal.query.first()
        if sample_meal:
            print(f"📋 Sample Meal: {sample_meal.name}")
            print(f"   Date: {sample_meal.meal_date}")
            print(f"   Type: {sample_meal.meal_type}")
            print(f"   Totals: {sample_meal.total_calories:.0f} cal, {sample_meal.total_protein:.1f}g protein")
            print("   Items:")
            for item in sample_meal.items:
                print(f"     - {item.food_name}: {item.quantity:.1f} {item.unit} ({item.calories:.0f} cal)")
        
        print("\n✅ Data verification complete!")

if __name__ == '__main__':
    verify_data()