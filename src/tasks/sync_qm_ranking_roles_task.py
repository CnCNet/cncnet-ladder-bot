import os

from discord.utils import get

from src.util.utils import is_error, get_exception_msg, send_file_to_channel
from src.util.logger import MyLogger
from src.svc.cncnet_api_svc import CnCNetApiSvc
from src.constants.constants import YR_DISCORD_ID

logger = MyLogger("SyncQMRankingRoles")


# Patterns for QM roles to remove
QM_ROLE_PATTERNS = [
    "ra2 qm", "yr qm", "blitz-2v2 qm", "ra2-2v2 qm"
]


# Helper to determine the correct role name for a given ladder and rank
def get_role_name(ladder, rank):
    if rank == 1:
        return f"{ladder} QM Rank 1"
    elif rank <= 3:
        return f"{ladder} QM Top 3"
    elif rank <= 5:
        return f"{ladder} QM Top 5"
    elif rank <= 10:
        return f"{ladder} QM Top 10"
    elif rank <= 25:
        return f"{ladder} QM Top 25"
    elif rank <= 50:
        return f"{ladder} QM Top 50"
    return None

async def execute(bot, cnc_api_client):

    logger.debug("Starting update_qm_roles")

    # Remove all QM roles from members before assigning new ones
    await remove_qm_roles(bot=bot)

    # Assign new QM roles based on current rankings
    await assign_qm_role(bot=bot, cnc_api_client=cnc_api_client)

    logger.debug("completed updating QM roles")


async def remove_qm_roles(bot):
    logger.debug("Removing QM roles")
    guilds = bot.guilds

    for server in guilds:
        if server.id != YR_DISCORD_ID:  # Only process YR discord
            continue

        for member in server.members:
            for role in member.roles:

                # Don't remove champion roles
                if 'champion' in role.name.lower():
                    continue

                # Remove any QM role matching the patterns
                if any(pattern in role.name.lower() for pattern in QM_ROLE_PATTERNS):
                    await member.remove_roles(role)

    logger.debug("Finished removing QM roles")


async def assign_qm_role(bot, cnc_api_client: CnCNetApiSvc):
    logger.debug("Assigning QM Roles")
    guilds = bot.guilds

    # Fetch QM player ranks once
    rankings_json = cnc_api_client.fetch_rankings()
    if is_error(rankings_json):
        logger.log(f"No ranking results found, exiting assign_qm_role(). {get_exception_msg(rankings_json)}")
        return

    for server in guilds:
        if server.id != YR_DISCORD_ID:  # Only process YR discord
            continue

        ladder_abbrev_arr = ["RA2", "YR", "BLITZ-2V2", "RA2-2V2"]
        for ladder in ladder_abbrev_arr:
            rank = 0
            ladder_assignments = []  # Collect action messages for this ladder
            if ladder not in rankings_json:
                available_keys = list(rankings_json.keys())
                logger.warning(
                    f"[LADDER ASSIGNMENT WARNING] Requested ladder '{ladder}' not found in rankings_json. "
                    f"This may indicate a data issue or a misconfiguration. "
                    f"Available ladders: {available_keys}"
                )
                ladder_assignments.append(f"Ladder '{ladder}' not found in rankings_json.")
            else:
                for item in rankings_json[ladder][:50]:  # Only process top 50
                    rank += 1
                    discord_name = item["discord_name"]
                    player_name = item["player_name"]

                    # Skip if no discord name for player
                    if not discord_name:
                        msg = f"#{rank}: No discord name found for player '{player_name}'"
                        ladder_assignments.append(msg)
                        logger.debug(msg)
                        continue

                    # Find the Discord member by name
                    member = server.get_member_named(discord_name)
                    if not member:
                        msg = f"#{rank}: No user found with name '{discord_name}' for player '{player_name}' in server {server}"
                        ladder_assignments.append(msg)
                        logger.debug(msg)
                        continue

                    # Determine the correct role name
                    role_name = get_role_name(ladder, rank)
                    if not role_name:
                        msg = f"#{rank}: No valid role found for ladder '{ladder}'"
                        ladder_assignments.append(msg)
                        logger.debug(msg)
                        continue

                    # Find the role object in the server
                    role = get(server.roles, name=role_name)
                    if not role:
                        msg = f"#{rank}: No valid role found for role_name '{role_name}'"
                        ladder_assignments.append(msg)
                        logger.debug(msg)
                        continue

                    # Assign the role to the member
                    msg = f"#{rank}: Assigned role '{role_name}' to user '{discord_name}' (player '{player_name}')"
                    ladder_assignments.append(msg)
                    logger.debug(msg)
                    await member.add_roles(role)

            # Send a summary of actions taken for this ladder to the log channel
            if ladder_assignments:
                await send_file_to_channel(bot=bot, filename=f"Ladder {ladder}: role updates log.txt", content="\n".join(ladder_assignments))
    logger.debug("Completed assigning QM Roles")
