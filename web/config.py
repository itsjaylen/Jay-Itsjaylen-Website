import os

from dotenv import load_dotenv

load_dotenv()


from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))


# TODO Update variables for .env file with venv using python-dotenv make interchangeable inside a database config
class Config:
    """Config For the main app"""

    PORT = os.environ.get("PORT") or 5000
    SECRET_KEY = "SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SCRAPPED_VIDEOS_PATH = os.environ.get("SCRAPPED_VIDEOS_PATH")
    SCRAPPING_ENABLED = False
    TWITCH_LISTENER_ENABLED = False


class YoutubeConfig:
    """Configuration for youtube"""

    YOUTUBE_VIDEOS_PATH = "./instance/videos"
    YOUTUBE_VIDEO_DELAY = 1

class TwitchConfig:
    """Configuration for twitch"""
    TOKEN = os.getenv('TOKEN')
    PREFIX = os.getenv('PREFIX')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    
    