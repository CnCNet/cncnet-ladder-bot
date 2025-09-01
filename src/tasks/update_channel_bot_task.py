import discord
from discord import DiscordServerError
from src.commands.GetActiveMatches import fetch_active_qms
from src.constants.Constants import BURG_ID, CNCNET_DISCORD_ID, DISCORDS, YR_DISCORD_ID
from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.util.MyLogger import MyLogger
from src.util.Utils import send_message_to_log_channel, get_exception_msg, is_error

async def handle_api_error(bot, error_json, error_type, error_count, debug, stats_json=None):
    if error_type == "stats":
        api_name = "/stats/all"
    else:
        api_name = "/active_matches/all"
    server_message = f"Error fetching {error_type} for '{api_name}'.\n{get_exception_msg(error_json)}"
    await send_message_to_log_channel(bot=bot, msg=f"{server_message}")
    error_count += 1
    logger.debug(f"error_count={error_count}")
    if error_count == 10:
        await send_message_to_log_channel(bot=bot,
                                          msg=f"<@{BURG_ID}> {error_type} API has failed {error_count} times in a row!")
    # Update bot channel message with error
    if error_type == "stats":
        await fetch_active_qms(
            bot=bot,
            stats_json={},
            active_matches_json={},
            debug=debug
        )
    else:
        await fetch_active_qms(
            bot=bot,
            stats_json=stats_json,
            active_matches_json={},
            debug=debug
        )
    return error_count


error_count = 0
RECENT_ACTIVE_PLAYERS = []
logger = MyLogger("update_channel_bot_task")
count = 0
total_count = 0


async def execute(bot, ladders: list, cnc_api_client: CnCNetApiSvc, debug) -> dict:
    logger.debug("Starting update_channel_bot_task()...")
    global error_count

    try:
        if not ladders:
            logger.error("Error: No ladders available")
            msg = "Error: No ladders available"
            await send_message_to_log_channel(bot=bot, msg=msg)
            return {"error": "Failed to fetch stats", "status": "failed"}

        stats_json = cnc_api_client.fetch_stats("all")
        if is_error(stats_json):
            error_count = await handle_api_error(bot, stats_json, "stats", error_count, debug)
            return {"error": "Failed to fetch stats", "status": "failed"}
        else:
            error_count = 0

        active_matches_json = cnc_api_client.active_matches(ladder="all")
        if is_error(active_matches_json):
            error_count = await handle_api_error(bot, active_matches_json, "active matches", error_count, debug, stats_json=stats_json)
            return {"error": "Failed to fetch stats"}
        await fetch_active_qms(bot=bot, stats_json=stats_json, active_matches_json=active_matches_json, debug=debug)

        return {"error": None, "status": "success"}
    except (DiscordServerError, KeyError, Exception) as e:
        logger.exception("Exception occurred in update_channel_bot_task()")
        await send_message_to_log_channel(bot=bot, msg=str(e))
        return {"error": f"Unexpected error: {str(e)}", "status": "failed"}


