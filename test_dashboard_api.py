#!/usr/bin/env python3
"""
Test script to verify dashboard API endpoints are working
"""

from nutrition import create_app
from nutrition.extensions import db
from nutrition.models import User
import requests
from flask_login import login_user

def test_dashboard_apis():
    """Test all dashboard API endpoints"""
    app = create_app()
    
    with app.app_context():
        # Find Muhammad's user
        muhammad = User.query.filter_by(email='awaissaeedsaib@gmail.com').first()
        if not muhammad:
            print("Muhammad's account not found!")
            return
        
        print("=== TESTING DASHBOARD API ENDPOINTS ===\n")
        
        # Test with app test client
        with app.test_client() as client:
            # Login as Muhammad
            with client.session_transaction() as sess:
                sess['_user_id'] = str(muhammad.id)
                sess['_fresh'] = True
            
            # Test nutrition stats
            print("1. Testing /dashboard/api/nutrition-stats")
            response = client.get('/dashboard/api/nutrition-stats?days=7')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Success: {data['success']}")
                print(f"   📊 Averages: {data.get('averages', {})}")
                print(f"   📈 Highest: {data.get('highest', {})}")
                print(f"   📉 Lowest: {data.get('lowest', {})}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
            
            print()
            
            # Test goal progress
            print("2. Testing /dashboard/api/goal-progress")
            response = client.get('/dashboard/api/goal-progress')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Success: {data['success']}")
                print(f"   🎯 Current: {data.get('current', {})}")
                print(f"   🎯 Targets: {data.get('targets', {})}")
                print(f"   📊 Progress: {data.get('progress', {})}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
            
            print()
            
            # Test meal frequency
            print("3. Testing /dashboard/api/meal-frequency")
            response = client.get('/dashboard/api/meal-frequency?days=7')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Success: {data['success']}")
                print(f"   🍽️ Meal Types: {data.get('meal_types', {})}")
                print(f"   ⏰ Total Meals: {data.get('total_meals', 0)}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
            
            print()
            
            # Test wearable integration
            print("4. Testing /dashboard/api/wearable-integration")
            response = client.get('/dashboard/api/wearable-integration?days=7')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Success: {data['success']}")
                health_data = data.get('health_data', {})
                print(f"   📱 Health Data Types: {list(health_data.keys())}")
                for data_type, records in health_data.items():
                    latest_date = max(records.keys()) if records else None
                    if latest_date:
                        latest_value = records[latest_date]['value']
                        print(f"      - {data_type}: {latest_value} (latest: {latest_date})")
            else:
                print(f"   ❌ Failed: {response.status_code}")
            
            print()
            
            # Test recent meals
            print("5. Testing /meals/api/recent")
            response = client.get('/meals/api/recent?limit=3')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Success: {data['success']}")
                meals = data.get('meals', [])
                print(f"   🍽️ Recent Meals Count: {len(meals)}")
                for meal in meals[:3]:
                    print(f"      - {meal['name']}: {meal['total_calories']} cal ({meal['meal_date']})")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        
        print("\n✅ Dashboard API testing complete!")

if __name__ == '__main__':
    test_dashboard_apis()