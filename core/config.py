# core/config.py

import os
from dotenv import load_dotenv

# Load the .env file immediately when this file is imported
load_dotenv()

class Settings:
    # 1. Database
    DATABASE_URL = "sqlite:///./app.db"

    # 2. Security
    # We try to get it from .env, but if missing, we warn the user (or fail)
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Defaults
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

    # 3. App Info
    PROJECT_NAME = "Karya 2 Work Hub"
    VERSION = "1.0.0"

# Create a single instance of the settings to use everywhere
settings = Settings()