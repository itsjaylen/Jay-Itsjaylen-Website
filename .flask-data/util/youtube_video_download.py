import logging
import time
import logging
import os
import re
import urllib.request


import requests
from bs4 import BeautifulSoup
from pytube import YouTube, request
from views import logger


valid_links = ["https://www.youtube.com/c/", "https://www.youtube.com/channel/",
               "https://www.youtube.com/feeds/videos.xml?channel_id="]


request.default_range_size = 10485760


@logger.catch
def process_channel(channel):
    if channel.startswith("https://www.youtube.com/feeds/videos.xml?channel_id="):
        html = requests.get(channel)
        soup = BeautifulSoup(html.text, "xml")
        entry = soup.find("entry")
        link = entry.find("link")

        process_video(link["href"])

    try:
        html = requests.get(channel + "/videos").text
        info = re.search('(?<={"label":").*?(?="})', html).group()
        #date = re.search('\d+ \w+ ago.*seconds ', info).group()
        url = "https://www.youtube.com/watch?v=" + \
            re.search('(?<="videoId":").*?(?=")', html).group()
    except Exception:
        pass

    process_video(url)


@logger.catch
def process_video(url):
    blacklisted_chars = ["<", ">", ":", '"', "/",
                         "backslash", "|", "?", "*", ".", ".."]

    video = YouTube(
        url,
        on_complete_callback=None,
        on_progress_callback=None)
    title = video.title

    for char in blacklisted_chars:
        title = title.replace(char, "")

    try:
        video.streams.get_highest_resolution().download(
            f"{os.getcwd()}/.flask-data/static/videos/{video.author}/{title}")

        with open(f"{os.getcwd()}/.flask-data/static/videos/{video.author}/{title}/{title}.txt", "a", encoding="utf-8") as f:
            f.truncate(0)
            f.write(f"""
                    Video Title: {title}{video.title}\n
                    Video Upload Date: {video.publish_date}\n
                    Video Description: {video.description}\n
                    Video Views: {video.views}\n
                    Video Length: {round(video.length / 60, 2)} minutes\n
                    """)

            with urllib.request.urlopen(video.thumbnail_url) as f:
                urllib.request.urlretrieve(
                    video.thumbnail_url, f"{os.getcwd()}/.flask-data/static/videos/{video.author}/{title}/{title}.png")

        print(f"Downloaded: {video.title} successfully")

    except Exception as e:
        logging.error(
            f"Error downloading {video.title} from {video.author}\n{url}\n{e}\n")


@logger.catch
def video_function():
    try:
        with open("channels.txt", encoding="utf-8") as channels:
            for channel in channels:
                for link in valid_links:
                    if channel.startswith(link):
                        try:
                            print(f"Processing {channel}")
                            process_channel(channel)
                        except Exception:
                            pass
                else:
                    continue

    except KeyboardInterrupt:
        print("Ending Processor")
        exit(-1)


@logger.catch
def get_videos():
    paths = []
    paths_clean = []
    channel_names = []
    for root, dirs, files in os.walk(f'{os.getcwd()}/.flask-data/static/videos/'):
        for file in files:
            if file.lower().endswith(".mp4".lower()):
                paths.append(os.path.join(root, file))
                for path in paths:
                    path_list = path.split(os.path.sep)[-4:]
                    clean_path = '/'.join(path_list)
                    
                    if clean_path not in paths_clean:
                        paths_clean.append(clean_path)

                        #channel_names.append(path_list[1])
    #print(paths_clean)

    return paths_clean
