import asyncio
import datetime
import psutil
import platform
import requests
from twitchio.ext import commands
from app.api.tools.apitool import update_user_stats
from app.models.TwitchScrapper import TwitchChannels, TwitchMessages, TwitchUsers
from app.extensions import db
from fuzzywuzzy import fuzz

import functools

def authorized_users(command_function):
    @functools.wraps(command_function)
    async def wrapper(ctx, *args, **kwargs):
        auth_users = get_auth_users()
        if ctx.author.name in auth_users:
            # The user is authorized to use the command, so execute the command function
            return await command_function(ctx, *args, **kwargs)
        else:
            # The user is not authorized, so send an error message
            pass
    return wrapper

def get_auth_users():
    return [user.username for user in TwitchUsers.query.all()]


def retry(max_retries=3, wait_time=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    retries += 1
                    await asyncio.sleep(wait_time)
                    continue
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator


@commands.command(name="adduser")
@authorized_users
@retry(max_retries=3, wait_time=1)
async def add_user(ctx: commands.Context, username: str):
    user = TwitchUsers.query.filter_by(username=username).first()
    if user is None:
        db.session.add(TwitchUsers(username=username.lower()))
        db.session.commit()
        await asyncio.sleep(2)
        await ctx.send(f"{username} added to database")
    else:
        await asyncio.sleep(2)
        await ctx.send(f"{username} already exists in database")


@commands.command(name="removeuser")
@commands.cooldown(1, 60)
@retry(max_retries=3, wait_time=1)
async def remove_user(ctx: commands.Context, username: str):
    user = TwitchUsers.query.filter_by(username=username).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        await ctx.send(f"{username} removed from database")
    else:
        await ctx.send(f"{username} does not exist in database")


@commands.command(name="addchannel")
@commands.cooldown(1, 60)
@retry(max_retries=3, wait_time=1)
async def add_channel(ctx: commands.Context, channel: str):
    channel = TwitchChannels.query.filter_by(channel=channel).first()
    if channel is None:
        db.session.add(TwitchChannels(channel=channel))
        db.session.commit()
        await asyncio.sleep(2)
        await ctx.send(f"{channel} added to database")
    else:
        await asyncio.sleep(2)
        await ctx.send(f"{channel} already exists in database")

@commands.command(name="listusers")
@authorized_users
@retry(max_retries=3, wait_time=1)
async def list_users(ctx: commands.Context):
    users = TwitchUsers.query.all()
    await asyncio.sleep(3)
    await ctx.send(", ".join([user.username for user in users]))


@commands.command(name="listchannels")
@authorized_users
@retry(max_retries=3, wait_time=1)
async def list_channels(ctx: commands.Context):
    channels = TwitchChannels.query.all()
    await ctx.send(", ".join([channel.channel for channel in channels]))


@commands.command(name="forceupdate")
@authorized_users
#@retry(max_retries=3, wait_time=1)
async def force_update(ctx: commands.Context):
    await ctx.send("/me Force updating user stats")
    update_user_stats()
    await asyncio.sleep(3)
    await ctx.send("/me Channels updated")
        
    


@commands.command(name="messagecount")
@authorized_users
@retry(max_retries=3, wait_time=1)
async def message_count(ctx, username=None):
    if username is None:
        username = ctx.author.name
    try:
        user = TwitchUsers.query.filter_by(username=username).first()
        if user:
            await asyncio.sleep(2)
            await ctx.send(
                f"/me {username} has sent {user.message_count} messages in this channel."
            )
        else:
            await asyncio.sleep(2)
            await ctx.send(f"/me {username} has not sent any messages in this channel.")
    except Exception as e:
        await ctx.send(f"/me An error occurred ping me and tell me to check console.")




@commands.command(name="findmessage")
@commands.cooldown(1, 30)
@authorized_users
@retry(max_retries=3, wait_time=1)
async def find_message(ctx, search_string, username=None, max_messages=5):
    threshold = 70  # Adjust this value as needed for matching accuracy
    if max_messages > 3:
        max_messages = 3

    messages = TwitchMessages.query.all()

    # Search for matching messages using fuzzywuzzy and username filter
    matching_messages = [
        msg
        for msg in messages
        if fuzz.partial_ratio(search_string, msg.message) >= threshold and (not username or msg.username.lower() == username.lower())
    ]

    if matching_messages:
        # Send up to max_messages matching messages to the chat channel
        for i, msg in enumerate(matching_messages[:max_messages]):
            message = f"[{msg.timestamp}] {msg.channel} - {msg.username}: {msg.message}"
            await ctx.send(message)
            await asyncio.sleep(3)
            if i == max_messages - 1:
                break
    else:
        await ctx.send(f"/me No messages found from user '{username}' that match '{search_string}'." if username else f"No messages found that match '{search_string}'.")


@commands.command(name="opt-in")
@commands.cooldown(1, 30)
@retry(max_retries=3, wait_time=3)
async def optin(ctx, username=None):
    if username is None:
        username = ctx.author.name
        user = TwitchUsers.query.filter_by(username=username).first()
    if user is None:
        db.session.add(TwitchUsers(username=username.lower()))
        db.session.commit()
        await asyncio.sleep(2)
        await ctx.send(f"{username} added to database.")
    else:
        await asyncio.sleep(2)
        await ctx.send(f"{username} already exists in database.")




@commands.command(name="sysinfo")
@commands.cooldown(1, 60)
async def sysinfo(ctx: commands.Context):
    # Get CPU information
        cpu_name = platform.processor()
        cpu_cores = psutil.cpu_count(logical=True)
        
        # Get memory information
        mem_usage = psutil.virtual_memory()
        mem_total = round(mem_usage.total / (1024**3), 2)
        mem_used = round(mem_usage.used / (1024**3), 2)
        mem_percent = mem_usage.percent
        
        # Get disk usage information
        disk_usage = psutil.disk_usage('/')
        disk_total = round(disk_usage.total / (1024**3), 2)
        disk_used = round(disk_usage.used / (1024**3), 2)
        disk_free = round(disk_usage.free / (1024**3), 2)
        disk_percent = disk_usage.percent
        
        # Get OS information
        os_name = platform.system()
        
        # Create chat message with system information
        sysinfo_msg = f"CPU: {cpu_name}, Cores: {cpu_cores}. RAM: {mem_used} GB / {mem_total} GB ({mem_percent}%). Disk: {disk_used} GB / {disk_total} GB ({disk_percent}%). OS: {os_name}"
        sysinfo_msg = sysinfo_msg[:500]
        
        await asyncio.sleep(2)
        # Send message in Twitch chat
        await ctx.send(sysinfo_msg)
        
        
@commands.command(name='totalmessages')
@commands.cooldown(1, 10)
@authorized_users
@retry(max_retries=3, wait_time=3)
async def total_messages(ctx):
    total_messages = db.session.query(db.func.sum(TwitchUsers.message_count)).scalar()
    if total_messages:
        await asyncio.sleep(3)
        await ctx.send(f"/me {total_messages} messages have been sent by all users.")
    else:
        asyncio.sleep(3)
        await ctx.send(f"/me No messages have been sent.")
        
