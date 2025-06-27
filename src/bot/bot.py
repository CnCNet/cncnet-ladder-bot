# bot.py
import os

from apiclient import JsonResponseHandler
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

from src.commands.GetMaps import get_maps
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.tasks import minute_task, eight_hour_task
from src.util.MyLogger import MyLogger
from src.util.Utils import *

load_dotenv()
TOKEN = os.getenv('DISCORD_CLIENT_SECRET')
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
intents = discord.Intents(messages=True, guilds=True, message_content=True, guild_messages=True, members=True)
bot = commands.Bot(command_prefix='!', intents=intents)
global cnc_api_client
global ladders
logger = MyLogger("bot")


@bot.event
async def on_ready():

    logger.log(f"bot online with DEBUG={DEBUG}")
    await send_message_to_log_channel(bot, "Ladder bot is online...")

    logger.log("Checking existing guilds...")
    for guild in bot.guilds:
        if guild.id != YR_DISCORD_ID and guild.id != CNCNET_DISCORD_ID and guild.id != BLITZ_DISCORD_ID and guild.id != DEV_DISCORD_ID:
            logger.log(f"Leaving unauthorized server on startup: {guild.name} (ID: {guild.id})")
            await guild.leave()
        else:
            logger.log(f"Remaining in authorized server: {guild.name} (ID: {guild.id})")
    logger.log("Finished checking guilds.")

    # guild = discord.utils.get(bot.guilds, id=1007684612291579904)
    # if guild:
    #     print(f'Leaving server: {guild.name} (ID: {guild.id})')
    #     await guild.leave()

    global cnc_api_client
    cnc_api_client = CnCNetApiSvc(
        response_handler=JsonResponseHandler
    )

    global ladders
    ladders = []
    ladders_json = cnc_api_client.fetch_ladders()
    for item in ladders_json:
        if item["private"] == 0:
            ladders.append(item["abbreviation"])

    ladders_string = ", ".join(ladders)
    logger.log(f"Ladders found: ({ladders_string})")

    minute_task_loop.start()

    if not DEBUG:
        update_qm_roles_loop.start()


@tasks.loop(seconds=45)
async def minute_task_loop():
    await minute_task.execute(bot=bot, ladders=ladders, cnc_api_client=cnc_api_client, debug=DEBUG)


@bot.command()
async def maps(ctx, arg=""):
    await get_maps(ctx=ctx, bot=bot, arg=arg, ladders=ladders, cnc_api_client=cnc_api_client)


@bot.event
async def on_rate_limit(rate_limit_info):
    logger.warning(f"WARNING - We are being rate limited: {rate_limit_info}")
    await send_message_to_log_channel(bot=bot, msg=rate_limit_info)


# @bot.command()
# async def purge_bot_channel_command(ctx):
#     if not ctx.message.author.guild_permissions.administrator:
#         logger.error(f"{ctx.message.author} is not admin, exiting command.")
#         return
#     await purge_bot_channel(0)


# async def purge_bot_channel(keep_messages: int):  # keep up to 'keep_messages' messages
#     guilds = bot.guilds
#
#     for server in guilds:
#         for channel in server.channels:
#             if QM_BOT_CHANNEL_NAME in channel.name:
#                 try:
#                     message_count = 0
#                     async for _ in channel.history(limit=2):
#                         message_count += 1
#                         if message_count > keep_messages:
#                             deleted = await channel.purge()
#                             logger.debug(f"Deleted {len(deleted)} message(s) from: server '{server.name}', channel: '{channel.name}'")
#                             continue
#                 except DiscordServerError or discord.errors.NotFound or Exception as e:
#                     await send_message_to_log_channel(bot=bot, msg=f"Failed to delete message from server '{server.name}', {str(e)}")


def is_in_bot_channel(ctx):
    return ctx.channel.name.startswith(QM_BOT_CHANNEL_NAME) or ctx.message.author.guild_permissions.administrator


@tasks.loop(hours=8)
async def update_qm_roles_loop():
    await eight_hour_task.execute(bot=bot, cnc_api_client=cnc_api_client)


bot.run(TOKEN)
