"""
Configuration settings for the Material Generator API.
"""

import os
import logging

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    
    # Model settings
    MODEL_DIR = os.environ.get('MODEL_DIR') or 'app/trained_material_vae'
    NLP_MODEL_NAME = os.environ.get('NLP_MODEL_NAME') or 'microsoft/phi-3-mini-4k-instruct'
    USE_GPU = os.environ.get('USE_GPU', 'true').lower() == 'true'
    LOAD_MODELS_AT_STARTUP = os.environ.get('LOAD_MODELS_AT_STARTUP', 'false').lower() == 'true'
    
    # File settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER') or 'generated_materials'
    
    # Generation settings
    DEFAULT_SAMPLES = 5
    DEFAULT_TEMPERATURE = 1.2
    
    # Logging settings
    LOG_LEVEL = logging.INFO
    LOG_FILE = os.environ.get('LOG_FILE') or 'material_generator.log'
    
    @staticmethod
    def init_app(app):
        """Initialize the app with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOAD_MODELS_AT_STARTUP = False
    
    # Use smaller/faster models for testing
    NLP_MODEL_NAME = 'microsoft/phi-2'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = logging.INFO
    
    # In production, enforce proper secret key
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Validate that SECRET_KEY has been set
        if app.config['SECRET_KEY'] == 'hard-to-guess-string':
            app.logger.warning("WARNING: Using default secret key in production!")
        
        # Set up production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Configure rotating file handler for production
        file_handler = RotatingFileHandler(
            cls.LOG_FILE, maxBytes=10485760, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}