import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Flask application configuration."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trolley_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = FLASK_ENV == 'development'

    # CORS
    CORS_HEADERS = 'Content-Type'
