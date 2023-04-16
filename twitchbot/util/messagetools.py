from models.TwitchScraping import TwitchMessages, TwitchUsers
from tweety.bot import Twitter

from database import get_session


def update_user_stats():
    # create a session
    session = get_session()

    # Get distinct usernames from TwitchMessages table
    users = session.query(TwitchMessages.username.distinct()).all()

    for user in users:
        # Get messages sent by user
        messages = session.query(TwitchMessages).filter_by(username=user[0]).all()

        if len(messages) > 0:
            # Calculate average message length
            total_length = sum([len(message.message) for message in messages])
            average_length = int(total_length / len(messages))

            # Calculate daily average message count
            # first_message_date = datetime.strptime(messages[0].timestamp, "%Y-%m-%d")
            # last_message_date = datetime.strptime(messages[-1].timestamp, "%Y-%m-%d")

            days = 7

            message_count = len(messages)
            # days = (last_message_date - first_message_date).days + 1
            daily_average = int(message_count / days)

            # Update user stats in TwitchUsers table
            user_stats = session.query(TwitchUsers).filter_by(username=user[0]).first()

            if user_stats is not None:
                user_stats.average_message_length = average_length
                user_stats.message_count = message_count
                user_stats.daily_average_message_count = daily_average
            else:
                # Create new user stats
                user_stats = TwitchUsers(
                    username=user[0],
                    average_message_length=average_length,
                    message_count=message_count,
                    daily_average_message_count=daily_average,
                )
                session.add(user_stats)

                session.commit()

    # close the session
    session.close()


def get_tweet(user):
    # proxy = {'http': '45.162.135.201:999', 'https': '45.162.135.201:999'}
    app = Twitter(profile_name=user)
    all_tweets = app.get_tweets(pages=1)

    return all_tweets[0].text
