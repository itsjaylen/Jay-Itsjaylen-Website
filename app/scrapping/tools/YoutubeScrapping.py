import logging
import os
import re
import sys
import urllib.request

import ffmpeg
import requests
from bs4 import BeautifulSoup
from loguru import logger
from pytube import YouTube

from app.models.YoutubeScrapping import Video, YoutubeChannels
from config import YoutubeConfig


#TODO compress the video
class YoutubeScraper:
    """Class for scraping youtube channels"""

    def __init__(self):
        self.valid_links = ["https://www.youtube.com/c/", "https://www.youtube.com/channel/",
                            "https://www.youtube.com/feeds/videos.xml?channel_id="]

        self.blacklisted_chars = ["<", ">", ":", '"', "/",
                                  "backslash", "|", "?", "*", ".", ".."]

        # Define a filter function

        def level_filter(record):
            return record['level'].name in ['DEBUG', 'INFO', 'ERROR']

        # FINISH the logger configuration
        logger.add(sys.stderr,
                   format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
                   filter=level_filter,
                   level="INFO",
                   enqueue=True,
                   backtrace=True,
                   diagnose=True,
                   )
        logger.add(sink="./logs/YoutubeScrapping.log",
                   rotation="500 MB", compression="zip")

    @logger.catch
    def process_channel(self, channel: str, app: str, db: str):
        """Process a channel from database."""
        if channel.startswith("https://www.youtube.com/feeds/videos.xml?channel_id="):
            response = requests.get(channel)
            soup = BeautifulSoup(response.text, 'xml')
            latest_video = soup.find('entry')
            link_element = latest_video.find('link')
            video_link = link_element['href']

            self.process_video(video_link, app, db)

        else:
            try:
                html = requests.get(channel + "/videos").text
                info = re.search('(?<={"label":").*?(?="})', html).group()
                #date = re.search('\d+ \w+ ago.*seconds ', info).group()
                url = "https://www.youtube.com/watch?v=" + \
                    re.search('(?<="videoId":").*?(?=")', html).group()
                self.process_video(url, app, db)
            except AttributeError:
                pass

    # TODO Clean this code up

    @logger.catch
    def process_video(self, url: str, app: str, db: str):
        """Process a video from database."""

        video = YouTube(
            url)
        title = video.title

        for char in self.blacklisted_chars:
            title = title.replace(char, "")

        try:
            try:
                video.streams.get_highest_resolution().download(
                    f"{YoutubeConfig.YOUTUBE_VIDEOS_PATH}/{video.author}/{title}")
                logger.success(f"Downloaded: `{video.title}` successfully")
            except FileExistsError:
                logging.warn(f"{video.title} already exists")
            except AttributeError:
                try:
                    video.streams.get_highest_resolution().download(
                        f"{YoutubeConfig.YOUTUBE_VIDEOS_PATH}/unknown_author/{title}")
                    logger.success(f"Downloaded: `{video.title}` successfully")
                except FileExistsError:
                    logging.warn(f"{video.title} already exists")

            with app.app_context():
                existing_video = Video.query.filter_by(
                    title=title, author=video.author).first()
                if existing_video is None:
                    try:
                        db.session.add(Video(url=url, title=title, author=video.author, publish_date=video.publish_date,
                                             description=video.description, views=video.views, length=round(video.length / 60, 2)))
                        db.session.commit()
                    except Exception as e:
                        logger.error(e)

                    with urllib.request.urlopen(video.thumbnail_url) as f:
                        urllib.request.urlretrieve(
                            video.thumbnail_url, f"{YoutubeConfig.YOUTUBE_VIDEOS_PATH}/{video.author}/{title}/{title}.png")
                else:
                    logger.warning("Video already exists in the database")

        except Exception as e:
            logging.error(
                f"Error downloading {video.title} from {video.author}\n{url}\n{e}\n")

    @logger.catch
    def video_function(self, app: str, db: str):
        """Main function for scraping youtube channels."""
        try:
            with app.app_context():
                channels = db.session.query(YoutubeChannels).all()
                for channel in channels:
                    for link in self.valid_links:
                        if channel.youtube_channel_id.startswith(link):
                            self.process_channel(
                                channel.youtube_channel_id, app, db)
        except Exception as e:
            logger.error(e)

@logger.catch
def get_videos():
    paths = []
    paths_clean = []
    channel_names = []
    for root, dirs, files in os.walk(YoutubeConfig.YOUTUBE_VIDEOS_PATH):
        for file in files:
            if file.lower().endswith(".mp4".lower()):
                paths.append(os.path.join(root, file))
                for path in paths:
                    path_list = path.split(os.path.sep)[-4:]
                    clean_path = '/'.join(path_list)

                    if clean_path not in paths_clean:
                        paths_clean.append(clean_path)

    return paths_clean
