import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.constants.constants import DEV_DISCORD_ID, BLITZ_DISCORD_ID, CNCNET_DISCORD_ID, YR_DISCORD_ID

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

    print("Checking existing guilds...")
    for guild in bot.guilds:
        if guild.id != YR_DISCORD_ID and guild.id != CNCNET_DISCORD_ID and guild.id != BLITZ_DISCORD_ID and guild.id != DEV_DISCORD_ID:
            print(f"Leaving unauthorized server on startup: {guild.name} (ID: {guild.id})")
            await guild.leave()
        else:
            print(f"Remaining in authorized server: {guild.name} (ID: {guild.id})")
    print("Finished checking guilds.")

bot.run(TOKEN)
