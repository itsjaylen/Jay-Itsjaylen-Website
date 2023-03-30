import string
from datetime import datetime, timedelta
from functools import wraps
import hashlib

from flask import jsonify, request, session

from app.api import api
from app.api.tools.apitool import get_attr
from app.extensions import db, cache
from app.models.TwitchScrapper import TwitchMessages
from app.models.YoutubeScrapping import Video, YoutubeChannels
from app.models.account import User


def check_api_key(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        api_key = api_key.translate(str.maketrans("", "", string.whitespace))
        user = User.query.filter_by(api_key=api_key).first()
        if not user or not api_key:
            return jsonify({"error": "Invalid API key"}), 401

        if user.is_admin:
            user.total_request_count += 1
            return fn(*args, **kwargs)

        now = datetime.now()
        if user.last_request_time is None or user.request_count is None:
            user.last_request_time = now
            user.request_count = 1
            user.total_request_count += 1
        if now - user.last_request_time > timedelta(seconds=60):
            user.last_request_time = now
            user.request_count = 1
            user.total_request_count += 1
        if user.request_count >= 10:
            return jsonify({"error": "Rate limit exceeded"}), 429
        else:
            user.request_count += 1
            user.total_request_count += 1

        db.session.commit()
        return fn(*args, **kwargs)

    return decorated


@api.route("/regenerate-api-key", methods=["POST"])
def regenerate_api_key():
    """This function generates a new API key for a user, by first retrieving the user data associated with the
    current API key provided by the client. It then uses the user's username and the request time to generate
    a new API key using the sha256 hashlib algorithm. The new API key is then updated in the database.

    Returns:
        str: The current user's API key."""
    if request.method == "POST":
        current_user_api = request.form.get("current_user_api_key")
        user = User.query.filter_by(api_key=current_user_api).first()
        username = user.username
        request_time = str(datetime.utcnow())

        hash_object = hashlib.sha256()
        hash_object.update(current_user_api.encode())
        hash_object.update(username.encode())
        hash_object.update(request_time.encode())

        new_api_key = hash_object.hexdigest()
        user.api_key = new_api_key
        db.session.commit()

    return current_user_api


# TODO WORK ON THIS
@api.route("/change-password", methods=["POST"])
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        with open("password.txt", "w") as f:
            f.write(new_password)

        # check if new password and confirm password match
        if new_password != confirm_password:
            return jsonify(
                {"message": "New password and confirm password do not match."}
            )


@api.route("/test", methods=["GET"])
@check_api_key
@cache.cached(timeout=60)
def home():
    test = []
    if request.method == "GET":
        api_key = request.headers.get("Authorization")
        user = User.query.filter_by(api_key=api_key).first()
        channels = db.session.query(YoutubeChannels).all()
        for channel in channels:
            test.append(channel.youtube_channel_id)
    return jsonify(test)


@api.route("/youtube/<youtube_channel_id>", methods=["GET"])
@check_api_key
@cache.cached(timeout=30)
def youtube(youtube_channel_id):
    if request.method == "GET":
        videos = (
            Video.query.filter_by(author=youtube_channel_id)
            .order_by(Video.publish_date.desc())
            .all()
        )
        if videos:
            video_list = []
            for video in videos:
                video_attributes = {
                    "id": get_attr("id", video),
                    "url": get_attr("url", video),
                    "title": get_attr("title", video),
                    "author": get_attr("author", video),
                    "publish_date": get_attr("publish_date", video),
                    "description": get_attr("description", video),
                    "views": get_attr("views", video),
                    "length": get_attr("length", video),
                }
                video_list.append(video_attributes)
            return jsonify(videos=video_list)
        else:
            return jsonify(message="No videos found for this channel"), 404


@api.route("/twitch/messages/<username>", methods=["GET"])
@check_api_key
@cache.cached(timeout=30)
def twitch_messages(username):
    if request.method == "GET":
        messages = (
            TwitchMessages.query.filter_by(
                username=username.lower(),
            )
            .order_by(TwitchMessages.timestamp.asc())
            .all()
        )
        if messages:
            message_list = []
            for message in messages:
                message_attributes = {
                    "id": get_attr("id", message),
                    "channel": get_attr("channel", message),
                    "username": get_attr("username", message),
                    "timestamp": get_attr("timestamp", message),
                    "message": get_attr("message", message),
                }
                message_list.append(message_attributes)
            return jsonify(messages=message_list)
        else:
            return jsonify(message="No messages found for this user"), 404
