import asyncio

from database import get_session
from models.TwitchScraping import TwitchChannels, TwitchUsers
from twitchio.ext import commands
from util.decorators import admin_users, authorized_users
from util.messagetools import update_user_stats, get_tweet


session = get_session()


class Apis(commands.Cog):
    def __init__(self, bot):
        self.session = get_session()
        self.bot = bot
        channels = self.session.query(TwitchChannels).all()
        CHANNELS = [channel.channel for channel in channels]

    @commands.command(name="searchtwitter")
    @admin_users
    async def searchtwitter(self, ctx: commands.Context, user: str):
        await ctx.send(get_tweet(user))


# Export the cog to be loaded in the main file
def prepare(bot):
    bot.add_cog(Apis(bot))
