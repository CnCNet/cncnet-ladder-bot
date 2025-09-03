# bot.py
import os

from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

from src.commands.GetMaps import get_maps
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.tasks import update_channel_bot_task, eight_hour_task
from src.tasks.update_qm_bot_channel_name_task import update_qm_bot_channel_name_task
from src.util.MyLogger import MyLogger
from src.util.Utils import *

load_dotenv()
TOKEN: str = str(os.getenv('DISCORD_CLIENT_SECRET'))
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
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

    await purge_bot_channel(0)

    global cnc_api_client
    cnc_api_client = CnCNetApiSvc()

    global ladders
    ladders = []
    ladders_json = cnc_api_client.fetch_ladders()
    for item in ladders_json:
        if item["private"] == 0:
            ladders.append(item["abbreviation"])

    ladders_string = ", ".join(ladders)
    logger.log(f"Ladders found: ({ladders_string})")

    update_bot_channel.start()
    
    periodic_update_qm_bot_channel_name.start()


@tasks.loop(minutes=10)
async def periodic_update_qm_bot_channel_name():

    # Skip the first execution after bot comes online
    if not hasattr(periodic_update_qm_bot_channel_name, "_has_run"):
        periodic_update_qm_bot_channel_name._has_run = True
        return
    
    stats_json = cnc_api_client.fetch_stats("all")
    active_matches_json = cnc_api_client.active_matches(ladder="all")
    await update_qm_bot_channel_name_task(bot, stats_json, active_matches_json)


@tasks.loop(seconds=30)
async def update_bot_channel():
    response = await update_channel_bot_task.execute(bot=bot, ladders=ladders, cnc_api_client=cnc_api_client, debug=DEBUG)
    if response.get("error"):
        logger.error(f"Error in update_bot_channel: {response['error']}")
        update_bot_channel.change_interval(seconds=90)
    else:
        # Restore interval to 30 seconds if previously changed due to error
        if update_bot_channel.seconds != 30:
            update_bot_channel.change_interval(seconds=30)


@bot.command()
async def maps(ctx, arg=""):
    await get_maps(ctx=ctx, bot=bot, arg=arg, ladders=ladders, cnc_api_client=cnc_api_client)


@bot.event
async def on_rate_limit(rate_limit_info):
    logger.warning(f"WARNING - We are being rate limited: {rate_limit_info}")
    await send_message_to_log_channel(bot=bot, msg=rate_limit_info)


@bot.command()
async def purge_bot_channel_command(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        logger.error(f"{ctx.message.author} is not admin, exiting command.")
        return
    await purge_bot_channel(0)


async def purge_bot_channel(keep_messages_count: int):  # keep up to 'keep_messages' messages
    guilds = bot.guilds

    for server in guilds:
        for channel in server.channels:
            if QM_BOT_CHANNEL_NAME in channel.name:
                try:
                    message_count = 0
                    async for _ in channel.history(limit=2):
                        message_count += 1
                        if message_count > keep_messages_count:
                            deleted = await channel.purge()
                            logger.debug(f"Deleted {len(deleted)} message(s) from: server '{server.name}', channel: '{channel.name}'")
                            continue
                except (discord.DiscordServerError, discord.errors.HTTPException) as e:
                    await send_message_to_log_channel(bot=bot, msg=f"Failed to delete message from server '{server.name}', {str(e)}")


def is_in_bot_channel(ctx):
    return ctx.channel.name.startswith(QM_BOT_CHANNEL_NAME) or ctx.message.author.guild_permissions.administrator


@tasks.loop(hours=8)
async def update_qm_roles_loop():
    await eight_hour_task.execute(bot=bot, cnc_api_client=cnc_api_client)


bot.run(TOKEN)
