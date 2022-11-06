
import snscrape.modules.twitter as sntwitter
import pandas as pd

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
        f.write(tweet[2])