

import json
import time
from http.client import HTTPException
from typing import Dict, Any, List, Optional

from discord import Forbidden, DiscordServerError, Message
from discord.ext.commands import Bot
from src.constants.Constants import DEV_DISCORD_ID, DISCORDS
from src.util.Embed import create_embeds
from src.util.MyLogger import MyLogger
from src.util.Utils import send_message_to_log_channel, get_channel_msgs, is_error, get_exception_msg

logger = MyLogger("GetActiveMatches")  # Logger for this module


def players_in_queue(ladder_abbrev: str, stats_json: dict, num_active_matches: int) -> str:
    """
    Returns a formatted message about the number of players in queue and in matches for a given ladder.
    """
    title = ladder_abbrev.upper()
    if ladder_abbrev == 'ra2-cl':
        title = 'RA2 Clan'

    in_queue = stats_json.get('queuedPlayers', 0)
    total_in_qm = in_queue + (num_active_matches * (4 if '2v2' in ladder_abbrev else 2))

    if total_in_qm == 0:
        return f"- **0** in **{title}** Ladder"
    return f"- **{total_in_qm}** in **{title}** Ladder, **{in_queue}** waiting in queue"


last_summary_message_ids: Dict[int, int] = {}  # channel_id -> message_id

async def fetch_active_qms(
    bot: Bot,
    stats_json: dict,
    active_matches_json: dict,
    debug: bool
) -> None:
    """
    Updates Discord channel messages with current queue and match info for each ladder.
    Aggregates all ladder info into a single message and updates it in the target channel.
    """
    logger.debug(f"Fetching active qms with debug={debug}...")

    if is_error(active_matches_json):
        fail_msg = f"Error fetching active_matches.\n{get_exception_msg(active_matches_json)}"
        await send_message_to_log_channel(bot=bot, msg=fail_msg)
        return

    for server in bot.guilds:
        if (server.id == DEV_DISCORD_ID) != debug:
            continue

        server_info = DISCORDS.get(server.id)
        if server_info is None:
            logger.warning(f"Unexpected server ID: {server.id} (server name: {server.name}) ... skipping")
            continue

        ladder_abbrev_arr: List[str] = server_info["ladders"]
        qm_bot_channel = bot.get_channel(server_info["qm_bot_channel_id"])

        if not qm_bot_channel:
            logger.error(f"Channel not found for {server.name}: {server_info['qm_bot_channel_id']}")
            continue

        # Aggregate all ladder info into one message
        summary_lines: List[str] = []
        all_embeds: List = []
        for ladder_abbrev in ladder_abbrev_arr:
            if ladder_abbrev not in stats_json:
                summary_lines = ["Failed to retrieve ladder stats from the API."]
                break
            else:
                msg = players_in_queue(
                    ladder_abbrev=ladder_abbrev,
                    stats_json=stats_json[ladder_abbrev],
                    num_active_matches=len(active_matches_json.get(ladder_abbrev, []))
                )
                summary_lines.append(msg)
                all_embeds.extend(create_embeds(ladder_abbrev, active_matches_json.get(ladder_abbrev, [])))

        time_updated_msg = f"*Updated* <t:{int(time.time())}:R>"
        summary_text = "\n".join(summary_lines) + "\n" + time_updated_msg

        # Use cached message ID if available
        bot_message: Optional[Message] = None
        channel_id = qm_bot_channel.id
        message_id = last_summary_message_ids.get(channel_id)
        if message_id:
            try:
                bot_message = await qm_bot_channel.fetch_message(message_id)
            except Exception:
                bot_message = None  # Message may have been deleted

        try:
            if bot_message:
                await bot_message.edit(content=summary_text[:2000], embeds=all_embeds)
            else:
                sent_msg = await qm_bot_channel.send(content=summary_text[:2000], embeds=all_embeds)
                last_summary_message_ids[channel_id] = sent_msg.id
        except (HTTPException, Forbidden, DiscordServerError) as e:
            error_msg = (
                f"Failed to send/edit summary message in '{server.name}.{qm_bot_channel.name}'\n"
                f"**{type(e).__name__}:** {e}"
            )
            logger.error(error_msg)
            await send_message_to_log_channel(bot=bot, msg=error_msg)

    logger.debug("Completed fetching active matches.")

