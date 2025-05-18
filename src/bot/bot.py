# bot.py
import os

from apiclient import JsonResponseHandler
from discord import DiscordServerError
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from dotenv import load_dotenv

from src.commands.GetActiveMatches import fetch_active_qms
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.util.MyLogger import MyLogger
from src.util.Utils import *

load_dotenv()
TOKEN = os.getenv('DISCORD_CLIENT_SECRET')
intents = discord.Intents(messages=True, guilds=True, message_content=True, guild_messages=True, members=True)
bot = commands.Bot(command_prefix='!', intents=intents)
global cnc_api_client
global ladders
logger = MyLogger("bot")


@bot.event
async def on_ready():

    logger.log("bot online")

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

    await purge_bot_channel(1)  # Delete messages in bot-channel
    minute_task.start()
    update_qm_roles.start()


@tasks.loop(seconds=45)
async def minute_task():

    try:
        if not ladders:
            logger.error("Error: No ladders available")
            await send_message_to_log_channel("update_qm_bot_channel_name_task - Error: No ladders available")
            return

        stats_json = cnc_api_client.fetch_stats("all")
        if is_error(stats_json):
            server_message = f"Error fetching stats for '/stats/all'.\n{get_exception_msg(stats_json)}"
            await send_message_to_log_channel(bot=bot, msg=f"{server_message}")
            return

        await fetch_active_qms(bot=bot, stats_json=stats_json, cnc_api_client=cnc_api_client)
        await update_qm_bot_channel_name_task(stats_json)
    except DiscordServerError or Exception or KeyError as e:
        logger.error(f"Cause: '{e.__cause__}'")
        logger.error(str(e))
        await send_message_to_log_channel(bot, str(e))


@bot.command()
async def maps(ctx, arg=""):
    logger.debug("Fetching maps for ladder '{arg}'")

    if not ladders:
        await ctx.send("Error: No ladders available")
        return

    if not arg:
        ladders_string = ', '.join(ladders)
        await ctx.send(f"No ladder provided, select a valid ladder from `[{ladders_string}]`, like `!maps ra2`")
        return

    if arg.lower() not in ladders:
        ladders_string = ', '.join(ladders)
        await ctx.send(f"{arg.lower()} is not a valid ladder from `{ladders_string}`")
        return

    maps_json = cnc_api_client.fetch_maps(arg.lower())

    if is_error(maps_json):
        await ctx.send(f"Error fetching maps for ladder {arg.lower()}")
        await send_message_to_log_channel(bot=bot, msg=get_exception_msg(maps_json))

    maps_arr = []
    for item in maps_json:
        maps_arr.append("(" + str(item["map_tier"]) + ") " + item["description"])

    if not maps_arr:
        await ctx.send(f"Error: No maps found in ladder': {arg.upper()}'")
        return

    maps_string = "\n" + "\n".join(maps_arr)
    message = f"{len(maps_arr)} **{arg.upper()}** maps:" \
              f"\n```" \
              f"{maps_string}" \
              f"\n```"
    await ctx.send(message[:3000])


count = 10
total_count = 0
RECENT_ACTIVE_PLAYERS = []


async def update_qm_bot_channel_name_task(stats_json):

    logger.debug("beginning update_qm_bot_channel_name_task()")

    global count
    global total_count
    global RECENT_ACTIVE_PLAYERS

    total_count = total_count + 1

    if count == 10:
        count = 0
    else:
        count += 1
        return

    guilds = bot.guilds
    for server in guilds:
        ladder_abbrev_arr = None
        qm_bot_channel = None

        if server.id == CNCNET_DISCORD_ID:  # CnCNet discord
            ladder_abbrev_arr = ["d2k", "ra", "ra-2v2", "ra2", "yr", "blitz", "blitz-2v2", "ra2-2v2"]
            qm_bot_channel = bot.get_channel(DISCORDS[CNCNET_DISCORD_ID]['qm_bot_channel_id'])
        elif server.id == YR_DISCORD_ID:  # YR discord
            ladder_abbrev_arr = ["ra2", "yr", "blitz", "blitz-2v2", "ra2-2v2"]
            qm_bot_channel = bot.get_channel(DISCORDS[YR_DISCORD_ID]['qm_bot_channel_id'])
        elif server.id == BLITZ_DISCORD_ID:  # RA2CashGames discord
            ladder_abbrev_arr = ["blitz", "blitz-2v2", "ra2", "yr", "ra2-2v2"]
            qm_bot_channel = bot.get_channel(DISCORDS[BLITZ_DISCORD_ID]['qm_bot_channel_id'])

        if not ladder_abbrev_arr:
            logger.log(f"No ladders defined for server '{server.name}'")
            continue

        if not qm_bot_channel:
            logger.log(f"No qm-bot channel found in server '{server.name}'")
            continue

        num_players = 0
        for ladder_abbrev in ladder_abbrev_arr:
            stats = stats_json[ladder_abbrev]
            if not stats:
                logger.error(f"Error: No stats available for ladder {ladder_abbrev}")
                await send_message_to_log_channel(bot=bot, msg=f"update_qm_bot_channel_name_task - Error: No stats available for ladder {ladder_abbrev}")
                continue

            queued_players = stats['queuedPlayers']
            active_matches_players = stats['activeMatches']

            if ladder_abbrev in "2v2" or ladder_abbrev in "cl":
                active_matches_players = active_matches_players * 4  # 4 players in a 2v2
            else:
                active_matches_players = active_matches_players * 2  # 2 players in a 1v1

            num_players = num_players + queued_players + active_matches_players

        RECENT_ACTIVE_PLAYERS.append(num_players)

        if len(RECENT_ACTIVE_PLAYERS) >= 10:
            RECENT_ACTIVE_PLAYERS.pop(0)

        # from the last 10 mins, grab the most players in queue
        avg_val = (sum(RECENT_ACTIVE_PLAYERS) // len(RECENT_ACTIVE_PLAYERS)) + 1

        logger.debug(f"count={count}, arr={str(RECENT_ACTIVE_PLAYERS)}, num_players={num_players}, avg={str(avg_val)}")
        new_channel_name = "ladder-bot-" + str(avg_val)

        # update channel name every 10 mins
        try:
            await qm_bot_channel.edit(name=new_channel_name)
        except DiscordServerError or discord.errors.HTTPException as e:
            logger.error("failed to update channel name")
            await send_message_to_log_channel(bot=bot, msg=str(e))


@bot.event
async def on_rate_limit(rate_limit_info):
    logger.warning("WARNING - We are being rate limited")
    await send_message_to_log_channel(bot=bot, msg=rate_limit_info)


@bot.command()
async def purge_bot_channel_command(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        logger.error(f"{ctx.message.author} is not admin, exiting command.")
        return
    await purge_bot_channel(0)


async def purge_bot_channel(keep_messages: int):  # keep up to 'keep_messages' messages
    guilds = bot.guilds

    for server in guilds:
        for channel in server.channels:
            if QM_BOT_CHANNEL_NAME in channel.name:
                try:
                    message_count = 0
                    async for _ in channel.history(limit=2):
                        message_count += 1
                        if message_count > keep_messages:
                            deleted = await channel.purge()
                            logger.debug(f"Deleted {len(deleted)} message(s) from: server '{server.name}', channel: '{channel.name}'")
                            continue
                except DiscordServerError or discord.errors.NotFound or Exception as e:
                    await send_message_to_log_channel(bot=bot, msg=f"Failed to delete message from server '{server.name}', {str(e)}")


def is_in_bot_channel(ctx):
    return ctx.channel.name.startswith(QM_BOT_CHANNEL_NAME) or ctx.message.author.guild_permissions.administrator


@tasks.loop(hours=8)
async def update_qm_roles():

    global total_count
    if total_count < 60:
        return

    if total_count > 60:
        total_count = 60

    logger.debug("Starting update_qm_roles")

    await purge_bot_channel(1)  # purge excess messages from bot channel periodically in case a message wasn't deleted

    await remove_qm_roles()  # remove discord members QM roles

    await assign_qm_role()  # assign discord members QM roles

    logger.debug("completed updating QM roles")


async def remove_qm_roles():
    logger.debug("Removing QM roles")
    guilds = bot.guilds

    for server in guilds:

        if server.id != YR_DISCORD_ID:  # YR discord
            continue

        for member in server.members:
            for role in member.roles:

                if 'champion' in role.name.lower():  # Don't remove QM Champion roles
                    continue

                if 'ra2 qm' in role.name.lower():
                    await member.remove_roles(role)
                elif 'yr qm' in role.name.lower():
                    await member.remove_roles(role)
                elif 'ra2 qm' in role.name.lower():
                    await member.remove_roles(role)

    logger.debug("Finished removing QM roles")


async def assign_qm_role():
    logger.debug("Assigning QM Roles")
    guilds = bot.guilds

    for server in guilds:

        if server.id != YR_DISCORD_ID:  # YR discord
            continue

        # Fetch QM player ranks
        rankings_json = cnc_api_client.fetch_rankings()
        if is_error(rankings_json):
            logger.log(f"No ranking results found, exiting assign_qm_role(). {get_exception_msg(rankings_json)}")
            return

        ladder_abbrev_arr = ["RA2", "YR"]
        for ladder in ladder_abbrev_arr:
            rank = 0
            text = ""
            for item in rankings_json[ladder]:
                rank = rank + 1

                discord_name = item["discord_name"]
                player_name = item["player_name"]

                if not discord_name:
                    message = f"No discord name found for player '{player_name}', rank {rank}"
                    text += message + "\n"
                    continue

                member = server.get_member_named(discord_name)  # find the discord user by the name provided

                if not member:
                    message = f"No user found with name '{discord_name}' for player '{player_name}', rank {rank}, in " \
                              f"server {server} "

                    text += message + "\n"
                    continue

                role_name = ""
                if ladder == "YR" and rank == 1:
                    role_name = "YR QM Rank 1"
                elif ladder == "RA2" and rank == 1:
                    role_name = "RA2 QM Rank 1"
                elif ladder == "YR" and rank <= 3:
                    role_name = "YR QM Top 3"
                elif ladder == "RA2" and rank <= 3:
                    role_name = "RA2 QM Top 3"
                elif ladder == "YR" and rank <= 5:
                    role_name = "YR QM Top 5"
                elif ladder == "RA2" and rank <= 5:
                    role_name = "RA2 QM Top 5"
                elif ladder == "YR" and rank <= 10:
                    role_name = "YR QM Top 10"
                elif ladder == "RA2" and rank <= 10:
                    role_name = "RA2 QM Top 10"
                elif ladder == "YR" and rank <= 25:
                    role_name = "YR QM Top 25"
                elif ladder == "RA2" and rank <= 25:
                    role_name = "RA2 QM Top 25"
                elif ladder == "YR" and rank <= 50:
                    role_name = "YR QM Top 50"
                elif ladder == "RA2" and rank <= 50:
                    role_name = "RA2 QM Top 50"

                if not role_name:
                    message = f"No valid role found for ladder '{ladder}' rank {rank}"

                    text += message + "\n"
                    continue

                role = get(server.roles, name=role_name)
                if not role:
                    message = f"No valid role found for role_name '{role_name}'"

                    text += message + "\n"
                    continue

                message = f"Assigning role '{role}' to user '{member}', (player '{player_name}', rank: {rank})"
                text += message + "\n"

                await member.add_roles(role)  # Add the Discord QM role
    logger.debug("Completed assigning QM Roles")


bot.run(TOKEN)
