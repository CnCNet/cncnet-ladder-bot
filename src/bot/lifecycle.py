"""Bot lifecycle and initialization management"""
from typing import TYPE_CHECKING
from discord.ext import commands
import discord

if TYPE_CHECKING:
    from src.bot.bot_state import BotState
    from src.bot.config import BotConfig

from src.util.utils import send_message_to_log_channel
from src.util.logger import MyLogger
from src.constants.constants import QM_BOT_CHANNEL_NAME

logger = MyLogger("lifecycle")


class BotLifecycle:
    """Manages bot initialization and lifecycle events"""

    def __init__(self, bot: commands.Bot, state: 'BotState', config: 'BotConfig'):
        """
        Initialize the lifecycle manager.

        Args:
            bot: Discord bot instance
            state: Bot state manager
            config: Bot configuration
        """
        self.bot = bot
        self.state = state
        self.config = config

    async def on_ready(self) -> None:
        """
        Handle bot ready event.
        Called when the bot has successfully connected to Discord.
        """
        logger.log(f"Bot online with DEBUG={self.config.debug}")
        await send_message_to_log_channel(self.bot, "Ladder bot is online...")

        await self.check_authorized_servers()
        await self.purge_bot_channels()
        self.state.initialize_api_client()
        self.state.load_ladders()
        await self.sync_slash_commands()

    async def check_authorized_servers(self) -> None:
        """
        Check all connected servers and leave unauthorized ones.

        The bot will only remain in servers listed in the
        authorized_servers configuration.
        """
        logger.log("Checking existing guilds...")

        for guild in self.bot.guilds:
            if guild.id not in self.config.authorized_servers:
                logger.log(f"Leaving unauthorized server: {guild.name} (ID: {guild.id})")
                await guild.leave()
            else:
                logger.log(f"Remaining in authorized server: {guild.name} (ID: {guild.id})")

        logger.log("Finished checking guilds.")

    async def sync_slash_commands(self) -> None:
        """
        Sync slash commands with Discord.

        This registers all slash commands with Discord's API
        so they appear in the client.
        """
        try:
            synced = await self.bot.tree.sync()
            logger.log(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def purge_bot_channels(self) -> None:
        """
        Purge messages from all bot channels across all servers.

        This cleans up old messages when the bot starts to ensure
        a fresh state.
        """
        for server in self.bot.guilds:
            for channel in server.channels:
                if QM_BOT_CHANNEL_NAME in channel.name:
                    try:
                        message_count = 0
                        async for _ in channel.history(limit=2):
                            message_count += 1
                            if message_count > 0:  # Keep 0 messages
                                deleted = await channel.purge()
                                logger.debug(
                                    f"Deleted {len(deleted)} message(s) from: "
                                    f"server '{server.name}', channel: '{channel.name}'"
                                )
                                continue
                    except (discord.DiscordServerError, discord.errors.HTTPException) as e:
                        await send_message_to_log_channel(
                            bot=self.bot,
                            msg=f"Failed to purge messages from server '{server.name}', {str(e)}"
                        )
