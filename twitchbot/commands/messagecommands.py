import asyncio
from datetime import datetime

import aiohttp
from config import TwitchConfig
from database import get_session
from models.TwitchScraping import TwitchMessages, TwitchUsers, TwitchMessagesLegacy
from twitchio.ext import commands
from util.decorators import authorized_users, log_errors
from util.messagetools import update_user_stats
from sqlalchemy import func



async def get_user_data(username, oauth_token):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": TwitchConfig.CLIENT_ID,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return data.get("data", [])[0]


async def get_account_age(username, oauth_token):
    user_data = await get_user_data(username, oauth_token)
    created_at = user_data.get("created_at")
    created_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    return created_datetime.strftime("%B %d, %Y at %I:%M:%S %p")


async def get_oauth_token(client_id, client_secret):
    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as resp:
            data = await resp.json()
            return data.get("access_token")


class MessageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = get_session()

    @commands.command(name="messagecount", aliases=["messagecounts"])
    @authorized_users
    async def message_count(self, ctx, username=None):
        update_user_stats()
        if username is None:
            username = ctx.author.name
        try:
            user = self.session.query(TwitchUsers).filter_by(username=username).first()

            message_count_ = None  # Initialize to None
            try:
                message_count_ = self.session.query(func.count(TwitchMessagesLegacy.id)).filter_by(username=username).scalar()
            except Exception as e:
                print(e)
            
            if user:
                message_count = (
                    self.session.query(TwitchMessages)
                    .filter_by(username=username)
                    .count()
                )
                message_count_total = message_count + message_count_ if message_count_ is not None else message_count  # Add message_count_ if it is not None
                await asyncio.sleep(2)
                await ctx.send(
                    f"/me {username} has sent {message_count_total} messages in this channel."
                )
            else:
                await asyncio.sleep(2)
                await ctx.send(
                    f"/me {username} has not sent any messages in this channel."
                )
        except Exception as e:
            await ctx.send(
                f"/me An error occurred ping me and tell me to check console."
            )
            print(e)


    @commands.command(name="accountage")
    @authorized_users
    async def accountage(self, ctx, username=None):
        if username is None:
            username = ctx.author.name
        oauth_token = await get_oauth_token(
            TwitchConfig.CLIENT_ID, TwitchConfig.CLIENT_SECRET
        )
        account_age = await get_account_age(username, oauth_token)
        asyncio.sleep(3)
        await ctx.send(f"{username} was created at {account_age} ")


# Export the cog to be loaded in the main file
def prepare(bot):
    bot.add_cog(MessageCommands(bot))
