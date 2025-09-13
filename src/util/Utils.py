from discord.ext.commands import Bot
from requests import RequestException

from src.constants.Constants import *
from io import StringIO
import discord

from src.util.MyLogger import MyLogger

logger = MyLogger("utils")


def is_error(obj):
    return isinstance(obj, Exception) or isinstance(obj, RequestException)


# Send error message to channel on discord for bot logs
async def send_message_to_log_channel(bot: Bot, msg: str, as_file: bool = False):
    import time
    try:
        channel = bot.get_channel(CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID)

        unix_ts = int(time.time())
        msg_with_time = f"<t:{unix_ts}:T> {msg}"

        if len(msg_with_time) > 2000 or as_file:
            buffer = StringIO(msg_with_time)
            filename = f"{unix_ts}_logfile.txt"
            f = discord.File(buffer, filename=filename)
            await channel.send(content=f"<t:{unix_ts}:T>", file=f)
        else:
            await channel.send(msg_with_time[:2000])
    except Exception as e:
        logger.exception(f"Failed to send message to log channel: {e}")


def get_exception_msg(e):
    return (
        f"Type: {type(e).__name__}, "
        f"Status code: '{getattr(e, 'status_code', None)}', "
        f"Message: '{getattr(e, 'message', str(e))}', "
        f"Info: '{getattr(e, 'info', None)}', "
        f"Cause: '{getattr(e, '__cause__', None)}', "
        f"Args: {getattr(e, 'args', None)}"
    )


async def get_latest_msg(channel):
    async for message in channel.history(limit=1):
        return message

    return None


async def get_channel_msgs(channel, limit=10):
    messages = []
    async for message in channel.history(limit=limit):
        messages.append(message)
    return list(reversed(messages))  # oldest to newest



