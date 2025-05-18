from apiclient.exceptions import APIRequestError
from discord.ext.commands import Bot

from src.util.Constants import *
from io import StringIO
import discord


def is_error(obj):
    return isinstance(obj, Exception) or isinstance(obj, APIRequestError)


# Send error message to channel on discord for bot logs
async def send_message_to_log_channel(bot: Bot, msg: str):
    channel = bot.get_channel(CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID)

    if len(msg) > 3000:
        buffer = StringIO(msg)
        f = discord.File(buffer, filename=f"error.txt")
        await channel.send(f"Error", file=f)
    else:
        await channel.send(msg[:3000])


def get_exception_msg(e):
    return f"Status code: '{e.status_code}', message: '{e.message}', Info: '{e.info}', Cause: '{e.__cause__}'"


async def get_latest_msg(channel):
    async for message in channel.history(limit=1):
        return message

    return None


async def get_channel_msgs(channel, limit=10):
    messages = []
    async for message in channel.history(limit=limit):
        messages.append(message)
    return list(reversed(messages))  # oldest to newest



