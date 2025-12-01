import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('086086086086') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = "sqlite:///nutrition.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB
    UPLOAD_FOLDER = 'nutrition/static/uploads'
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or "api-key"
    # FITBIT_CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID')
    # FITBIT_CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET')
    
    # Rate limiting
   
    
    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
