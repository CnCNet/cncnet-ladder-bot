import os

import discord
from discord import DiscordServerError

from src.util.MyLogger import MyLogger
from src.commands.GetActiveMatches import fetch_active_qms
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.constants.Constants import BURG_ID, CNCNET_DISCORD_ID, DISCORDS, YR_DISCORD_ID
from src.util.Utils import send_message_to_log_channel, get_exception_msg, is_error

error_count = 0
RECENT_ACTIVE_PLAYERS = []
logger = MyLogger("MinuteTask")
count = 0
total_count = 0


async def execute(bot, ladders: list, cnc_api_client: CnCNetApiSvc, debug):
    logger.debug("Starting minute_task()...")
    global error_count

    try:
        if not ladders:
            logger.error("Error: No ladders available")
            msg = "Error: No ladders available"
            await send_message_to_log_channel(bot=bot, msg=msg)
            return

        stats_json = cnc_api_client.fetch_stats("all")
        if is_error(stats_json):
            server_message = f"Error fetching stats for '/stats/all'.\n{get_exception_msg(stats_json)}"
            await send_message_to_log_channel(bot=bot, msg=f"{server_message}")
            error_count += 1
            logger.debug(f"error_count={error_count}")
            if error_count >= 10:
                await send_message_to_log_channel(bot=bot,
                                                  msg=f"<@{BURG_ID}> stats API has failed {error_count} times in a row!")
            return
        else:
            error_count = 0

        await fetch_active_qms(bot=bot, stats_json=stats_json, cnc_api_client=cnc_api_client, debug=debug)

        if not debug:
            await update_qm_bot_channel_name_task(bot=bot, stats_json=stats_json)
    except (DiscordServerError, KeyError, Exception) as e:
        logger.exception("Exception occurred in minute_task()")
        await send_message_to_log_channel(bot=bot, msg=str(e))


async def update_qm_bot_channel_name_task(bot, stats_json):
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
                await send_message_to_log_channel(bot=bot,
                                                  msg=f"update_qm_bot_channel_name_task - Error: No stats available for ladder {ladder_abbrev}")
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
        except (DiscordServerError, discord.errors.HTTPException) as e:
            logger.error("failed to update channel name")
            await send_message_to_log_channel(bot=bot, msg=str(e))
