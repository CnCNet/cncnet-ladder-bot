# bot.py
import os
from http.client import HTTPException

import discord
from apiclient import JsonResponseHandler
from apiclient.exceptions import APIRequestError
from discord import Forbidden, DiscordServerError
from discord.ext import tasks
from discord.utils import get
from dotenv import load_dotenv
from discord.ext import commands
from CnCNetApiSvc import CnCNetApiSvc

from MyLogger import MyLogger


load_dotenv()
TOKEN = os.getenv('DISCORD_CLIENT_SECRET')
intents = discord.Intents(messages=True, guilds=True, message_content=True, guild_messages=True, members=True)
bot = commands.Bot(command_prefix='!', intents=intents)
global cnc_api_client
global ladders
global logger

QM_BOT_CHANNEL_NAME = "ladder-bot"

BURG_ID = 123726717067067393

# Discord server IDs
BLITZ_DISCORD_ID = 818265922615377971
YR_DISCORD_ID = 252268956033875970  # Yuri's Revenge - Server ID
GIBI_DISCORD_ID = 1007684612291579904  # Gibi server ID (polye's discord)

CNCNET_LADDER_DISCORD_BOT_LOGS_ID = 1240364999931854999

# Discord Channel IDs
YR_DISCORD_QM_BOT_ID = 1039026321826787338  # Yuri's Revenge.ladder-bot
CNCNET_DISCORD_QM_BOT_ID = 1039608594057924609  # CnCNet.qm-bot
GIBI_BOT_CHANNEL_ID = 1224207197173715064  # GIBI ladder-bot channel id
BLITZ_DISCORD_QM_BOT_ID = 1040396984164548729  # RA2 World Series.qm-bot


@bot.event
async def on_ready():

    global logger
    logger = MyLogger("bot.txt")
    logger.log("bot online")

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

    await purge_bot_channel()  # Delete messages in bot-channel
    minute_task.start()
    update_qm_roles.start()


@tasks.loop(minutes=1)
async def minute_task():

    stats_json = cnc_api_client.fetch_stats("all")
    if is_error(stats_json):
        server_message = f"Error fetching stats for '/stats/all'. <@{BURG_ID}>\n{get_exception_msg(stats_json)}"
        await send_message_to_log_channel(f"{server_message}")
        return

    await fetch_active_qms(stats_json)
    await update_qm_bot_channel_name_task(stats_json)


@bot.command()
async def maps(ctx, arg=""):
    logger.log("Fetching maps for ladder '{arg}'")

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
        await send_message_to_log_channel(get_exception_msg(maps_json))

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
    await ctx.send(message)


count = 10
RECENT_ACTIVE_PLAYERS = []


async def update_qm_bot_channel_name_task(stats_json):

    logger.log("beginning update_qm_bot_channel_name_task()")

    global count
    global RECENT_ACTIVE_PLAYERS

    if count == 10:
        count = 0
    else:
        count += 1
        return

    if not ladders:
        logger.error("Error: No ladders available")
        await send_message_to_log_channel("update_qm_bot_channel_name_task - Error: No ladders available")
        return

    guilds = bot.guilds
    for server in guilds:
        ladder_abbrev_arr = None
        qm_bot_channel = None

        if server.id == 188156159620939776:  # CnCNet discord
            ladder_abbrev_arr = ["ra", "ra2", "yr", "blitz", "blitz-2v2", "ra2-cl"]
            qm_bot_channel = bot.get_channel(CNCNET_DISCORD_QM_BOT_ID)
        elif server.id == YR_DISCORD_ID:  # YR discord
            ladder_abbrev_arr = ["ra2", "yr", "blitz", "blitz-2v2", "ra2-cl"]
            qm_bot_channel = bot.get_channel(YR_DISCORD_QM_BOT_ID)
        elif server.id == BLITZ_DISCORD_ID:  # RA2CashGames discord
            ladder_abbrev_arr = ["blitz", "blitz-2v2", "ra2", "yr", "ra2-cl"]
            qm_bot_channel = bot.get_channel(BLITZ_DISCORD_QM_BOT_ID)
        elif server.id == GIBI_DISCORD_ID:  # GIBI discord
            ladder_abbrev_arr = ["blitz", "blitz-2v2", "ra2", "yr", "ra2-cl"]
            qm_bot_channel = bot.get_channel(GIBI_BOT_CHANNEL_ID)

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
                await send_message_to_log_channel(f"update_qm_bot_channel_name_task - Error: No stats available for ladder {ladder_abbrev}")
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
        max_val = max(RECENT_ACTIVE_PLAYERS)

        logger.log(f"count={count}, num_players={num_players}")
        new_channel_name = "ladder-bot-" + str(max_val)

        # update channel name every 10 mins
        await qm_bot_channel.edit(name=new_channel_name)


# Send error message to channel on discord for bot logs
async def send_message_to_log_channel(msg):
    channel = bot.get_channel(CNCNET_LADDER_DISCORD_BOT_LOGS_ID)
    await channel.send(msg)


def clans_in_queue_msg(clans_in_queue):
    msg = ""

    if clans_in_queue:
        clan_count = 1
        msg += " "

        for clan_id, num_clans in clans_in_queue.items():
            msg += "Clan" + str(clan_count) + " (" + str(num_clans) + " players)"
            clan_count += 1

            if clan_count < len(clans_in_queue) + 1:
                msg += ", "
            else:
                msg += "."

    return msg


def is_error(obj):
    return isinstance(obj, Exception) or isinstance(obj, APIRequestError)


def get_exception_msg(e):
    return f"Status code: '{e.status_code}', message: '{e.message}', Info: '{e.info}', Cause: '{e.__cause__}'"


async def fetch_active_qms(stats_json):
    if not ladders:
        logger.error("Error: No ladders available")
        return

    current_matches_json = cnc_api_client.fetch_current_matches("all")

    if is_error(current_matches_json):
        fail_msg = f"Error fetching current_matches'. <@{BURG_ID}>\n{get_exception_msg(current_matches_json)}"
        await send_message_to_log_channel(f"{fail_msg}")
        return


    guilds = bot.guilds
    for server in guilds:

        ladder_abbrev_arr = []
        qm_bot_channel = None
        if server.id == 188156159620939776:  # CnCNet discord
            ladder_abbrev_arr = ["ra", "ra2", "ra2-cl", "yr", "blitz", "blitz-2v2"]
            qm_bot_channel = bot.get_channel(CNCNET_DISCORD_QM_BOT_ID)
        elif server.id == YR_DISCORD_ID:  # YR discord
            ladder_abbrev_arr = ["ra2-cl", "ra2", "yr", "blitz", "blitz-2v2"]
            qm_bot_channel = bot.get_channel(YR_DISCORD_QM_BOT_ID)
        elif server.id == BLITZ_DISCORD_ID:  # RA2CashGames discord
            ladder_abbrev_arr = ["blitz", "ra2-cl", "ra2", "yr", "blitz-2v2"]
            qm_bot_channel = bot.get_channel(BLITZ_DISCORD_QM_BOT_ID)
        elif server.id == GIBI_DISCORD_ID:  # GIBI discord
            ladder_abbrev_arr = ["blitz", "ra2", "yr", "ra2-cl", "blitz-2v2"]
            qm_bot_channel = bot.get_channel(GIBI_BOT_CHANNEL_ID)

        if not qm_bot_channel:
            continue

        server_message = ""
        # Loop through each ladder and get the results
        # Display active games in all ladders
        for ladder_abbrev in ladder_abbrev_arr:

            title = ladder_abbrev.upper()
            if ladder_abbrev == 'ra2-cl':
                title = 'Red Alert 2 Clan'

            qms_arr = []
            if ladder_abbrev in current_matches_json:
                for game in current_matches_json[ladder_abbrev]:
                    qms_arr.append(game.strip())

            # Get players in queue
            if ladder_abbrev not in stats_json:
                send_msg = f"Ladder not found in stats, {ladder_abbrev}, {stats_json[ladder_abbrev]}. <@{BURG_ID}>"
                await send_message_to_log_channel(f"{send_msg}")
                server_message = f"Failed fetching ladder stats for {ladder_abbrev}"
                continue
            else:
                stats = stats_json[ladder_abbrev]
                in_queue = stats['queuedPlayers']

                total_in_qm = in_queue + (len(qms_arr) * 2)
                if '-cl' in ladder_abbrev:
                    clans_in_queue = stats['clans']
                    total_in_qm = in_queue + (len(qms_arr) * 4)
                    current_message = str(total_in_qm) + " in **" + title \
                                      + "** Ladder:\n- " \
                                      + str(in_queue) \
                                      + " clan(s) in queue." + clans_in_queue_msg(clans_in_queue)
                else:
                    if '2v2' in ladder_abbrev:
                        total_in_qm = in_queue + (len(qms_arr) * 4)
                    current_message = str(total_in_qm) + " in **" + title \
                                      + "** Ladder:\n- " + str(in_queue) + " in queue"

                if qms_arr:
                    current_message += "\n- " + str(len(qms_arr)) + " active matches:\n```\n- " \
                                       + '\n- '.join(qms_arr) + "\n```\n"
                else:
                    current_message += "\n- 0 active matches.\n\n"

                server_message += current_message

        if server_message:  # Send one message per server
            try:
                await qm_bot_channel.send(server_message, delete_after=56)
            except HTTPException as he:
                msg = f"Failed to send message '{server_message}' to '{server}'\nexception: '{he}'"
                logger.error(msg)
                await send_message_to_log_channel(msg)
                return
            except Forbidden as f:
                msg = f"Failed to send message '{server_message}' \nforbidden error:  to '{server}' exception: '{f}'"
                logger.error(msg)
                await send_message_to_log_channel(msg)
                return
            except DiscordServerError as de:
                msg = f"Failed to send message '{server_message}'\nDiscordServerError: to '{server}' exception: '{de}'"
                logger.error(msg)
                await send_message_to_log_channel(msg)
                return
    logger.log("completed fetching active matches")


@bot.command()
async def purge_bot_channel_command(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        logger.error(f"{ctx.message.author} is not admin, exiting command.")
        return
    await purge_bot_channel()


async def purge_bot_channel():
    guilds = bot.guilds

    for server in guilds:
        for channel in server.channels:
            if QM_BOT_CHANNEL_NAME in channel.name:
                deleted = await channel.purge()
                logger.log(f"Deleted {len(deleted)} message(s) from: server '{server.name}', channel: '{channel.name}'")


def is_in_bot_channel(ctx):
    return ctx.channel.name.startswith(QM_BOT_CHANNEL_NAME) or ctx.message.author.guild_permissions.administrator


@tasks.loop(hours=8)
async def update_qm_roles():

    logger.log("Starting update_qm_roles")

    await purge_bot_channel()  # purge bot channel periodically in case a message wasn't deleted

    await remove_qm_roles()  # remove discord members QM roles

    await assign_qm_role()  # assign discord members QM roles

    await send_message_to_log_channel("completed updating QM roles")


async def remove_qm_roles():
    logger.log("Removing QM roles")
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

    logger.log("Finished removing QM roles")


async def assign_qm_role():
    logger.log("Assigning QM Roles")
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
    logger.log("Completed assigning QM Roles")


bot.run(TOKEN)
