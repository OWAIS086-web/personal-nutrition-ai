class NutritionCalculator:
    """Service for calculating nutritional values and daily requirements"""
    
    @staticmethod
    def calculate_bmr(weight_kg, height_cm, age_years, gender):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
        return round(bmr)
    
    @staticmethod
    def calculate_tdee(bmr, activity_level):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'extra': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        return round(bmr * multiplier)
    
    @staticmethod
    def calculate_macro_targets(calories, goal='maintenance'):
        """Calculate macro targets based on calories and goal"""
        if goal == 'weight_loss':
            # Higher protein, moderate carbs
            protein_ratio = 0.30
            carb_ratio = 0.35
            fat_ratio = 0.35
        elif goal == 'muscle_gain':
            # High protein, higher carbs
            protein_ratio = 0.25
            carb_ratio = 0.45
            fat_ratio = 0.30
        else:  # maintenance
            protein_ratio = 0.20
            carb_ratio = 0.45
            fat_ratio = 0.35
        
        return {
            'protein': round(calories * protein_ratio / 4),  # 4 cal per gram
            'carbs': round(calories * carb_ratio / 4),       # 4 cal per gram
            'fat': round(calories * fat_ratio / 9)           # 9 cal per gram
        }
    
    @staticmethod
    def calculate_meal_totals(meal_items):
        """Calculate total nutrition from a list of meal items"""
        totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        for item in meal_items:
            totals['calories'] += item.calories
            totals['protein'] += item.protein
            totals['carbs'] += item.carbs
            totals['fat'] += item.fat
        
        return {k: round(v, 1) for k, v in totals.items()}
    
    @staticmethod
    def get_nutrition_per_gram(food_name, nutrition_per_100g, grams):
        """Calculate nutrition for specific gram amount"""
        factor = grams / 100
        return {
            'calories': round(nutrition_per_100g['calories'] * factor, 1),
            'protein': round(nutrition_per_100g['protein'] * factor, 1),
            'carbs': round(nutrition_per_100g['carbs'] * factor, 1),
            'fat': round(nutrition_per_100g['fat'] * factor, 1)
        }
