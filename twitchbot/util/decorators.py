import functools

from database import get_session
from models.TwitchScraping import TwitchUsers
from twitchio.ext import commands
import sys
import os.path
from loguru import logger

session = get_session()


def authorized_users(command_function):
    @functools.wraps(command_function)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        auth_users = get_auth_users()
        if ctx.author.name in auth_users:
            # The user is authorized to use the command, so execute the command function
            return await command_function(self, ctx, *args, **kwargs)
        else:
            # The user is not authorized, so send an error message
            pass

    return wrapper


def get_auth_users():
    users = session.query(TwitchUsers).all()
    return [user.username for user in users]


def admin_users(command_function):
    @functools.wraps(command_function)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        auth_users = get_auth_users()
        user = session.query(TwitchUsers).filter_by(username=ctx.author.name).first()
        if user and user.role == "admin" and ctx.author.name in auth_users:
            # The user is authorized to use the command and has the admin role, so execute the command function
            return await command_function(self, ctx, *args, **kwargs)
        else:
            # The user is not authorized or does not have the admin role, so send an error message
            pass

    return wrapper


def get_logger_from_filepath(filepath):
    filename = os.path.splitext(os.path.basename(filepath))[0]
    return get_logger(filename)


def get_logger(filename):
    log_path = f"./logs/{filename}.log"
    logger.remove()
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        filter=level_filter,
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(sink=log_path, rotation="500 MB", compression="zip")
    return logger


def log_errors(logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(e)
                raise

        return wrapper

    return decorator


def level_filter(record, level):
    if record["level"].name == level:
        return True
    if record["level"].name == "ERROR" and level == "CRITICAL":
        return True
    return False
