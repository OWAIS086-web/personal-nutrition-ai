Personal Nutrition AI — AI-Powered Wellness Companion
An AI-powered nutrition and wellness platform that turns meal photos into structured nutrition insights, tracks daily/macronutrient goals, and provides personalized AI coaching based on user preferences, dietary restrictions, health goals, and recent nutrition history.

 
Overview
Personal Nutrition AI is a full-stack wellness application built around the idea of making nutrition tracking as simple as taking a photo.
Instead of requiring users to manually enter every food item, the platform can analyze a meal image using OpenAI vision models, identify visible foods, estimate serving sizes, and calculate nutrition values for the estimated serving.
The platform then combines that nutrition data with the user's:
- Dietary preferences
- Allergies and food restrictions
- Health goals
- Activity level
- Recent meals
- Nutrition history
to provide personalized AI-generated coaching and insights.
Core AI Capabilities
1. AI Food Recognition
Users upload a meal image and the vision pipeline attempts to identify the visible food items.
The AI response is normalized into structured data containing:
{
  "food_name": "Grilled Chicken Breast",
  "estimated_grams": 180,
  "confidence": 0.94,
  "nutrition_per_100g": {
    "calories": 165,
    "protein": 31,
    "carbs": 0,
    "fat": 3.6
  },
  "estimated_nutrition": {
    "calories": 297,
    "protein": 55.8,
    "carbs": 0,
    "fat": 6.5
  }
}

The application validates the returned structure, normalizes numeric values, clamps confidence scores, and calculates serving-level nutrition.
Vision model strategy
The application attempts:
GPT-4o
   ↓
GPT-4o-mini
   ↓
Fallback Food Detection

The fallback system uses an internal nutrition database when the external AI service is unavailable.
This makes the meal-analysis workflow more resilient rather than completely dependent on a single API response.
2. AI Nutrition Coaching
The AICoachService provides several AI-powered workflows:
Daily Nutrition Tip
Generates a short personalized recommendation using the user's profile and recent nutrition context.
Meal Analysis
Reviews a specific meal using:
- Calories
- Protein
- Carbohydrates
- Fat
- Food items
- Meal type
- Dietary preferences
- Health goals
- Allergies
Weekly Insights
Analyzes the user's recent nutrition history and generates:
- Progress observations
- Nutrition patterns
- Positive feedback
- Suggested improvements
Goal-Based Coaching
Provides recommendations based on goals such as:
- Weight loss
- Muscle gain
- Heart health
- Energy improvement
- Better sleep
- Digestive health
3. Personalized User Context
The AI does not operate only on generic prompts.
It builds a user-specific context containing information such as:
User
├── Dietary Preferences
├── Allergies
├── Health Goals
├── Activity Level
├── Units
├── Recent Meals
└── Average Daily Calories

That context is then injected into the coaching workflow so recommendations can be tailored to the user's profile.
4. Nutrition Tracking
Every meal can store detailed nutritional values including:
- Calories
- Protein
- Carbohydrates
- Fat
- Food item
- Quantity
- Unit
- Meal type
- Meal date
- Meal image
The application can calculate:
Per Food
   ↓
Per Meal
   ↓
Daily Totals
   ↓
Weekly Statistics
   ↓
Goal Progress

5. BMR, TDEE & Macro Calculation
The application includes a dedicated NutritionCalculator service.
BMR
Uses the Mifflin-St Jeor equation to estimate basal metabolic rate.
TDEE
Applies activity multipliers for:
Sedentary
Light
Moderate
Active
Extra Active

Macro Targets
The platform calculates protein, carbohydrate, and fat targets based on calorie goals and the selected objective.
Supported goal strategies include:
- Weight loss
- Muscle gain
- Maintenance
6. Goal Progress Dashboard
The dashboard tracks actual intake against daily targets.
Example:
Calories
████████████████░░░░ 82%

Protein
██████████████░░░░░░ 71%

Carbohydrates
█████████████████░░░ 86%

Fat
███████████░░░░░░░░░ 58%

The backend exposes APIs for retrieving current totals, target values, and progress percentages.
7. Nutrition Analytics
The dashboard provides analytics across configurable time periods.
Tracked metrics include:
- Daily calories
- Protein
- Carbohydrates
- Fat
- Total meals
- Average intake
- Highest intake
- Lowest intake
- Meal frequency
- Hourly meal distribution
The application also exposes JSON APIs for frontend visualization and reporting.
8. Meal Frequency Analysis
The system analyzes eating patterns by:
Meal Type
Breakfast
Lunch
Dinner
Snack

Time of Day
It also analyzes the hour at which meals were logged, enabling the dashboard to surface meal-timing patterns.
9. Health & Wearable Data Layer
The application contains a health-data model designed around imported health metrics.
Supported health-data concepts include:
- Steps
- Calories
- Distance
- Heart rate
- Sleep
- Active minutes
Health records track:
Source
Import Type
Date
Value
Unit
User

The platform also includes an Apple Health service layer for processing exported health records and mapping Apple Health identifiers into application-level metrics.
Example:
HKQuantityTypeIdentifierStepCount
                ↓
              steps

HKQuantityTypeIdentifierHeartRate
                ↓
           heart_rate

The repository describes this Apple Health integration as a simplified export-processing implementation rather than native iOS HealthKit integration.

10. Data Export
Users can export nutrition information through API endpoints.
Supported output formats include:
JSON
CSV

Exported data can contain:
- Date
- Meal type
- Food name
- Quantity
- Unit
- Calories
- Protein
- Carbohydrates
- Fat
11. Authentication & Security
Security is implemented using several Flask extensions and controls:
- Flask-Login
- Password hashing with bcrypt
- CSRF protection
- Flask-WTF
- Rate limiting
- Secure session cookies
- HTTP-only cookies
- SameSite cookie configuration
- Input validation
- Secure file-name handling
- Upload size limits
Protected API operations require authentication.
AI endpoints also have rate limits to reduce abuse and unnecessary API consumption.
12. AI Interaction Logging
AI interactions are persisted through an AILog model.
Logged information can include:
User
Request Type
Prompt
Response

This provides a foundation for:
- AI usage analytics
- Debugging
- Prompt evaluation
- Product improvement
- Interaction auditing
13. Resilient AI Architecture
The project uses graceful degradation throughout the AI workflow.
For example:
User Upload
     │
     ▼
OpenAI Vision
     │
     ├── Success ───────► Structured Nutrition
     │
     └── Failure
           │
           ▼
      Local Fallback
           │
           ▼
    Nutrition Database

The coaching layer also has fallback responses when OpenAI is unavailable.
This means the application can continue providing basic functionality even when the external AI dependency fails.
Architecture
                         ┌───────────────────────┐
                         │     Web Interface     │
                         │    HTML/CSS/JS/PWA    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      Flask App        │
                         │   Auth / Dashboard    │
                         │ Meals / Wearables     │
                         │        API            │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
       Food Vision Service      AI Coach Service      Nutrition Calculator
              │                      │                      │
              ▼                      ▼                      ▼
        OpenAI Vision          OpenAI Chat API       BMR / TDEE / Macros
              │                      │
              └──────────────┬───────┘
                             ▼
                        AI Interaction Log
                             │
                             ▼
                    ┌───────────────────┐
                    │    SQLAlchemy     │
                    │      Models       │
                    └─────────┬─────────┘
                              │
                              ▼
                      SQLite / PostgreSQL

Technology Stack
Backend
- Python
- Flask 2.3.3
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF
- Flask-Limiter
- WTForms
- Werkzeug
AI
- OpenAI GPT-4o
- OpenAI GPT-4o-mini
- OpenAI Chat Completions
- Prompt Engineering
- Vision-based Food Recognition
- AI Nutrition Coaching
Data & Processing
- SQLAlchemy
- SQLite
- PostgreSQL support
- Pillow
- Requests
- JSON
- Database migrations
Security
- bcrypt
- CSRF protection
- Rate limiting
- Secure sessions
- Authenticated routes
- Secure file uploads
Frontend
- HTML5
- CSS3
- JavaScript
- Responsive UI
- Dashboard visualizations
- PWA/service-worker support
Project Structure
personal-nutrition-ai/
│
├── app.py
├── config.py
├── requirements.txt
│
├── nutrition/
│   ├── __init__.py
│   ├── extensions.py
│   │
│   ├── controllers/
│   │   ├── api_controller.py
│   │   ├── auth_controller.py
│   │   ├── dashboard_controller.py
│   │   ├── meal_controller.py
│   │   └── wearable_controller.py
│   │
│   ├── forms/
│   ├── models/
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── wearable.py
│   │   └── ai_log.py
│   │
│   ├── services/
│   │   ├── food_vision.py
│   │   ├── ai_coach.py
│   │   ├── nutrition_calc.py
│   │   ├── apple_health_service.py
│   │   └── fitbit_service.py
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── meals/
│   │   └── wearables/
│   │
│   └── static/
│
├── migrations/
├── styles/
│
├── test_dashboard_api.py
├── populate_dummy_data.py
├── verify_data.py
└── create_portfolio_pdf.py

API Surface
The application exposes authenticated JSON endpoints for AI and analytics workflows.
Nutrition
GET /api/nutrition-stats
GET /api/goal-progress
GET /api/meal-frequency
GET /api/wearable-integration

AI Coaching
POST /api/analyze
POST /api/coach
GET  /api/coach/daily-tip
GET  /api/coach/weekly-insights
GET  /api/coach/goal-coaching
POST /api/coach/meal-feedback

Dashboard
GET /dashboard/api/nutrition-stats
GET /dashboard/api/goal-progress
GET /dashboard/api/meal-frequency
GET /dashboard/api/wearable-integration
GET /dashboard/api/export-data

Example AI Workflow
                Meal Photo
                    │
                    ▼
             Image Validation
                    │
                    ▼
             OpenAI Vision API
                    │
             ┌──────┴──────┐
             │             │
          Success         Error
             │             │
             ▼             ▼
       Food Detection    Fallback
             │
             ▼
      Portion Estimation
             │
             ▼
      Nutrition / 100g
             │
             ▼
       Serving Calculation
             │
             ▼
       Meal Persistence
             │
             ▼
        AI Meal Analysis
             │
             ▼
       Dashboard Insights

Reliability Engineering
A key design principle of the project is graceful degradation.
The system includes fallbacks for:
- Vision API failures
- Missing OpenAI credentials
- OpenAI package initialization problems
- API response parsing failures
- AI coaching failures
- Nutrition lookup
This gives the application a better user experience when external AI services are unavailable.
Testing & Validation
The repository includes an API verification script covering:
- Nutrition statistics
- Goal progress
- Meal frequency
- Health/wearable data
- Recent meals
Example:
python test_dashboard_api.py

The project also includes data population and validation utilities for development/demo environments.
Local Development
1. Clone
git clone https://github.com/OWAIS086-web/personal-nutrition-ai.git
cd personal-nutrition-ai

2. Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate

Linux/macOS
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment
Create your environment configuration and provide an OpenAI API key:
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=development

Never commit real API credentials.
5. Run
python app.py

The application starts on:
http://localhost:5000

Development Data
The repository includes scripts for generating and validating development/demo data.
python populate_dummy_data.py
python verify_data.py

There are also specialized scripts for data validation and health-goal cleanup.
Why This Project Matters
Personal Nutrition AI demonstrates practical engineering across several AI application layers:
Computer Vision
      +
Generative AI
      +
Structured Data
      +
Personalization
      +
Analytics
      +
Backend Engineering
      +
Security

It is not simply an AI chatbot.
The application connects multimodal AI inference to a complete product workflow:
Image
  ↓
AI Recognition
  ↓
Structured Nutrition
  ↓
Database
  ↓
Analytics
  ↓
Personalized Coaching

Engineering Highlights
This project demonstrates experience with:
- AI vision integration
- Prompt engineering
- OpenAI API integration
- Structured AI output parsing
- AI response validation
- Graceful AI fallbacks
- Personalized AI context construction
- Nutrition calculations
- REST APIs
- Flask application architecture
- SQLAlchemy ORM
- Database migrations
- Authentication
- RBAC-style protected workflows
- CSRF protection
- Rate limiting
- Secure file uploads
- Dashboard analytics
- Health-data modeling
- Data export
- Testing and validation
Important Disclaimer
This project is intended for software demonstration, experimentation, and educational purposes.
AI-generated food recognition and nutritional estimates are approximate and should not be treated as medical advice, diagnosis, or a substitute for a qualified nutrition professional.
Roadmap
Potential future improvements:
- Native Apple HealthKit integration
- Production Fitbit/OAuth integration
- Dedicated food-detection model
- More comprehensive nutrition database
- Barcode scanning
- Recipe generation
- Meal planning
- Grocery-list generation
- Multilingual AI coaching
- Mobile application
- Advanced nutrition forecasting
- Personalized recommendation models
Author
Awais Saeed
Senior Software Engineer | AI/ML Engineer | Python Backend Engineer
GitHub: https://github.com/OWAIS086-web
