#!/usr/bin/env python3
"""
Utility script to fix corrupted health goals data
"""

import json
import re
from nutrition import create_app
from nutrition.extensions import db
from nutrition.models.user import User

def fix_health_goals():
    """Fix corrupted health goals for all users"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        fixed_count = 0
        
        for user in users:
            if user.health_goals:
                try:
                    # Try to parse as JSON
                    parsed = json.loads(user.health_goals)
                    
                    # Check if it's stored as a string instead of array
                    if isinstance(parsed, str):
                        print(f"User {user.email}: Converting string '{parsed}' to array")
                        user.health_goals = json.dumps([parsed])
                        fixed_count += 1
                    elif isinstance(parsed, list):
                        # It's already a list, check if any items need cleaning
                        cleaned_goals = []
                        needs_fix = False
                        
                        for goal in parsed:
                            if isinstance(goal, str) and len(goal) > 1:
                                cleaned_goals.append(goal)
                            elif len(goal) == 1:
                                # Skip single characters (corrupted data)
                                needs_fix = True
                                print(f"User {user.email}: Removing single character '{goal}'")
                        
                        if needs_fix and cleaned_goals:
                            user.health_goals = json.dumps(cleaned_goals)
                            fixed_count += 1
                        elif needs_fix and not cleaned_goals:
                            # All goals were corrupted, reset to empty
                            user.health_goals = json.dumps([])
                            fixed_count += 1
                            
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"User {user.email}: JSON error {e}, resetting to empty goals")
                    user.health_goals = json.dumps([])
                    fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"Fixed health goals for {fixed_count} users")
        else:
            print("No corrupted health goals found")

if __name__ == '__main__':
    fix_health_goals()