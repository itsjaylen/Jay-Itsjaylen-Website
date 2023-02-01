import os


from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))


# TODO Update variables for .env file with venv using python-dotenv make interchangeable inside a database config
class Config:
    """Config For the main app"""

    PORT = os.environ.get("PORT") or 5000
    SECRET_KEY = "SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/database.db?check_same_thread=False"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SCRAPPED_VIDEOS_PATH = os.environ.get("SCRAPPED_VIDEOS_PATH")
    SCRAPPING_ENABLED = False


class YoutubeConfig:
    """Configuration for youtube"""

    YOUTUBE_VIDEOS_PATH = "./instance/videos"
    YOUTUBE_VIDEO_DELAY = 1
