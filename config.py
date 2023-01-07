import os
import sys


from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))


# TODO Update variables
class Config:
    PORT = os.environ.get('PORT') or 5000
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    SCRAPPED_VIDEOS_PATH = os.environ.get('SCRAPPED_VIDEOS_PATH')


# FINISH the logger configuration
logger.add(sys.stderr,
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
           filter="my_module",
           level="INFO",
           enqueue=True,
           backtrace=True,
           diagnose=True,)
logger.add("lastest.log", rotation="500 MB", compression="zip")
