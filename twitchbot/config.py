import os

from dotenv import load_dotenv

load_dotenv()

class TwitchConfig:
    """Configuration for twitch"""
    TOKEN = ""
    PREFIX = "+"
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')