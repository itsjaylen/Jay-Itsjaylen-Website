import asyncio

from database import get_session
from models.TwitchScraping import TwitchChannels, TwitchUsers
from twitchio.ext import commands
from util.decorators import admin_users, authorized_users
from util.messagetools import update_user_stats

session = get_session()


class Administrative(commands.Cog):
    def __init__(self, bot):
        self.session = get_session()
        self.bot = bot
        channels = self.session.query(TwitchChannels).all()
        CHANNELS = [channel.channel for channel in channels]

    @commands.command(name="adduser")
    @admin_users
    async def add_user(self, ctx: commands.Context, username: str):
        user = self.session.query(TwitchUsers).filter_by(username=username).first()
        if user is None:
            try:
                self.session.add(TwitchUsers(username=username.lower()))
                self.session.commit()
            except Exception as e:
                print(e)
            await asyncio.sleep(2)
            await ctx.send(f"{username} added to database")
        else:
            await asyncio.sleep(2)
            await ctx.send(f"{username} already exists in database")

    @commands.command(name="removeuser")
    @admin_users
    async def remove_user(self, ctx: commands.Context, username: str):
        user = self.session.query(TwitchUsers).filter_by(username=username).first()
        if user is not None:
            self.session.delete(user)
            self.session.commit()
            await ctx.send(f"{username} removed from database")
        else:
            await ctx.send(f"{username} does not exist in database")

    @commands.command(name="addchannel")
    @admin_users
    async def add_channel(self, ctx: commands.Context, channel: str):
        if not channel:
            await ctx.send("Please provide a valid channel name.")
            return

        channel = channel.lower()
        existing_channel = (
            self.session.query(TwitchChannels).filter_by(channel=channel).first()
        )

        if existing_channel:
            await ctx.send(f"{channel} already exists in database")
        else:
            new_channel = TwitchChannels(channel=channel)
            self.session.add(new_channel)
            self.session.commit()
            await asyncio.sleep(3)
            await self.join_channel(channel)
            await ctx.send(f"{channel} added to database")

    @commands.command(name="listusers")
    @authorized_users
    async def list_users(self, ctx: commands.Context):
        users = self.session.query(TwitchUsers).all()
        await asyncio.sleep(3)
        await ctx.send(", ".join([user.username for user in users]))

    @commands.command(name="listchannels")
    @admin_users
    async def list_channels(self, ctx: commands.Context):
        channels = self.session.query(TwitchChannels).all()
        await asyncio.sleep(3)
        await ctx.send(", ".join([channel.channel for channel in channels]))
        


# Export the cog to be loaded in the main file
def prepare(bot):
    bot.add_cog(Administrative(bot))
