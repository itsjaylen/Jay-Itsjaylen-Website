from bs4 import BeautifulSoup
import requests
import cloudscraper


def scrap_twitch():
    scraper = cloudscraper.create_scraper(delay=10, browser='chrome') 
    url = "https://twitchtracker.com/subscribers"
    info = scraper.get(url).text
    soup = BeautifulSoup(info, "html.parser")
    streamers = soup.find_all('td')

    top_20 = []

    for streamer in streamers:
        #print(streamer.get_text().strip())
        top_20.append(streamer.get_text().strip())
        
    #top_20 = top_20[3:]

    #print(top_20)
        


    #print(top_20[0:11])





    n = 11


    result = []

    for idx in range(0, len(top_20), n):
        result.append(top_20[idx:idx+n])

    #print(len(result))
    return result


def get_subs_from_tracker(channel):
    URL = f'https://twitchtracker.com/{channel.lower()}/subscribers'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        subs_counter = soup.find("span", {"class": "to-number"}).getText()
        return subs_counter
    except:
        return None
    