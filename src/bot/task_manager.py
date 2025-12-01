"""Background task management"""
from typing import TYPE_CHECKING
from discord.ext import tasks, commands

if TYPE_CHECKING:
    from src.bot.bot_state import BotState
    from src.bot.config import BotConfig

from src.tasks import update_channel_bot_task, sync_qm_ranking_roles_task
from src.tasks.update_qm_bot_channel_name_task import update_qm_bot_channel_name_task
from src.util.logger import MyLogger

logger = MyLogger("task_manager")


class TaskManager:
    """Manages all background tasks"""

    def __init__(self, bot: commands.Bot, state: 'BotState', config: 'BotConfig'):
        """
        Initialize the task manager.

        Args:
            bot: Discord bot instance
            state: Bot state manager
            config: Bot configuration
        """
        self.bot = bot
        self.state = state
        self.config = config
        self._setup_tasks()

    def _setup_tasks(self) -> None:
        """Set up all background tasks with their intervals"""

        @tasks.loop(seconds=self.config.update_bot_channel_interval_seconds)
        async def update_bot_channel() -> None:
            """
            Update bot channel with current QM statistics.
            Runs every 30 seconds, increases to 90 seconds on error.
            """
            response = await update_channel_bot_task.execute(
                bot=self.bot,
                ladders=self.state.ladders,
                cnc_api_client=self.state.cnc_api_client,
                debug=self.config.debug
            )

            if response.get("error"):
                logger.error(f"Error in update_bot_channel: {response['error']}")
                update_bot_channel.change_interval(
                    seconds=self.config.update_bot_channel_error_interval_seconds
                )
            else:
                # Restore interval to normal if previously changed due to error
                if update_bot_channel.seconds != self.config.update_bot_channel_interval_seconds:
                    update_bot_channel.change_interval(
                        seconds=self.config.update_bot_channel_interval_seconds
                    )

        @tasks.loop(minutes=self.config.update_channel_name_interval_minutes)
        async def update_channel_name() -> None:
            """
            Periodically update the QM bot channel name with player statistics.
            Runs every 10 minutes, skips first execution.
            """
            # Skip the first execution after bot comes online
            if not hasattr(update_channel_name, "_has_run"):
                update_channel_name._has_run = True
                return

            stats_json = self.state.cnc_api_client.fetch_stats("all")
            active_matches = self.state.cnc_api_client.active_matches(ladder="all")
            await update_qm_bot_channel_name_task(self.bot, stats_json, active_matches)

        @tasks.loop(hours=self.config.sync_roles_interval_hours)
        async def sync_roles() -> None:
            """
            Sync Discord roles with ladder rankings.
            Runs every 8 hours (production only).
            """
            await sync_qm_ranking_roles_task.execute(
                bot=self.bot,
                cnc_api_client=self.state.cnc_api_client
            )

        # Store task references
        self.update_bot_channel_task = update_bot_channel
        self.update_channel_name_task = update_channel_name
        self.sync_roles_task = sync_roles

    def start_all_tasks(self) -> None:
        """
        Start all background tasks.

        Note: sync_roles_task is only started if DEBUG is False.
        """
        self.update_bot_channel_task.start()
        self.update_channel_name_task.start()

        if not self.config.debug:
            self.sync_roles_task.start()

        logger.log("All background tasks started")

    def stop_all_tasks(self) -> None:
        """Stop all background tasks gracefully"""
        if self.update_bot_channel_task.is_running():
            self.update_bot_channel_task.cancel()

        if self.update_channel_name_task.is_running():
            self.update_channel_name_task.cancel()

        if self.sync_roles_task.is_running():
            self.sync_roles_task.cancel()

        logger.log("All background tasks stopped")
