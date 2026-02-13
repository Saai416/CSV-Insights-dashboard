import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "data", "app.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE_MB', 5)) * 1024 * 1024  # 5MB default
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Report settings
    MAX_STORED_REPORTS = 5
    
    @staticmethod
    def validate():
        """Validate that required configuration is present."""
        if not Config.GROQ_API_KEY:
            print("WARNING: GROQ_API_KEY not set. LLM features will not work.")
