from src.svc.CnCNetApiSvc import CnCNetApiSvc
from src.util.MyLogger import MyLogger
import json
from src.util.Utils import *
from src.util.Embed import *
from discord import Forbidden, DiscordServerError
import time
from http.client import HTTPException

logger = MyLogger("GetActiveMatches")


def players_in_queue(ladder_abbrev: str, stats_json: json):
    title = ladder_abbrev.upper()
    if ladder_abbrev == 'ra2-cl':
        title = 'RA2 Clan'

    # Get players in queue

    in_queue = stats_json['queuedPlayers']

    total_in_qm = in_queue + (stats_json['activeMatches'] * 2)  # players in queue + players in a match

    if total_in_qm == 0:
        msg = f"**0** players in **{title}** Ladder"
    else:
        if '2v2' in ladder_abbrev:
            total_in_qm = in_queue + (stats_json['activeMatches'] * 4)
            msg = f"**{str(total_in_qm)}** in **{title}** Ladder, **{str(in_queue)}** waiting in queue"
        else:
            msg = f"**{str(total_in_qm)}** in **{title}** Ladder, **{str(in_queue)}** waiting in queue"
    return msg


async def fetch_active_qms(bot: Bot, stats_json: json, cnc_api_client: CnCNetApiSvc):
    logger.debug("Fetching active qms")

    current_matches_json: json = cnc_api_client.active_matches("all")

    if is_error(current_matches_json):
        fail_msg = f"Error fetching current_matches'.\n{get_exception_msg(current_matches_json)}"
        await send_message_to_log_channel(bot, f"{fail_msg}")
        return

    guilds = bot.guilds
    for server in guilds:

        if server.id == DEV_DISCORD_ID:  # skip dev discord
            continue

        # grab which ladders to fetch for this discord server
        server_info: dict = DISCORDS.get(server.id)
        if server_info is None:
            logger.error(f"Unexpected server ID: {server.id}")
            continue

        ladder_abbrev_arr: list = server_info['ladders']
        qm_bot_channel = bot.get_channel(server_info['qm_bot_channel_id'])

        if not qm_bot_channel:
            raise ValueError(f"Unable to find channel for {server.name}, channel {server_info['qm_bot_channel_id']}")

        # Loop through each ladder and get the results
        # Display active games in all ladders
        count = 0
        channel_messages = await get_channel_msgs(channel=qm_bot_channel, limit=10)
        for ladder_abbrev in ladder_abbrev_arr:

            embeds: list = []
            if ladder_abbrev not in stats_json:
                send_msg = f"Ladder not found in stats, {ladder_abbrev}."
                await send_message_to_log_channel(f"{send_msg}")
                message_text = f"Failed fetching ladder stats for {ladder_abbrev}"
            else:
                message_text = players_in_queue(ladder_abbrev, stats_json[ladder_abbrev])
                if stats_json[ladder_abbrev]['activeMatches'] > 0:
                    embeds = create_embeds(ladder_abbrev=ladder_abbrev, match_data=current_matches_json[ladder_abbrev])

            if count == 0:
                message_text = f"*Updated* <t:{int(time.time())}:R>" + f"\n\n{message_text}"

            try:
                if count >= len(channel_messages):
                    await qm_bot_channel.send(content=message_text[:2000], embeds=embeds)
                else:
                    await channel_messages[count].edit(content=message_text[:2000],
                                                       embeds=embeds)  # edit the existing msg
            except HTTPException as he:
                msg = f"Failed to send message '{message_text[:2000]}' to '{server}'\nexception: '{he}'"
                logger.error(msg)
                await send_message_to_log_channel(bot, msg)
                return
            except Forbidden as f:
                msg = f"Failed to send message '{message_text[:2000]}' \nforbidden error:  to '{server}' exception: '{f}'"
                logger.error(msg)
                await send_message_to_log_channel(bot, msg)
                return
            except DiscordServerError as de:
                msg = f"Failed to send message '{message_text[:2000]}'\nDiscordServerError: to '{server}' exception: '{de}'"
                logger.error(msg)
                await send_message_to_log_channel(bot, msg)
                return

            count += 1

    logger.debug("completed fetching active matches")


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
