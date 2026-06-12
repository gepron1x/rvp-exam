import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = 'secret-key'

# SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False
REMEMBER_COOKIE_DURATION= 31 * 24 * 3600
PERMANENT_SESSION_LIFETIME=timedelta(days=7)
SQLALCHEMY_ECHO = True
