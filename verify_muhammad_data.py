#!/usr/bin/env python3
"""
Script to verify Muhammad's dashboard data
"""

from nutrition import create_app
from nutrition.extensions import db
from nutrition.models import User, Meal, MealItem, HealthImport, AILog
from datetime import date, timedelta

def verify_muhammad_data():
    """Verify Muhammad's dashboard data"""
    app = create_app()
    
    with app.app_context():
        # Find Muhammad
        muhammad = User.query.filter_by(email='awaissaeedsaib@gmail.com').first()
        if not muhammad:
            print("Muhammad's account not found!")
            return
        
        print("=== MUHAMMAD SAEED'S DASHBOARD DATA ===\n")
        
        # Profile Information
        print("👤 PROFILE:")
        print(f"   Name: {muhammad.full_name}")
        print(f"   Email: {muhammad.email}")
        print(f"   Goals: {muhammad.calorie_goal} cal, {muhammad.protein_goal}g protein")
        print(f"   Physical: {muhammad.height}cm, {muhammad.weight}kg")
        print(f"   Activity: {muhammad.activity_level}")
        print(f"   Dietary Preferences: {muhammad.get_dietary_preferences()}")
        print(f"   Health Goals: {muhammad.get_health_goals()}")
        
        print("\n🍽️ RECENT MEALS:")
        recent_meals = Meal.query.filter_by(user_id=muhammad.id).order_by(Meal.meal_date.desc(), Meal.created_at.desc()).limit(10).all()
        
        for meal in recent_meals:
            print(f"   📅 {meal.meal_date} - {meal.meal_type.title()}")
            print(f"      {meal.name}")
            print(f"      {meal.total_calories:.0f} cal | {meal.total_protein:.1f}g protein | {meal.total_carbs:.1f}g carbs | {meal.total_fat:.1f}g fat")
            
            # Show meal items
            for item in meal.items[:3]:  # Show first 3 items
                print(f"        • {item.food_name}: {item.quantity:.1f} {item.unit}")
            if len(meal.items) > 3:
                print(f"        ... and {len(meal.items) - 3} more items")
            print()
        
        # Daily nutrition summary for today
        today = date.today()
        today_meals = Meal.query.filter_by(user_id=muhammad.id, meal_date=today).all()
        
        if today_meals:
            total_cal = sum(meal.total_calories for meal in today_meals)
            total_protein = sum(meal.total_protein for meal in today_meals)
            total_carbs = sum(meal.total_carbs for meal in today_meals)
            total_fat = sum(meal.total_fat for meal in today_meals)
            
            print("📊 TODAY'S NUTRITION:")
            print(f"   Calories: {total_cal:.0f}/{muhammad.calorie_goal} ({total_cal/muhammad.calorie_goal*100:.1f}%)")
            print(f"   Protein: {total_protein:.1f}g/{muhammad.protein_goal}g ({total_protein/muhammad.protein_goal*100:.1f}%)")
            print(f"   Carbs: {total_carbs:.1f}g/{muhammad.carbs_goal}g ({total_carbs/muhammad.carbs_goal*100:.1f}%)")
            print(f"   Fat: {total_fat:.1f}g/{muhammad.fat_goal}g ({total_fat/muhammad.fat_goal*100:.1f}%)")
        
        print("\n📈 HEALTH DATA SUMMARY:")
        
        # Recent health data
        recent_steps = HealthImport.query.filter_by(
            user_id=muhammad.id, 
            import_type='steps'
        ).order_by(HealthImport.date.desc()).limit(7).all()
        
        if recent_steps:
            avg_steps = sum(h.value for h in recent_steps) / len(recent_steps)
            print(f"   Average Steps (7 days): {avg_steps:.0f}")
            print(f"   Latest Steps: {recent_steps[0].value:.0f} ({recent_steps[0].date})")
        
        recent_weight = HealthImport.query.filter_by(
            user_id=muhammad.id, 
            import_type='weight'
        ).order_by(HealthImport.date.desc()).first()
        
        if recent_weight:
            print(f"   Current Weight: {recent_weight.value:.1f}kg ({recent_weight.date})")
        
        # Health data counts
        health_counts = {}
        health_types = db.session.query(HealthImport.import_type).filter_by(user_id=muhammad.id).distinct().all()
        for health_type in health_types:
            count = HealthImport.query.filter_by(user_id=muhammad.id, import_type=health_type[0]).count()
            health_counts[health_type[0]] = count
        
        print(f"   Health Data Points: {health_counts}")
        
        print("\n🤖 AI INTERACTIONS:")
        recent_ai = AILog.query.filter_by(user_id=muhammad.id).order_by(AILog.created_at.desc()).limit(3).all()
        
        for ai_log in recent_ai:
            print(f"   📝 {ai_log.request_type} ({ai_log.created_at.strftime('%Y-%m-%d')})")
            print(f"      {ai_log.response[:100]}...")
            print()
        
        # Statistics
        total_meals = Meal.query.filter_by(user_id=muhammad.id).count()
        total_health_data = HealthImport.query.filter_by(user_id=muhammad.id).count()
        total_ai_logs = AILog.query.filter_by(user_id=muhammad.id).count()
        
        print("📋 SUMMARY STATISTICS:")
        print(f"   Total Meals: {total_meals}")
        print(f"   Total Health Data Points: {total_health_data}")
        print(f"   Total AI Interactions: {total_ai_logs}")
        
        print("\n✅ Muhammad's dashboard is fully populated and ready!")

if __name__ == '__main__':
    verify_muhammad_data()