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
async def send_message_to_log_channel(bot: Bot, msg: str):
    import time
    try:
        channel = bot.get_channel(CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID)
        if channel is None:
            logger.error(f"Channel with ID {CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID} not found")
            return

        unix_ts = int(time.time())
        msg_with_time = f"<t:{unix_ts}:T> {msg}"

        if len(msg_with_time) > 2000:
            await send_file_to_channel(bot, f"{unix_ts}_logfile.txt", msg)
        else:
            await channel.send(msg_with_time[:2000])
    except Exception as e:
        logger.exception(f"Failed to send message to log channel: {e}")


async def send_file_to_channel(bot: Bot, filename: str, content: str):
    """
    Send a file to a Discord channel.

    Args:
        bot: The Discord bot instance
        filename: The name of the file to send
        content: The content of the file (as a string)
    """
    try:
        channel = bot.get_channel(CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID)
        if channel is None:
            logger.error(f"Channel with ID {CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID} not found")
            return

        buffer = StringIO(content)
        file = discord.File(buffer, filename=filename)
        await channel.send(file=file)
    except Exception as e:
        logger.exception(f"Failed to send file to channel {CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID}: {e}")


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



