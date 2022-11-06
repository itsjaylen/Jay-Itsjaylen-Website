from bs4 import BeautifulSoup
import requests
import cloudscraper
import asyncio
import snscrape.modules.twitter as sntwitter
import pandas as pd


def scrap_twitch():
    scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
    url = "https://twitchtracker.com/subscribers"
    info = scraper.get(url).text
    soup = BeautifulSoup(info, "html.parser")
    streamers = soup.find_all('td')

    top_20 = []

    for streamer in streamers:
        # print(streamer.get_text().strip())
        top_20.append(streamer.get_text().strip())

    #top_20 = top_20[3:]

    # print(top_20)

    # print(top_20[0:11])

    n = 11

    result = []

    for idx in range(0, len(top_20), n):
        result.append(top_20[idx:idx+n])

    # print(len(result))
    return result


def get_subs_from_tracker(channel):
    URL = f'https://twitchtracker.com/{channel.lower()}/subscribers'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(URL, headers=HEADERS, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        subs_counter = soup.find(
            "span", {"class": "to-number"}).getText()  # type: ignore
        return subs_counter
    except:
        return "None: Channel not found"


def is_live(channel):
    URL = f'https://www.twitch.tv/{channel.lower()}'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(URL, headers=HEADERS, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        if 'isLiveBroadcast' in soup:
            return True
        else:
            return False
    except:
        return False

# print(get_subs_from_tracker("yourragegaming"))


async def get_tweets():
    query = "(from:YourRAGEz)" # Use the link below to make search term more advanced:
    # https://twitter.com/search-advanced
    # example tweets:
    ## "(from:PolestarCars)"
    ## "sustainability (from:elonmusk) until:2022-10-27 since:2010-01-01"

    tweets = []
    limit = 1 # how many tweets you want
    for tweet in sntwitter.TwitterSearchScraper(query).get_items():

        #print(vars(tweet))
        #break
        if len(tweets) == limit:
            break
        else:
            print(tweet.content)
            tweets.append([tweet.date, tweet.user.username, tweet.content])

    df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
    print(df)

    with open("tweets.txt", "a+") as f:
        for tweet in tweets:
            return(tweet[2])
        
