import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = 'secret-key'

# SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
