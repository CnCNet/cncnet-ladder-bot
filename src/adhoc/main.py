import os

from discord.ext import commands
from dotenv import load_dotenv

from src.constants.Constants import DEV_DISCORD_ID, BLITZ_DISCORD_ID, CNCNET_DISCORD_ID, YR_DISCORD_ID
from src.util.Embed import *

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_CLIENT_SECRET')

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Sample match data
match_data = {
    "mapName": "Barrens",
    "mapUrl": "https://ladder.cncnet.org/images/maps/yr/011efbdac56a80afc301e52d70565c0cb92c6ab6.png",
    "gameDuration": "4 mins 3 sec",
    "players": [
        {"playerName": "Burg", "playerFaction": "America", "playerColor": "red", "teamId": "1"},
        {"playerName": "Palacio", "playerFaction": "Iraq", "playerColor": "yellow", "teamId": "1"},
        {"playerName": "Ardee", "playerFaction": "America", "playerColor": "green", "teamId": "2"},
        {"playerName": "Fomalhaut", "playerFaction": "Iraq", "playerColor": "blue", "teamId": "2"}
    ]
}

match_data_1v1 = {
    "mapName": "Arabian Oasis",
    "mapUrl": "https://ladder.cncnet.org/images/maps/yr/daef8a59785f070a6242db3bbc1336b2e23ade9f.png",
    "gameDuration": "4 mins 3 sec",
    "players": [
        {"playerName": "Burg", "playerFaction": "America", "playerColor": "red"},
        {"playerName": "Palacio", "playerFaction": "Iraq", "playerColor": "yellow"}
    ]
}


# Send the embed when bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # channel = bot.get_channel(CNCNET_LADDER_DEV_DISCORD_BOT_LOGS_ID)
    # if channel:
    #     embed = create_team_match_embed("Blitz 2v2", match_data)
    #
    #     # await channel.send(
    #     #     content="Here are today's matches:",
    #     #     embeds=[embed]
    #     # )
    #
    # if channel:
    #     embed = create_1v1_match_embed("Red Alert 2", match_data_1v1)
    #
    #     await channel.send(
    #         content="Here are today's matches:",
    #         embeds=[embed]
    #     )

    print("Checking existing guilds...")
    for guild in bot.guilds:
        if guild.id != YR_DISCORD_ID and guild.id != CNCNET_DISCORD_ID and guild.id != BLITZ_DISCORD_ID and guild.id != DEV_DISCORD_ID:
            print(f"Leaving unauthorized server on startup: {guild.name} (ID: {guild.id})")
            await guild.leave()
        else:
            print(f"Remaining in authorized server: {guild.name} (ID: {guild.id})")
    print("Finished checking guilds.")

    # cnc_api_client = CnCNetApiSvc(
    #     response_handler=JsonResponseHandler
    # )
    #
    # stats_json = cnc_api_client.fetch_stats("all")
    # await fetch_active_qms(bot=bot, stats_json=stats_json, cnc_api_client=cnc_api_client)

bot.run(TOKEN)
