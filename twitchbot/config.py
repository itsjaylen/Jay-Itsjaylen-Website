import os

from dotenv import load_dotenv

load_dotenv()

class TwitchConfig:
    """Configuration for twitch"""
    DATABASE = os.getenv("DATABASE_URL")
    TOKEN = os.getenv("TOKEN")
    PREFIX = os.getenv("PREFIX")
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    DATABASE_URL = os.getenv("DATABASE_URL")