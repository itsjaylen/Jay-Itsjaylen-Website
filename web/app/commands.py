import hashlib
import secrets
import sys
import time
from typing import Optional

import click
import requests
from fuzzywuzzy import fuzz
from loguru import logger

from app.extensions import bcrypt, db
from app.models.account import User
from app.models.YoutubeScrapping import Video, YoutubeChannels
from app.scrapping.tools.YoutubeScrapping import get_videos
from app.models.TwitchScrapper import TwitchChannels, TwitchMessages, TwitchUsers

# TODO UPDATE THE COMMANDS/ADD MORE COMMANDS


# Define a filter function
def level_filter(record):
    return record["level"].name in ["DEBUG", "INFO", "ERROR"]


# FINISH the logger configuration
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    filter=level_filter,
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
logger.add(sink="./logs/commands.log", rotation="500 MB", compression="zip")


# TODO ADD HELP TO COMMANDS
def configure_cli(app):
    @app.cli.command()
    def init_db():
        """Initializes the database."""
        db.drop_all()
        db.create_all()

    @app.cli.command()
    def create_db():
        """Creates the database."""
        db.create_all()

    @app.cli.command()
    def db_upgrade():
        #migrate.upgrade()
        logger.info("Database upgraded.")

    @app.cli.command()
    def db_downgrade():
        #migrate.downgrade()
        logger.info("Database downgraded.")

    # TODO add the role type to the command
    @app.cli.command()
    @click.option(
        "--username",
        help="The username of the account.",
        default="username",
        required=True,
    )
    @click.option(
        "--password", help="The password of the account.", default=None, required=False
    )
    @click.option(
        "--role", help="The role of the account.", default="Default", required=False
    )
    @click.option(
        "--is-admin", help="Is the account an admin?", default=False, required=True
    )
    def create_account(
        username: str, password: Optional[str], role: Optional[str], is_admin: bool
    ) -> str:
        """
        Creates an account with the provided username, password, and is_admin status.
        If the provided password is None, it will generate a secure 12 characters (letters and digits) password and print it to the console for the user to see.
        If the provided username already exists in the database, it will add a number at the end of the username to make it unique.
        The account will be stored in the database and the api_key will be generated by using the hashlib library.
        If the account is created successfully, it will return a log statement with the account's details.
        If any exception is raised, it will return the error and rollback the transaction.

        Args:
            username (str): The username of the account. Default is "username".
            password (str): The password of the account. Default is None.
            is_admin (bool): Is the account an admin? Default is False.

        Returns:
            Log statement with account details if the account is created successfully.
            Error statement if an exception is raised.
        """
        try:
            if password is None:
                password = secrets.token_hex(12)
            if User.query.filter_by(username=username).first():
                counter = 1
                while User.query.filter_by(username=f"{username}{counter}").first():
                    counter += 1
                username = f"{username}{counter}"
                print("The username already exist, your new username is:", username)
            hashed_password = bcrypt.generate_password_hash(password)
            hash_object = hashlib.sha256()
            hash_object.update(username.encode())
            hash_object.update(password.encode())
            api_key = hash_object.hexdigest()
            new_user = User(
                username=username,
                password=hashed_password,
                api_key=api_key,
                is_admin=is_admin,
                role=role,
            )
            db.session.add(new_user)
            db.session.commit()
            logger.info(
                f"Created account with username of `{username}`, password of `{password}` and api-key of `{api_key}`."
            )
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @logger.catch
    @app.cli.command()
    @click.option("--channel", help="The youtube channel id.")
    @click.option("--load", help="Loads a list channels from a file")
    def add_channel(channel, load):
        """Adds channel to db."""
        if load:
            with open(load, "r") as file:
                for line in file:

                    try:
                        new_channel = YoutubeChannels(youtube_channel_id=line.strip())
                        db.session.add(new_channel)
                        db.session.commit()
                        logger.info(f"{line.strip()} added to database.")
                    except Exception as e:
                        print("Channel already in database.")
                        logger.error(e)
                        db.session.rollback()
                        print("Channel already in database.")

        if channel:
            try:
                new_channel = YoutubeChannels(youtube_channel_id=channel)
                db.session.add(new_channel)
                db.session.commit()
                logger.info(f"{channel} added to database.")
            except Exception as e:
                logger.error(e)
                print("Channel already in database.")
                db.session.rollback()

    @logger.catch
    @app.cli.command()
    @click.option(
        "--channel", help="The youtube channel id.", default=None, required=True
    )
    def remove_channel(channel):
        """Removes youtube channel the database."""
        if channel.casefold() == "all":
            try:
                channels = YoutubeChannels.query.all()
                for channel in channels:
                    db.session.delete(channel)
                    db.session.commit()
                    logger.info(f"{channel} removed from database.")
            except Exception as e:
                logger.error(e)
                logger.warning("Channel not in database.")
                db.session.rollback()
        else:
            try:
                del_channel = YoutubeChannels.query.filter_by(
                    youtube_channel_id=channel
                ).first()
                db.session.delete(del_channel)
                db.session.commit()
                logger.info(f"{channel} removed from database.")
            except Exception as e:
                logger.error(e)
                logger.warning("Channel not in database.")
                db.session.rollback()

    @logger.catch()
    @app.cli.command()
    def list_channels():
        """Lists all channels in the database."""
        try:
            channels = YoutubeChannels.query.all()
            for channel in channels:
                print(channel.youtube_channel_id)
        except Exception as e:
            logger.error(e)

    @app.cli.command()
    @click.option("--query", help="query the database", required=True)
    def search_db(query):
        """Searches the database."""
        query = query.lower()
        videos = Video.query.filter(db.or_(Video.author.like(f"%{query}%"))).all()
        for video in videos:
            author = video.author
            score = fuzz.token_set_ratio(author.lower(), query)
            print(f"{author} - Score: {score}")

    @app.cli.command()
    def get_videos_test():
        """Gets videos from database."""
        for video_path in get_videos():
            print(video_path)

    @app.cli.command()
    def api_get_request():
        """Test the api"""
        headers = {"Authorization": ""}
        response = requests.get("http://192.168.50.232:7000/api/test", headers=headers)

        if response.status_code == 401:
            print(response.status_code)
        if response.status_code == 200:
            print(response.text)

        else:
            print(f"Error {response.status_code}")
            print(response.text)

    @app.cli.command()
    def api_post_request():
        """Test the api"""
        headers = {"Content-type": "application/json"}
        data = {
            "Authorization": "",
            "poster": "test",
        }
        try:
            response = requests.post(
                "http://192.168.50.232:7000/api/poster", json=data, headers=headers
            )
            response.raise_for_status()
            print(response.status_code)
            print(response.json())
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                print("Unauthorized: Check your API key")
            if err.response.status_code == 429:
                retry_after = int(err.response.headers.get("Retry-After", 30))
                print(f"Too Many Requests, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                api_post_request()
            else:
                print("Error:", err)
        except requests.exceptions.RequestException as err:
            print("Error:", err)

    @app.cli.command()
    def api_get():
        """Test the api"""
        headers = {"Authorization": ""}
        response = requests.get(
            "https://jay.itsjaylen.com/api/youtube/LongBeachGriffy", headers=headers
        )

        if response.status_code == 401:
            print(response.status_code)
        if response.status_code == 200:
            # print(response.text)
            video_data = response.json()
            video_title = video_data["videos"][0]["title"]
            print(video_title)
            print(video_data)

        else:
            print(f"Error {response.status_code}")

    @app.cli.command()
    @click.option("--channel", help="Twitch channel chat that will be scrapped for messages", required=True)
    def add_twitch_channel(channel):
        """Adds twitch channel to db."""
        try:
            channel = f"#{channel.strip()}"
            existing_channel = TwitchChannels.query.filter_by(channel=channel).first()
            if existing_channel:
                logger.info(f"{channel} already exists in database.")
                return
            new_channel = TwitchChannels(channel=channel)
            db.session.add(new_channel)
            db.session.commit()
            logger.info(f"{channel} added to database.")
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @app.cli.command()
    @click.option("--channel", help="Remove twitch channel thats being scraped", required=True)
    def remove_twitch_channel(channel):
        """Remove twitch channel from db."""
        try:
            del_channel = TwitchChannels.query.filter_by(channel=channel.strip()).first()
            if not del_channel:
                logger.info(f"{channel} does not exist in database.")
                return
            db.session.delete(del_channel)
            db.session.commit()
            logger.info(f"{channel} removed from database.")
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @app.cli.command()
    @click.option("--username", help="Twitch user that will be scrapped for messages", required=True)
    def add_twitch_username(username):
        """Adds twitch user to db."""
        try:
            existing_username = TwitchUsers.query.filter_by(username=username.strip()).first()
            if existing_username:
                logger.info(f"{username} already exists in database.")
                return
            new_username = TwitchUsers(username=username.strip())
            db.session.add(new_username)
            db.session.commit()
            logger.info(f"{username} added to database.")
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @app.cli.command()
    @click.option("--username", help="Twitch user that will be scrapped for messages", required=True)
    def remove_twitch_username(username):
        """Remove twitch user from db."""
        try:
            del_username = TwitchUsers.query.filter_by(username=username.strip()).first()
            if not del_username:
                logger.info(f"{username} does not exist in database.")
                return
            db.session.delete(del_username)
            db.session.commit()
            logger.info(f"{username} removed from database.")
        except Exception as e:
            logger.error(e)
            db.session.rollback()

        
        
        