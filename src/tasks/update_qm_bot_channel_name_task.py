import asyncio
import discord
from src.constants.constants import CNCNET_DISCORD_ID, YR_DISCORD_ID, DISCORDS
from src.util.logger import MyLogger
from src.util.utils import send_message_to_log_channel

RECENT_ACTIVE_PLAYERS = []
logger = MyLogger("update_qm_bot_channel_name_task")
count = 0
total_count = 0

async def update_qm_bot_channel_name_task(bot, stats_json, active_matches):
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
        if server.id == CNCNET_DISCORD_ID:
            ladder_abbrev_arr = ["d2k", "ra", "ra-2v2", "ra2", "yr", "blitz", "blitz-2v2", "ra2-2v2"]
            qm_bot_channel = bot.get_channel(DISCORDS[CNCNET_DISCORD_ID]['qm_bot_channel_id'])
        elif server.id == YR_DISCORD_ID:
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
            stats = stats_json.get(ladder_abbrev)
            if not stats:
                logger.error(f"Error: No stats available for ladder {ladder_abbrev}")
                await send_message_to_log_channel(bot=bot,
                                                  msg=f"update_qm_bot_channel_name_task - Error: No stats available for ladder {ladder_abbrev}")
                continue
            queued_players = stats.get('queuedPlayers', 0)
            active_matches_players = len(active_matches.get(ladder_abbrev, []))
            if "2v2" in ladder_abbrev or "cl" in ladder_abbrev:
                active_matches_players = active_matches_players * 4
            else:
                active_matches_players = active_matches_players * 2
            num_players = num_players + queued_players + active_matches_players
        RECENT_ACTIVE_PLAYERS.append(num_players)
        if len(RECENT_ACTIVE_PLAYERS) >= 10:
            RECENT_ACTIVE_PLAYERS.pop(0)
        avg_val = (sum(RECENT_ACTIVE_PLAYERS) // len(RECENT_ACTIVE_PLAYERS)) + 1
        logger.debug(f"count={count}, arr={str(RECENT_ACTIVE_PLAYERS)}, num_players={num_players}, avg={str(avg_val)}")
        new_channel_name = "ladder-bot-" + str(avg_val)
        try:
            await qm_bot_channel.edit(name=new_channel_name)
        except (discord.DiscordServerError, discord.errors.HTTPException) as e:
            logger.error("failed to update channel name")
            await send_message_to_log_channel(bot=bot, msg=str(e))

async def periodic_update_qm_bot_channel_name(bot, cnc_api_client):
    while True:
        stats_json = cnc_api_client.fetch_stats("all")
        active_matches_json = cnc_api_client.active_matches(ladder="all")
        await update_qm_bot_channel_name_task(bot, stats_json, active_matches_json)
