import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
USERNAME = os.getenv('TRIVIA_USERNAME')
PASSWORD = os.getenv('TRIVIA_PASSWORD')

# IMPLEMENT DATABASE URL AND SETTINGS
SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/fyyur2"
SQLALCHEMY_TRACK_MODIFICATIONS = False
