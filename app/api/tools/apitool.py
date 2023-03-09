import hashlib
from app.models.TwitchScrapper import TwitchMessages, TwitchUsers
from app.models.YoutubeScrapping import Video, YoutubeChannels
from datetime import datetime, timedelta
from app.extensions import db
import zlib
import sys
import re
from loguru import logger
import emoji


def level_filter(record):
    return record["level"].name in ["DEBUG", "INFO", "ERROR"]


logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    filter=level_filter,
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
logger.add(sink="./logs/apitools.log", rotation="500 MB", compression="zip")


def compress_message(message):
    return zlib.compress(message.encode())


def decompress_message(compressed_message):
    return zlib.decompress(compressed_message).decode()


def get_attr(attr_name, obj) -> str:
    if hasattr(obj, attr_name):
        return getattr(obj, attr_name)
    else:
        return "N/A"


def hash_sha256(string):
    string_bytes = string.encode()
    sha256 = hashlib.sha256()
    sha256.update(string_bytes)
    return sha256.hexdigest()


def strip_u_e0000(input_str):
    return re.sub("\U000e0000", "", input_str)


def strip_unicode(string):
    stripped = ""
    for char in string:
        if ord(char) < 128 or emoji.emojize(char) != char:
            stripped += char
            stripped = stripped.strip("")
            stripped = re.sub("\W+", " ", string).strip()
    return stripped


def update_user_stats():
    # Get distinct usernames from TwitchMessages table
    users = TwitchMessages.query.with_entities(TwitchMessages.username).distinct()

    for user in users:
        # Get messages sent by user
        messages = TwitchMessages.query.filter_by(username=user[0]).all()

        if len(messages) > 0:
            # Calculate average message length
            total_length = sum([len(message.message) for message in messages])
            average_length = int(total_length / len(messages))

            # Calculate daily average message count
            first_message_date = datetime.strptime(
                messages[0].timestamp, "%Y-%m-%d %H:%M:%S"
            )
            last_message_date = datetime.strptime(
                messages[-1].timestamp, "%Y-%m-%d %H:%M:%S"
            )
            message_count = len(messages)
            days = (last_message_date - first_message_date).days + 1
            daily_average = int(message_count / days)

            # Update user stats in TwitchUsers table
            user_stats = TwitchUsers.query.filter_by(username=user[0]).first()
            user_stats.average_message_length = average_length
            user_stats.message_count = message_count
            user_stats.daily_average_message_count = daily_average

            db.session.commit()
