import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dobrodelo-super-secret-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database URL configuration
    # Default to sqlite:///app.db if not specified or fallback
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
