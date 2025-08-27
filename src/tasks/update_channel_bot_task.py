import discord
from discord import DiscordServerError

from src.commands.GetActiveMatches import fetch_active_qms
from src.constants.Constants import BURG_ID, CNCNET_DISCORD_ID, DISCORDS, YR_DISCORD_ID
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.util.MyLogger import MyLogger
from src.util.Utils import send_message_to_log_channel, get_exception_msg, is_error

error_count = 0
RECENT_ACTIVE_PLAYERS = []
logger = MyLogger("update_channel_bot_task")
count = 0
total_count = 0


async def execute(bot, ladders: list, cnc_api_client: CnCNetApiSvc, debug):
    logger.debug("Starting update_channel_bot_task()...")
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
            if error_count == 10:
                await send_message_to_log_channel(bot=bot,
                                                  msg=f"<@{BURG_ID}> stats API has failed {error_count} times in a row!")
            # Update bot channel message with error
            await fetch_active_qms(
                bot=bot,
                stats_json={},
                active_matches_json={},
                debug=debug
            )
            return
        else:
            error_count = 0

        active_matches_json = cnc_api_client.active_matches(ladder="all")
        await fetch_active_qms(bot=bot, stats_json=stats_json, active_matches_json=active_matches_json, debug=debug)

    except (DiscordServerError, KeyError, Exception) as e:
        logger.exception("Exception occurred in update_channel_bot_task()")
        await send_message_to_log_channel(bot=bot, msg=str(e))


