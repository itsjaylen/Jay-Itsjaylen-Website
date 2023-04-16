import asyncio
import datetime
import importlib
import sys

from config import TwitchConfig
from database import get_session
from models.TwitchScraping import TwitchChannels, TwitchMessages, TwitchUsers
from twitchio.ext import commands
from util.decorators import admin_users

# create the tables in the database if they don't exist
# Base.metadata.create_all(engine)


class Bot(commands.Bot):
    def __init__(self):
        self.session = get_session()
        channels = self.session.query(TwitchChannels).all()
        CHANNELS = [channel.channel for channel in channels]

        super().__init__(
            token=TwitchConfig.TOKEN,
            prefix=TwitchConfig.PREFIX,
            initial_channels=CHANNELS,
        )

        # load initial modules
        self.load_module("commands.messagecommands")
        self.load_module("commands.administrative")
        self.load_module("commands.apis")
        

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    async def event_disconnect(self):
        print("Disconnected from Twitch IRC server. Reconnecting...")
        await self._ws.close()
        await self._ws.wait_closed()
        await self._connect()

    async def event_message(self, message):
        if message.echo:
            print(message.content)

        try:
            if message.author.name.lower() != self.nick.lower():
                TARGET_USERS = [
                    user.username for user in self.session.query(TwitchUsers).all()
                ]
                if message.author.name.lower() in TARGET_USERS:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    data = {
                        "timestamp": timestamp,
                        "channel": message.channel.name,
                        "username": message.author.name,
                        "message": message.content,
                    }

                    print(
                        f"{message.channel.name} | {message.author.name}: {message.content}"
                    )

                    try:
                        self.session.add(TwitchMessages(**data))
                        self.session.commit()

                    except ConnectionResetError as e:
                        print("Error: 1", e)
                        self.session.rollback()

                    if message.author.name.lower() == "test":
                        pass

            else:
                print(f"{message.channel.name} | {self.nick}: {message.content}")
        except Exception as e:
            pass

        try:
            await self.handle_commands(message)
        except Exception:
            pass

    @commands.command(name="reload")
    @admin_users
    async def reload(self, ctx, module):
        self.unload_module(module)
        self.load_module(module)
        await asyncio.sleep(3)
        await ctx.send(f"Reloaded {module}")


if __name__ == "__main__":
    bot = Bot()
    print("Starting bot...")
    bot.run()
