import os
import base64
import json
from PIL import Image
import random
import requests
from flask import current_app

class FoodVisionService:
    """Food detection service with OpenAI GPT-4 Vision API integration"""
    
    # Mock food database with nutritional info per 100g
    FOOD_DATABASE = {
        'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2},
        'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
        'chicken breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
        'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
        'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4},
        'salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13},
        'bread': {'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2},
        'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1},
        'egg': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11},
        'avocado': {'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15},
        'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4},
        'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
        'cheese': {'calories': 113, 'protein': 7, 'carbs': 1, 'fat': 9},
        'yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
        'oatmeal': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4},
    }
    
    @classmethod
    def analyze_image(cls, image_path):
        """
        Analyze food image using OpenAI GPT-4 Vision API with fallback
        """
        try:
            # First try OpenAI Vision API
            print(f"Attempting OpenAI Vision API analysis for: {image_path}")
            openai_result = cls._analyze_with_openai(image_path)
            if openai_result['success']:
                print("OpenAI Vision API analysis successful")
                return openai_result
            
            print("OpenAI Vision API failed, falling back to mock detection")
            # Fallback to mock detection if OpenAI fails
            return cls._mock_analyze_image(image_path)
            
        except Exception as e:
            print(f"OpenAI Vision API error: {str(e)}")
            # Fallback to mock detection on any error
            return cls._mock_analyze_image(image_path)
    
    @classmethod
    def _analyze_with_openai(cls, image_path):
        """Use OpenAI GPT-4 Vision to analyze food image"""
        # Try different model names in order of preference
        models_to_try = ["gpt-4o", "gpt-4o-mini"]
        
        for model_name in models_to_try:
            try:
                print(f"Trying OpenAI model: {model_name}")
                return cls._try_openai_model(image_path, model_name)
            except Exception as e:
                print(f"Model {model_name} failed: {str(e)}")
                continue
        
        # If all models fail, raise the last error
        raise ValueError("All OpenAI models failed")
    
    @classmethod
    def _try_openai_model(cls, image_path, model_name):
        """Try a specific OpenAI model"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key or api_key.startswith('your-'):
            raise ValueError("OpenAI API key not configured properly")
        
        # Validate image file
        if not os.path.exists(image_path):
            raise ValueError("Image file not found")
        
        # Check file size (max 20MB for OpenAI)
        file_size = os.path.getsize(image_path)
        if file_size > 20 * 1024 * 1024:
            raise ValueError("Image file too large (max 20MB)")
        
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are a nutrition analysis AI. Analyze the food in this image and provide detailed nutritional information.

CRITICAL REQUIREMENTS:
1. Return ONLY a valid JSON array
2. NO markdown code blocks (no ```json or ```)
3. NO explanatory text before or after
4. NO null values - always provide numbers

For EACH visible food item, return an object with these EXACT fields:
{
  "food_name": "specific food name (e.g., grilled ribeye steak, not just steak)",
  "estimated_grams": number (realistic weight estimate in grams),
  "confidence": number (0.0 to 1.0, your confidence in detection),
  "nutrition_per_100g": {
    "calories": number (kcal per 100g),
    "protein": number (grams per 100g),
    "carbs": number (grams per 100g),
    "fat": number (grams per 100g)
  }
}

NUTRITION GUIDELINES:
- Use USDA or standard nutrition databases for accuracy
- For meats: Include cooking method (grilled, fried, baked)
- For vegetables: Specify if raw or cooked
- Provide realistic portion estimates based on plate size
- All nutrition values must be per 100g for consistency

EXAMPLE OUTPUT:
[
  {
    "food_name": "Grilled Ribeye Steak",
    "estimated_grams": 300,
    "confidence": 0.95,
    "nutrition_per_100g": {
      "calories": 291,
      "protein": 25.0,
      "carbs": 0.0,
      "fat": 21.0
    }
  },
  {
    "food_name": "Mashed Potatoes",
    "estimated_grams": 150,
    "confidence": 0.85,
    "nutrition_per_100g": {
      "calories": 88,
      "protein": 1.7,
      "carbs": 17.0,
      "fat": 1.2
    }
  }
]

IMPORTANT: Return ONLY the JSON array. Start with [ and end with ]. No other text."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        print("Sending request to OpenAI API...")
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=payload, timeout=30)
        
        print(f"OpenAI API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Clean up response - remove markdown code blocks if present
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            # Parse JSON response
            try:
                foods_data = json.loads(content)
                if not isinstance(foods_data, list):
                    raise ValueError("Response is not a list")
                
                results = []
                for food in foods_data:
                    # Validate required fields
                    if not all(key in food for key in ['food_name', 'estimated_grams', 'confidence', 'nutrition_per_100g']):
                        continue
                    
                    nutrition = food['nutrition_per_100g']
                    estimated_grams = max(int(food['estimated_grams']), 1)  # Minimum 1g
                    
                    # Validate nutrition values
                    nutrition = {
                        'calories': max(float(nutrition.get('calories', 0)), 0),
                        'protein': max(float(nutrition.get('protein', 0)), 0),
                        'carbs': max(float(nutrition.get('carbs', 0)), 0),
                        'fat': max(float(nutrition.get('fat', 0)), 0)
                    }
                    
                    # Calculate nutrition for estimated serving
                    serving_nutrition = {
                        'calories': round(nutrition['calories'] * estimated_grams / 100, 1),
                        'protein': round(nutrition['protein'] * estimated_grams / 100, 1),
                        'carbs': round(nutrition['carbs'] * estimated_grams / 100, 1),
                        'fat': round(nutrition['fat'] * estimated_grams / 100, 1)
                    }
                    
                    results.append({
                        'food_name': str(food['food_name']).strip(),
                        'confidence': min(max(float(food['confidence']), 0.0), 1.0),  # Clamp between 0-1
                        'estimated_grams': estimated_grams,
                        'nutrition_per_100g': nutrition,
                        'estimated_nutrition': serving_nutrition
                    })
                
                return {
                    'success': True,
                    'foods': results,
                    'message': f'AI detected {len(results)} food item(s)'
                }
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw content: {content}")
                raise ValueError("Invalid JSON response from OpenAI")
        else:
            error_msg = f"OpenAI API error: {response.status_code}"
            try:
                error_details = response.json()
                print(f"OpenAI API error details: {error_details}")
                if 'error' in error_details:
                    error_msg += f" - {error_details['error'].get('message', 'Unknown error')}"
            except:
                print(f"OpenAI API raw response: {response.text}")
            
            if response.status_code == 401:
                error_msg += " - Invalid API key"
            elif response.status_code == 429:
                error_msg += " - Rate limit exceeded"
            elif response.status_code == 400:
                error_msg += " - Bad request"
            elif response.status_code == 404:
                error_msg += " - Model not found (try gpt-4o or gpt-4-turbo)"
            
            raise ValueError(error_msg)
    
    @classmethod
    def _mock_analyze_image(cls, image_path):
        """
        Fallback mock food detection
        """
        try:
            # Validate image
            with Image.open(image_path) as img:
                # Basic image validation
                if img.size[0] < 50 or img.size[1] < 50:
                    raise ValueError("Image too small")
            
            # Mock detection - return 1-3 random foods
            num_foods = random.randint(1, 3)
            detected_foods = random.sample(list(cls.FOOD_DATABASE.keys()), num_foods)
            
            results = []
            for food in detected_foods:
                nutrition = cls.FOOD_DATABASE[food].copy()
                
                # Add estimated serving size (random between 50-200g)
                estimated_grams = random.randint(50, 200)
                
                # Calculate nutrition for estimated serving
                serving_nutrition = {
                    'calories': round(nutrition['calories'] * estimated_grams / 100, 1),
                    'protein': round(nutrition['protein'] * estimated_grams / 100, 1),
                    'carbs': round(nutrition['carbs'] * estimated_grams / 100, 1),
                    'fat': round(nutrition['fat'] * estimated_grams / 100, 1)
                }
                
                results.append({
                    'food_name': food.title(),
                    'confidence': round(random.uniform(0.7, 0.95), 2),
                    'estimated_grams': estimated_grams,
                    'nutrition_per_100g': nutrition,
                    'estimated_nutrition': serving_nutrition
                })
            
            return {
                'success': True,
                'foods': results,
                'message': f'Detected {len(results)} food item(s) using fallback detection (OpenAI API temporarily unavailable)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'foods': [],
                'message': f'Error analyzing image: {str(e)}'
            }
    
    @classmethod
    def search_food(cls, query):
        """Search for food in database by name"""
        query = query.lower().strip()
        matches = []
        
        for food_name, nutrition in cls.FOOD_DATABASE.items():
            if query in food_name or food_name in query:
                matches.append({
                    'food_name': food_name.title(),
                    'nutrition_per_100g': nutrition
                })
        
        return matches
    
    @classmethod
    def get_food_nutrition(cls, food_name):
        """Get nutrition info for a specific food"""
        food_key = food_name.lower()
        if food_key in cls.FOOD_DATABASE:
            return cls.FOOD_DATABASE[food_key]
        return None