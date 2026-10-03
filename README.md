# Personal Nutrition AI --- AI-Powered Wellness Companion

> **An AI-powered nutrition and wellness platform that turns meal photos
> into structured nutrition insights, tracks daily/macronutrient goals,
> and provides personalized AI coaching.**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20Vision-412991.svg)](https://openai.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791.svg)](https://www.postgresql.org/)

------------------------------------------------------------------------

## Overview

**Personal Nutrition AI** is a full-stack AI wellness application
designed to make nutrition tracking as simple as taking a photo.

Users can upload a meal image and the application uses **OpenAI vision
models** to identify visible foods, estimate serving sizes, and
calculate estimated nutritional values. The platform combines meal data
with dietary preferences, allergies, health goals, activity level,
recent meals, and nutrition history to deliver personalized AI coaching
and insights.

## Core AI Capabilities

### AI Food Recognition

The vision pipeline analyzes uploaded meal images and returns structured
information such as:

``` json
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
```

The application validates AI output, normalizes numeric values, clamps
confidence scores, and calculates serving-level nutrition.

### Vision Model Strategy

``` text
GPT-4o
   ↓
GPT-4o-mini
   ↓
Fallback Food Detection
```

A local fallback nutrition database helps preserve basic functionality
when the external vision API is unavailable.

### AI Nutrition Coaching

`AICoachService` supports:

-   Personalized daily nutrition tips
-   AI meal analysis
-   Weekly nutrition insights
-   Goal-specific coaching
-   Dietary preference awareness
-   Allergy-aware context
-   Recent meal context

Goal-oriented coaching supports areas such as weight loss, muscle gain,
heart health, energy, sleep, and digestive health.

## Personalized AI Context

``` text
User
├── Dietary Preferences
├── Allergies
├── Health Goals
├── Activity Level
├── Units
├── Recent Meals
└── Average Daily Calories
```

This context is incorporated into coaching prompts to generate more
relevant responses.

## Nutrition Tracking

The platform tracks:

-   Calories
-   Protein
-   Carbohydrates
-   Fat
-   Food items
-   Quantity and units
-   Meal type
-   Meal date
-   Meal images

``` text
Per Food
   ↓
Per Meal
   ↓
Daily Totals
   ↓
Weekly Statistics
   ↓
Goal Progress
```

## BMR, TDEE & Macro Calculation

The dedicated `NutritionCalculator` service supports:

-   BMR estimation using the **Mifflin-St Jeor equation**
-   TDEE estimation using activity multipliers
-   Protein, carbohydrate, and fat target calculation
-   Weight-loss, muscle-gain, and maintenance strategies

## Analytics Dashboard

The application provides nutrition analytics including:

-   Daily calories
-   Protein
-   Carbohydrates
-   Fat
-   Total meals
-   Average intake
-   Highest and lowest intake
-   Meal frequency
-   Hourly meal distribution
-   Goal progress

## Apple Health / Health Data Layer

The application contains a health-data model for metrics such as:

-   Steps
-   Calories
-   Distance
-   Heart rate
-   Sleep
-   Active minutes

The Apple Health service maps exported health identifiers into
application metrics.

``` text
HKQuantityTypeIdentifierStepCount
                ↓
              steps

HKQuantityTypeIdentifierHeartRate
                ↓
           heart_rate
```

> Apple Health support currently uses simplified export processing
> rather than native iOS HealthKit integration.

## Data Export

Nutrition information can be exported through API workflows in:

-   JSON
-   CSV

## Security

Security-related implementation includes:

-   Flask-Login authentication
-   bcrypt password hashing
-   CSRF protection
-   Flask-WTF validation
-   API rate limiting
-   Authenticated routes
-   Secure filename handling
-   Upload limits

## AI Interaction Logging

AI requests can be persisted using the `AILog` model:

``` text
User
Request Type
Prompt
Response
```

This provides a foundation for debugging, AI usage analytics, prompt
evaluation, and future system improvement.

## Resilient AI Architecture

``` text
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
```

The AI coaching layer also provides fallback responses when the external
AI service is unavailable.

## System Architecture

``` text
                         ┌───────────────────────┐
                         │     Web Interface     │
                         │    HTML/CSS/JS/PWA    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      Flask App        │
                         │ Auth / Dashboard/API  │
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
                       SQLAlchemy ORM
                             │
                             ▼
                      SQLite / PostgreSQL
```

## Technology Stack

**Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate,
Flask-Login, Flask-WTF, Flask-Limiter, WTForms, Werkzeug

**AI:** OpenAI GPT-4o, GPT-4o-mini, OpenAI Chat Completions, prompt
engineering, multimodal food recognition

**Data:** SQLAlchemy, SQLite, PostgreSQL support, Pillow, Requests, JSON

**Frontend:** HTML5, CSS3, JavaScript, responsive dashboard UI,
PWA/service-worker support

## Project Structure

``` text
personal-nutrition-ai/
├── app.py
├── config.py
├── requirements.txt
├── nutrition/
│   ├── __init__.py
│   ├── extensions.py
│   ├── controllers/
│   │   ├── api_controller.py
│   │   ├── auth_controller.py
│   │   ├── dashboard_controller.py
│   │   ├── meal_controller.py
│   │   └── wearable_controller.py
│   ├── forms/
│   ├── models/
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── wearable.py
│   │   └── ai_log.py
│   ├── services/
│   │   ├── food_vision.py
│   │   ├── ai_coach.py
│   │   ├── nutrition_calc.py
│   │   ├── apple_health_service.py
│   │   └── fitbit_service.py
│   ├── templates/
│   └── static/
├── migrations/
├── styles/
├── test_dashboard_api.py
├── populate_dummy_data.py
├── verify_data.py
└── create_portfolio_pdf.py
```

## API Surface

### Nutrition & Analytics

``` http
GET /api/nutrition-stats
GET /api/goal-progress
GET /api/meal-frequency
GET /api/wearable-integration
```

### AI Coaching

``` http
POST /api/analyze
POST /api/coach
GET  /api/coach/daily-tip
GET  /api/coach/weekly-insights
GET  /api/coach/goal-coaching
POST /api/coach/meal-feedback
```

### Dashboard

``` http
GET /dashboard/api/nutrition-stats
GET /dashboard/api/goal-progress
GET /dashboard/api/meal-frequency
GET /dashboard/api/wearable-integration
GET /dashboard/api/export-data
```

## AI Meal Workflow

``` text
Meal Photo
    │
    ▼
Image Validation
    │
    ▼
OpenAI Vision
    │
    ├── Success
    │      ↓
    │ Food Detection
    │      ↓
    │ Portion Estimation
    │      ↓
    │ Nutrition Calculation
    │
    └── Failure → Fallback Detection
                   │
                   ▼
             Meal Persistence
                   │
                   ▼
              AI Coaching
                   │
                   ▼
            Dashboard Insights
```

## Testing

Run the dashboard API test:

``` bash
python test_dashboard_api.py
```

Development/demo utilities are also included for populating and
validating data.

## Local Development

### Clone

``` bash
git clone https://github.com/OWAIS086-web/personal-nutrition-ai.git
cd personal-nutrition-ai
```

### Create a Virtual Environment

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

### Configure Environment

``` env
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=development
```

> Never commit real API keys or production credentials.

### Run

``` bash
python app.py
```

Open:

``` text
http://localhost:5000
```

## Engineering Highlights

This project demonstrates:

-   Multimodal AI integration
-   OpenAI Vision API integration
-   Prompt engineering
-   Structured AI output parsing
-   AI response validation
-   Graceful AI fallbacks
-   Personalized context construction
-   Nutrition calculations
-   Flask backend architecture
-   REST APIs
-   SQLAlchemy ORM
-   Database migrations
-   Authentication
-   CSRF protection
-   API rate limiting
-   Secure file uploads
-   Dashboard analytics
-   Health-data modeling
-   Data export
-   Testing and validation

## Roadmap

Potential future improvements include:

-   Native Apple HealthKit integration
-   Production Fitbit/OAuth integration
-   Dedicated food-detection models
-   Comprehensive nutrition database
-   Barcode scanning
-   AI recipe generation
-   Personalized meal planning
-   Grocery-list generation
-   Multilingual AI coaching
-   Mobile applications
-   Advanced nutrition forecasting
-   Personalized recommendation models

## Disclaimer

> **Personal Nutrition AI is intended for software demonstration,
> experimentation, and educational purposes. AI-generated food
> recognition and nutritional estimates are approximate and should not
> be treated as medical advice, diagnosis, or a substitute for a
> qualified healthcare or nutrition professional.**

## Author

### Awais Saeed

**Senior Software Engineer \| AI/ML Engineer \| Python Backend
Engineer**

-   GitHub: [OWAIS086-web](https://github.com/OWAIS086-web)
-   Project: [Personal Nutrition
    AI](https://github.com/OWAIS086-web/personal-nutrition-ai)

------------------------------------------------------------------------

::: {align="center"}
### Built with Python, Flask, OpenAI Vision & Applied AI Engineering

**If you find this project useful, consider giving the repository a
star.**
:::
