import json
import time
from http.client import HTTPException

from discord import Forbidden, DiscordServerError

from src.util.Embed import *
from src.util.MyLogger import MyLogger
from src.util.Utils import *

logger = MyLogger("GetActiveMatches")


def players_in_queue(ladder_abbrev: str, stats_json: json, num_active_matches: int):
    title = ladder_abbrev.upper()
    if ladder_abbrev == 'ra2-cl':
        title = 'RA2 Clan'

    # Get players in queue

    in_queue = stats_json['queuedPlayers']

    total_in_qm = in_queue + (num_active_matches * 2)  # players in queue + players in a match

    if total_in_qm == 0:
        msg = f"- **0** in **{title}** Ladder"
    else:
        if '2v2' in ladder_abbrev:
            total_in_qm = in_queue + (num_active_matches * 4)
            msg = f"- **{str(total_in_qm)}** in **{title}** Ladder, **{str(in_queue)}** waiting in queue"
        else:
            msg = f"- **{str(total_in_qm)}** in **{title}** Ladder, **{str(in_queue)}** waiting in queue"
    return msg


async def fetch_active_qms(bot: Bot, stats_json: json, current_matches_json, debug: bool):
    logger.debug(f"Fetching active qms with debug={debug}...")

    if is_error(current_matches_json):
        fail_msg = f"Error fetching current_matches.\n{get_exception_msg(current_matches_json)}"
        await send_message_to_log_channel(bot=bot, msg=fail_msg)
        return

    for server in bot.guilds:
        if (server.id == DEV_DISCORD_ID) != debug:
            continue

        server_info = DISCORDS.get(server.id)
        if server_info is None:
            logger.error(f"Unexpected server ID: {server.id}")
            continue

        ladder_abbrev_arr = server_info["ladders"]
        qm_bot_channel = bot.get_channel(server_info["qm_bot_channel_id"])

        if not qm_bot_channel:
            raise ValueError(f"Channel not found for {server.name}: {server_info['qm_bot_channel_id']}")

        count = 0
        channel_messages = await get_channel_msgs(channel=qm_bot_channel, limit=10)

        for ladder_abbrev in ladder_abbrev_arr:
            if ladder_abbrev not in stats_json:
                await send_message_to_log_channel(bot=bot, msg=f"Ladder not found: {ladder_abbrev}")
                message_text = f"Failed fetching ladder stats for {ladder_abbrev}"
                embeds = []
            else:
                message_text = players_in_queue(
                    ladder_abbrev=ladder_abbrev,
                    stats_json=stats_json[ladder_abbrev],
                    num_active_matches=len(current_matches_json[ladder_abbrev])
                )
                embeds = create_embeds(ladder_abbrev, current_matches_json[ladder_abbrev])

            try:
                if count >= len(channel_messages):
                    await qm_bot_channel.send(content=message_text[:2000], embeds=embeds)
                else:
                    await channel_messages[count].edit(content=message_text[:2000], embeds=embeds)
                count += 1
            except (HTTPException, Forbidden, DiscordServerError, Exception) as e:
                msg = (
                    f"Failed to send/edit message in '{server.name}.{qm_bot_channel.name}' "
                    f"(ladder: {ladder_abbrev})\nMessage: '{message_text[:2000]}'\n**{type(e).__name__}:** {e}"
                )
                logger.error(msg)
                await send_message_to_log_channel(bot=bot, msg=msg)

        # Update time as last message
        time_updated_msg = f"*Updated* <t:{int(time.time())}:R>"
        try:
            if count >= len(channel_messages):
                await qm_bot_channel.send(content=time_updated_msg)
            else:
                await channel_messages[count].edit(content=time_updated_msg)
        except Exception as e:
            logger.warning(f"Failed to send final update timestamp: {e}")

        # Clean up any remaining old messages
        for extra_msg in channel_messages[count + 1:]:
            try:
                await extra_msg.delete()
                logger.debug(f"Deleted extra message: {extra_msg.id}")
            except Exception as e:
                logger.warning(f"Failed to delete extra message {extra_msg.id}: {e}")

    logger.debug("Completed fetching active matches.")


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
