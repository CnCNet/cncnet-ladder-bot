"""
CnCNet Ladder Discord Bot

Main entry point for the bot.
Monitors Quick Match queues and provides ladder statistics across multiple Discord servers.
"""
from discord.ext import commands
from discord import Intents

from src.bot.config import BotConfig
from src.bot.bot_state import BotState
from src.bot.lifecycle import BotLifecycle
from src.bot.command_manager import CommandManager
from src.bot.task_manager import TaskManager
from src.util.logger import MyLogger
from src.util.utils import send_message_to_log_channel

logger = MyLogger("main")


class CnCNetBot:
    """
    Main bot controller.

    Coordinates all bot components including configuration, state management,
    commands, tasks, and lifecycle events.
    """

    def __init__(self):
        """Initialize the bot and all its components"""
        # Load configuration from environment
        self.config = BotConfig.from_env()

        # Initialize Discord bot with required intents
        intents = Intents(
            messages=True,
            guilds=True,
            message_content=True,
            guild_messages=True,
            members=True
        )
        self.bot = commands.Bot(
            command_prefix=self.config.command_prefix,
            intents=intents
        )

        # Initialize bot components
        self.state = BotState()
        self.lifecycle = BotLifecycle(self.bot, self.state, self.config)
        self.command_manager = CommandManager(self.bot, self.state)
        self.task_manager = TaskManager(self.bot, self.state, self.config)

        # Register event handlers
        self._register_events()

        # Register all commands (prefix and slash)
        self.command_manager.register_all_commands()

        logger.log("CnCNet Bot initialized successfully")

    def _register_events(self) -> None:
        """Register Discord event handlers"""

        @self.bot.event
        async def on_ready():
            """Called when the bot successfully connects to Discord"""
            await self.lifecycle.on_ready()
            self.task_manager.start_all_tasks()

        @self.bot.event
        async def on_rate_limit(rate_limit_info):
            """Called when the bot is being rate limited by Discord"""
            logger.warning(f"WARNING - We are being rate limited: {rate_limit_info}")
            await send_message_to_log_channel(bot=self.bot, msg=str(rate_limit_info))

    def run(self) -> None:
        """Start the bot"""
        logger.log(f"Starting CnCNet Ladder Bot (DEBUG={self.config.debug})")
        try:
            self.bot.run(self.config.token)
        except KeyboardInterrupt:
            logger.log("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            raise
        finally:
            logger.log("Bot shutting down...")
            self.task_manager.stop_all_tasks()


if __name__ == "__main__":
    bot = CnCNetBot()
    bot.run()
