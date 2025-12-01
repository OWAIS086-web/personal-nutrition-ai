from flask import Flask
from flask_migrate import Migrate
from nutrition.extensions import db, login_manager, limiter, cache, csrf
from nutrition.controllers.auth_controller import auth_bp
from nutrition.controllers.dashboard_controller import dashboard_bp
from nutrition.controllers.meal_controller import meal_bp
from nutrition.controllers.wearable_controller import wearable_bp
from nutrition.controllers.api_controller import api_bp
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Add CSRF token to template context
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Add custom Jinja2 filters
    @app.template_filter('clean_goal')
    def clean_goal_filter(goal_text):
        """Clean and format health goal text"""
        if not goal_text:
            return goal_text
        
        # Handle single character corruption (when string is iterated as chars)
        if len(str(goal_text)) == 1:
            return ""  # Skip single characters
        
        # Convert to string and clean
        cleaned = str(goal_text).strip()
        
        # Remove emojis
        import re
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"  # emoticons
                                  u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                  u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                  u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                  u"\U00002702-\U000027B0"
                                  u"\U000024C2-\U0001F251"
                                  "]+", flags=re.UNICODE)
        
        cleaned = emoji_pattern.sub('', cleaned).strip()
        
        # Map common goal values to display names
        goal_mapping = {
            'weight_loss': 'Weight Loss',
            'weight_gain': 'Weight Gain',
            'muscle_gain': 'Muscle Gain',
            'maintenance': 'Weight Maintenance',
            'maintain_weight': 'Weight Maintenance',
            'heart_health': 'Heart Health',
            'diabetes_management': 'Diabetes Management',
            'energy_boost': 'Increase Energy',
            'improve_energy': 'Increase Energy',
            'better_sleep': 'Better Sleep',
            'digestive_health': 'Digestive Health',
            'improve_performance': 'Improve Performance'
        }
        
        # Check if it's a known goal
        if cleaned.lower() in goal_mapping:
            return goal_mapping[cleaned.lower()]
        
        # Otherwise, format it nicely
        cleaned = cleaned.replace('_', ' ').title()
        return cleaned
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(meal_bp, url_prefix='/meals')
    app.register_blueprint(wearable_bp, url_prefix='/wearables')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')
    
    # Redirect /logout to /auth/logout for convenience
    @app.route('/logout')
    def logout_redirect():
        from flask import redirect, url_for
        return redirect(url_for('auth.logout'))
    
    return app
