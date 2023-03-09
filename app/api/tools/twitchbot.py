import asyncio
import datetime

from app.api.tools.apitool import (
    hash_sha256,
)
from app.api.tools.twitch.commands import add_user, list_channels, list_users, remove_user, force_update, message_count, find_message, sysinfo, total_messages, optin
from app.extensions import db
from app.models.TwitchScrapper import TwitchChannels, TwitchMessages, TwitchUsers
from config import TwitchConfig


from twitchio.ext import commands


class Bot(commands.Bot):
    def __init__(self, app, db):
        CHANNELS = [channel.channel for channel in TwitchChannels.query.all()]
        super().__init__(
            token=TwitchConfig.TOKEN,
            prefix=TwitchConfig.PREFIX,
            initial_channels=CHANNELS,
        )
        with app.app_context():
            self.db = db
            self.add_command(add_user)
            self.add_command(list_channels)
            self.add_command(list_users)
            #self.add_command(remove_user)
            self.add_command(force_update)
            self.add_command(message_count)
            self.add_command(find_message)
            #self.add_command(sysinfo)
            self.add_command(total_messages)
            self.add_command(optin)
        
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
                TARGET_USERS = [user.username for user in TwitchUsers.query.all()]
                if message.author.name.lower() in TARGET_USERS:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    hashed_message = hash_sha256(
                        f"{timestamp} {message.channel.name} | {message.author.name} SIGNED MESSAGE SHA256: {message.content}"
                    )
                    data = {
                        "timestamp": timestamp,
                        "channel": message.channel.name,
                        "username": message.author.name,
                        "message": message.content,
                        "hashed_message": hashed_message,
                    }

                    print(
                        f"{message.channel.name} | {message.author.name}: {message.content}"
                    )

                    try:
                        self.db.session.add(TwitchMessages(**data))
                        self.db.session.commit()
                    except ConnectionResetError as e:
                        print("Error: 1", e)
                        self.db.session.rollback()
                        
                    if message.author.name.lower() == "test":
                        pass

            else:
                print(f"{message.channel.name} | {self.nick}: {message.content}")
        except Exception as e:
            pass

        try:
            await self.handle_commands(message)
        except commands.CommandNotFound:
            pass
        except Exception as e:
            print(f"Error handling command: {e}")


    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello {ctx.author.name}!")
        
