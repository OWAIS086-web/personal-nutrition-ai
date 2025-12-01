import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from nutrition.models.user import User
from nutrition.models.meal import Meal
from nutrition.models.ai_log import AILog
from nutrition.extensions import db

class AICoachService:
    """AI-powered nutrition coaching service"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.mock_mode = not self.api_key  # Use mock responses if no API key
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Install with: pip install openai")
                self.mock_mode = True
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.mock_mode = True
    
    def get_daily_tip(self, user: User) -> Dict:
        """Generate a personalized daily nutrition tip"""
        
        # Get user context
        user_context = self._build_user_context(user)
        
        if self.mock_mode:
            return self._get_mock_daily_tip(user_context)
        
        prompt = self._build_daily_tip_prompt(user_context)
        
        try:
            response = self._call_openai(prompt, "daily_tip")
            
            # Log the interaction
            self._log_ai_interaction(user.id, "daily_tip", prompt, response)
            
            return {
                'success': True,
                'tip': response,
                'type': 'daily_tip'
            }
            
        except Exception as e:
            return {
                'success': False,
                'tip': "Stay hydrated and eat a variety of colorful foods today!",
                'error': str(e)
            }
    
    def get_meal_analysis(self, user: User, meal_data: Dict) -> Dict:
        """Analyze a meal and provide feedback"""
        
        user_context = self._build_user_context(user)
        
        if self.mock_mode:
            return self._get_mock_meal_analysis(meal_data, user_context)
        
        prompt = self._build_meal_analysis_prompt(user_context, meal_data)
        
        try:
            response = self._call_openai(prompt, "meal_analysis")
            
            self._log_ai_interaction(user.id, "meal_analysis", prompt, response)
            
            return {
                'success': True,
                'analysis': response,
                'type': 'meal_analysis'
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis': "This meal looks nutritious! Try to include a variety of colors and food groups.",
                'error': str(e)
            }
    
    def get_weekly_insights(self, user: User) -> Dict:
        """Generate weekly nutrition insights and recommendations"""
        
        # Get last 7 days of meals
        week_ago = date.today() - timedelta(days=7)
        recent_meals = Meal.query.filter(
            Meal.user_id == user.id,
            Meal.meal_date >= week_ago
        ).all()
        
        weekly_stats = self._calculate_weekly_stats(recent_meals)
        user_context = self._build_user_context(user)
        
        if self.mock_mode:
            return self._get_mock_weekly_insights(weekly_stats, user_context)
        
        prompt = self._build_weekly_insights_prompt(user_context, weekly_stats)
        
        try:
            response = self._call_openai(prompt, "weekly_insights")
            
            self._log_ai_interaction(user.id, "weekly_insights", prompt, response)
            
            return {
                'success': True,
                'insights': response,
                'stats': weekly_stats,
                'type': 'weekly_insights'
            }
            
        except Exception as e:
            return {
                'success': False,
                'insights': "Keep up the great work with your nutrition journey!",
                'stats': weekly_stats,
                'error': str(e)
            }
    
    def get_goal_coaching(self, user: User) -> Dict:
        """Provide coaching based on user's health goals"""
        
        user_context = self._build_user_context(user)
        goals = user.get_health_goals()
        
        if not goals:
            return {
                'success': True,
                'coaching': "Consider setting some health goals to get personalized coaching!",
                'type': 'goal_coaching'
            }
        
        if self.mock_mode:
            return self._get_mock_goal_coaching(goals, user_context)
        
        prompt = self._build_goal_coaching_prompt(user_context, goals)
        
        try:
            response = self._call_openai(prompt, "goal_coaching")
            
            self._log_ai_interaction(user.id, "goal_coaching", prompt, response)
            
            return {
                'success': True,
                'coaching': response,
                'goals': goals,
                'type': 'goal_coaching'
            }
            
        except Exception as e:
            return {
                'success': False,
                'coaching': "Focus on consistent, small changes to reach your health goals!",
                'goals': goals,
                'error': str(e)
            }
    
    def _call_openai(self, prompt: str, request_type: str) -> str:
        """Make actual OpenAI API call"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a friendly, supportive AI nutrition coach. Provide helpful, encouraging, and actionable nutrition advice. Keep responses concise and positive."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall back to mock response
            return self._mock_openai_call(prompt, request_type)
    
    def _build_user_context(self, user: User) -> Dict:
        """Build context about the user for AI prompts"""
        
        # Get recent meals for context
        recent_meals = Meal.query.filter(
            Meal.user_id == user.id,
            Meal.meal_date >= date.today() - timedelta(days=3)
        ).limit(10).all()
        
        return {
            'name': user.first_name,
            'dietary_preferences': user.get_dietary_preferences(),
            'allergies': user.get_allergies(),
            'health_goals': user.get_health_goals(),
            'activity_level': user.activity_level,
            'units': user.units,
            'recent_meals_count': len(recent_meals),
            'avg_daily_calories': self._calculate_avg_calories(recent_meals) if recent_meals else 0
        }
    
    def _build_daily_tip_prompt(self, user_context: Dict) -> str:
        """Build prompt for daily tip generation"""
        
        prompt = f"""
        You are a friendly, supportive AI nutrition coach. Generate a personalized daily tip for {user_context['name']}.
        
        User Context:
        - Dietary preferences: {', '.join(user_context['dietary_preferences']) if user_context['dietary_preferences'] else 'None specified'}
        - Health goals: {', '.join(user_context['health_goals']) if user_context['health_goals'] else 'General wellness'}
        - Activity level: {user_context['activity_level']}
        - Recent meals logged: {user_context['recent_meals_count']}
        - Average daily calories: {user_context['avg_daily_calories']}
        
        Generate a short (1-2 sentences), encouraging, and actionable nutrition tip. Be culturally sensitive and supportive.
        Focus on practical advice they can implement today.
        """
        
        return prompt
    
    def _build_meal_analysis_prompt(self, user_context: Dict, meal_data: Dict) -> str:
        """Build prompt for meal analysis"""
        
        prompt = f"""
        You are a supportive AI nutrition coach analyzing a meal for {user_context['name']}.
        
        User Context:
        - Dietary preferences: {', '.join(user_context['dietary_preferences']) if user_context['dietary_preferences'] else 'None'}
        - Health goals: {', '.join(user_context['health_goals']) if user_context['health_goals'] else 'General wellness'}
        - Allergies: {', '.join(user_context['allergies']) if user_context['allergies'] else 'None'}
        
        Meal Data:
        - Name: {meal_data.get('name', 'Unknown')}
        - Type: {meal_data.get('meal_type', 'Unknown')}
        - Calories: {meal_data.get('calories', 0)}
        - Protein: {meal_data.get('protein', 0)}g
        - Carbs: {meal_data.get('carbs', 0)}g
        - Fat: {meal_data.get('fat', 0)}g
        - Foods: {', '.join(meal_data.get('foods', []))}
        
        Provide encouraging feedback about this meal (2-3 sentences). Highlight positive aspects and suggest gentle improvements if needed.
        Be supportive and avoid being judgmental.
        """
        
        return prompt
    
    def _build_weekly_insights_prompt(self, user_context: Dict, weekly_stats: Dict) -> str:
        """Build prompt for weekly insights"""
        
        prompt = f"""
        You are an encouraging AI nutrition coach providing weekly insights for {user_context['name']}.
        
        User Context:
        - Health goals: {', '.join(user_context['health_goals']) if user_context['health_goals'] else 'General wellness'}
        - Dietary preferences: {', '.join(user_context['dietary_preferences']) if user_context['dietary_preferences'] else 'None'}
        
        Weekly Stats:
        - Days logged: {weekly_stats['days_logged']}/7
        - Total meals: {weekly_stats['total_meals']}
        - Average daily calories: {weekly_stats['avg_calories']}
        - Average daily protein: {weekly_stats['avg_protein']}g
        - Average daily carbs: {weekly_stats['avg_carbs']}g
        - Average daily fat: {weekly_stats['avg_fat']}g
        
        Provide encouraging weekly insights (3-4 sentences). Celebrate progress, identify patterns, and suggest actionable improvements for next week.
        Be positive and motivating.
        """
        
        return prompt
    
    def _build_goal_coaching_prompt(self, user_context: Dict, goals: List[str]) -> str:
        """Build prompt for goal-specific coaching"""
        
        prompt = f"""
        You are a supportive AI nutrition coach providing goal-specific advice for {user_context['name']}.
        
        User's Health Goals: {', '.join(goals)}
        
        User Context:
        - Dietary preferences: {', '.join(user_context['dietary_preferences']) if user_context['dietary_preferences'] else 'None'}
        - Activity level: {user_context['activity_level']}
        - Recent nutrition tracking: {user_context['recent_meals_count']} meals in last 3 days
        
        Provide specific, actionable coaching advice (2-3 sentences) to help them achieve their health goals.
        Be encouraging and focus on sustainable habits.
        """
        
        return prompt
    
    def _mock_openai_call(self, prompt: str, request_type: str) -> str:
        """Mock OpenAI API call - replace with actual API call in production"""
        
        mock_responses = {
            'daily_tip': [
                "Try adding a handful of colorful vegetables to your next meal - they're packed with vitamins and add great flavor!",
                "Remember to stay hydrated throughout the day - aim for 8 glasses of water to support your metabolism.",
                "Consider having a protein-rich snack between meals to help maintain steady energy levels.",
                "Take a moment to eat mindfully today - chewing slowly can help with digestion and satisfaction.",
                "Include some healthy fats like avocado or nuts in your meals to help absorb fat-soluble vitamins."
            ],
            'meal_analysis': [
                "This meal looks well-balanced with a good mix of protein and vegetables! Consider adding some whole grains for sustained energy.",
                "Great choice on the lean protein! The colorful vegetables provide excellent nutrients. Maybe add a small portion of healthy fats next time.",
                "I love seeing those fresh ingredients! This meal provides good nutrition. Try to include a variety of colors for maximum nutrient diversity.",
                "This is a nutritious meal that aligns well with your health goals! The portion sizes look appropriate for sustained energy."
            ],
            'weekly_insights': [
                "You've been consistent with logging your meals this week - that's fantastic! Your protein intake looks good, and I notice you're including plenty of vegetables. For next week, try to add more variety in your breakfast choices.",
                "Great job staying on track with your nutrition goals! Your calorie intake has been steady, which is perfect for sustainable progress. Consider adding more fiber-rich foods to support digestive health.",
                "I'm impressed by your dedication to tracking your meals! Your macro balance is improving each week. Focus on incorporating more whole grains to boost your energy levels.",
                "You're making excellent progress! Your meal consistency is paying off. Try to include more healthy fats like nuts or olive oil to support nutrient absorption."
            ],
            'goal_coaching': [
                "For weight loss, focus on creating a moderate calorie deficit while maintaining protein intake. Small, consistent changes work better than drastic restrictions!",
                "To build muscle, ensure you're getting enough protein (aim for 1.6-2.2g per kg body weight) and don't forget to fuel your workouts with complex carbs.",
                "For heart health, emphasize omega-3 rich foods like salmon and walnuts, and include plenty of fiber from fruits and vegetables.",
                "To boost energy, focus on balanced meals with complex carbs, lean protein, and healthy fats. Avoid energy crashes by eating regularly throughout the day."
            ]
        }
        
        import random
        responses = mock_responses.get(request_type, ["Keep up the great work with your nutrition journey!"])
        return random.choice(responses)
    
    def _get_mock_daily_tip(self, user_context: Dict) -> Dict:
        """Generate mock daily tip based on user context"""
        
        tips = [
            f"Hi {user_context['name']}! Try adding more colorful vegetables to your meals today for extra nutrients.",
            f"Great job tracking your meals, {user_context['name']}! Remember to stay hydrated throughout the day.",
            f"Consider having a protein-rich snack, {user_context['name']} - it can help maintain steady energy levels.",
            f"Mindful eating tip for today, {user_context['name']}: chew slowly and savor each bite for better digestion."
        ]
        
        # Customize based on user context
        if 'weight_loss' in user_context.get('health_goals', []):
            tips.append(f"Focus on fiber-rich foods today, {user_context['name']} - they'll help you feel satisfied longer!")
        
        if 'muscle_gain' in user_context.get('health_goals', []):
            tips.append(f"Don't forget your post-workout protein, {user_context['name']} - it's crucial for muscle recovery!")
        
        import random
        return {
            'success': True,
            'tip': random.choice(tips),
            'type': 'daily_tip'
        }
    
    def _get_mock_meal_analysis(self, meal_data: Dict, user_context: Dict) -> Dict:
        """Generate mock meal analysis"""
        
        analyses = [
            "This meal looks nutritious and well-balanced! The combination of protein and vegetables is excellent for your health goals.",
            "Great food choices! This meal provides good nutrition and fits well with your dietary preferences.",
            "I love the variety in this meal! The nutrients from these foods will give you sustained energy throughout the day.",
            "This is a solid meal choice that aligns with your health objectives. The portion sizes look appropriate too!"
        ]
        
        import random
        return {
            'success': True,
            'analysis': random.choice(analyses),
            'type': 'meal_analysis'
        }
    
    def _get_mock_weekly_insights(self, weekly_stats: Dict, user_context: Dict) -> Dict:
        """Generate mock weekly insights"""
        
        insights = [
            f"Excellent work this week! You logged {weekly_stats['days_logged']} days and maintained consistent nutrition habits.",
            f"Your dedication shows - {weekly_stats['total_meals']} meals logged! Your average daily intake looks balanced.",
            f"Great progress this week! Your nutrition tracking is helping you stay on track with your health goals.",
            f"Impressive consistency! You're building healthy habits that will serve you well long-term."
        ]
        
        import random
        return {
            'success': True,
            'insights': random.choice(insights),
            'stats': weekly_stats,
            'type': 'weekly_insights'
        }
    
    def _get_mock_goal_coaching(self, goals: List[str], user_context: Dict) -> Dict:
        """Generate mock goal-specific coaching"""
        
        coaching_map = {
            'weight_loss': "Focus on creating a sustainable calorie deficit through balanced meals and regular activity. Small changes lead to lasting results!",
            'muscle_gain': "Prioritize protein intake and consistent strength training. Don't forget to fuel your workouts with quality carbohydrates!",
            'heart_health': "Emphasize omega-3 rich foods, fiber, and limit processed foods. Your heart will thank you for these nutritious choices!",
            'energy_boost': "Balance your meals with complex carbs, lean protein, and healthy fats to maintain steady energy throughout the day.",
            'better_sleep': "Consider avoiding caffeine late in the day and include magnesium-rich foods like leafy greens and nuts in your diet.",
            'digestive_health': "Focus on fiber-rich foods, probiotics, and staying hydrated. Your gut health impacts your overall wellbeing!"
        }
        
        # Get coaching for the first goal or provide general advice
        primary_goal = goals[0] if goals else 'general'
        coaching = coaching_map.get(primary_goal, "Keep focusing on balanced nutrition and consistent healthy habits - you're doing great!")
        
        return {
            'success': True,
            'coaching': coaching,
            'goals': goals,
            'type': 'goal_coaching'
        }
    
    def _log_ai_interaction(self, user_id: int, request_type: str, prompt: str, response: str):
        """Log AI interaction for analytics and improvement"""
        
        ai_log = AILog(
            user_id=user_id,
            request_type=request_type,
            prompt=prompt[:1000],  # Truncate long prompts
            response=response[:2000]  # Truncate long responses
        )
        
        db.session.add(ai_log)
        db.session.commit()
    
    def _calculate_weekly_stats(self, meals: List[Meal]) -> Dict:
        """Calculate weekly nutrition statistics"""
        
        if not meals:
            return {
                'total_meals': 0,
                'avg_calories': 0,
                'avg_protein': 0,
                'avg_carbs': 0,
                'avg_fat': 0,
                'days_logged': 0
            }
        
        total_calories = sum(meal.total_calories for meal in meals)
        total_protein = sum(meal.total_protein for meal in meals)
        total_carbs = sum(meal.total_carbs for meal in meals)
        total_fat = sum(meal.total_fat for meal in meals)
        
        # Count unique days
        unique_days = len(set(meal.meal_date for meal in meals))
        
        return {
            'total_meals': len(meals),
            'avg_calories': round(total_calories / max(unique_days, 1), 1),
            'avg_protein': round(total_protein / max(unique_days, 1), 1),
            'avg_carbs': round(total_carbs / max(unique_days, 1), 1),
            'avg_fat': round(total_fat / max(unique_days, 1), 1),
            'days_logged': unique_days,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat
        }
    
    def _calculate_avg_calories(self, meals: List[Meal]) -> float:
        """Calculate average daily calories from recent meals"""
        if not meals:
            return 0
        
        # Group by date and sum calories per day
        daily_calories = {}
        for meal in meals:
            date_key = meal.meal_date
            if date_key not in daily_calories:
                daily_calories[date_key] = 0
            daily_calories[date_key] += meal.total_calories
        
        if not daily_calories:
            return 0
        
        return round(sum(daily_calories.values()) / len(daily_calories), 1)
