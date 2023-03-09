import matplotlib.pyplot as plt
import numpy as np
from app.models.TwitchScrapper import TwitchUsers


def generate_top_users_graph():
    # Query the database to get the top users with the most amount of messages
    top_users = (
        TwitchUsers.query.order_by(TwitchUsers.message_count.desc()).limit(10).all()
    )

    # Extract the usernames and message counts
    usernames = [user.username for user in top_users]
    message_counts = [user.message_count for user in top_users]

    # Create a bar chart to display the message counts for each user
    plt.bar(usernames, message_counts)
    plt.title("Top Users by Message Count")
    plt.xlabel("Usernames")
    plt.ylabel("Message Count")

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha="right")

    # Save the graph as an image file
    plt.savefig("./instance/top_users.png")
