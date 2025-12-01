"""Discord command registration and management"""
from typing import TYPE_CHECKING, List
from discord.ext import commands
from discord import app_commands, Interaction

if TYPE_CHECKING:
    from src.bot.bot_state import BotState

from src.commands.get_maps import get_maps
from src.commands.create_qm_roles import create_qm_roles as create_qm_roles_impl
from src.commands.candle import candle as candle_impl
from src.bot.slash_context import SlashContext
from src.util.logger import MyLogger

logger = MyLogger("command_manager")


class CommandManager:
    """Manages all bot commands (prefix and slash)"""

    def __init__(self, bot: commands.Bot, state: 'BotState'):
        """
        Initialize the command manager.

        Args:
            bot: Discord bot instance
            state: Bot state manager
        """
        self.bot = bot
        self.state = state

    def register_all_commands(self) -> None:
        """Register both prefix and slash commands"""
        self._register_prefix_commands()
        self._register_slash_commands()
        logger.log("All commands registered")

    def _register_prefix_commands(self) -> None:
        """Register legacy prefix commands (!command)"""

        @self.bot.command(name="maps")
        async def maps(ctx: commands.Context, arg: str = "") -> None:
            """
            Display the current QM map pool for a ladder.

            Usage: !maps <ladder>
            Example: !maps yr
            """
            await get_maps(
                ctx=ctx,
                bot=self.bot,
                arg=arg,
                ladders=self.state.ladders,
                cnc_api_client=self.state.cnc_api_client
            )

        @self.bot.command(name="candle")
        async def candle(ctx: commands.Context, player: str, ladder: str) -> None:
            """
            Display player's daily win/loss candle chart.

            Usage: !candle <player> <ladder>
            Example: !candle ProPlayer yr
            """
            await candle_impl(
                ctx=ctx,
                bot=self.bot,
                player=player,
                ladder=ladder,
                ladders=self.state.ladders,
                cnc_api_client=self.state.cnc_api_client
            )

        @self.bot.command(name="purge_bot_channel_command")
        async def purge_bot_channel_command(ctx: commands.Context) -> None:
            """
            Purge messages from the bot channel (Admin only).

            Usage: !purge_bot_channel_command
            """
            if not ctx.message.author.guild_permissions.administrator:
                logger.error(f"{ctx.message.author} is not admin, exiting command.")
                return

            await self._purge_bot_channel(0)

        @self.bot.command(name="create_qm_roles")
        async def create_qm_roles(ctx: commands.Context, ladder: str = None) -> None:
            """
            Create QM ranking roles for a ladder (Admin only).

            Usage: !create_qm_roles <ladder>
            Example: !create_qm_roles yr
            """
            await create_qm_roles_impl(ctx=ctx, bot=self.bot, ladder=ladder)

    def _register_slash_commands(self) -> None:
        """Register modern slash commands (/command)"""

        @self.bot.tree.command(name="maps", description="Display the current QM map pool for a ladder")
        @app_commands.describe(ladder="Which ladder's maps to display")
        @app_commands.autocomplete(ladder=self._ladder_autocomplete)
        async def maps_slash(interaction: Interaction, ladder: str) -> None:
            """Slash command version of !maps with autocomplete"""
            ctx = SlashContext(interaction)
            await get_maps(
                ctx=ctx,
                bot=self.bot,
                arg=ladder,
                ladders=self.state.ladders,
                cnc_api_client=self.state.cnc_api_client
            )

        @self.bot.tree.command(name="candle", description="Display player's daily win/loss candle chart")
        @app_commands.describe(
            ladder="Which ladder to check",
            player="Player name to lookup"
        )
        @app_commands.autocomplete(ladder=self._ladder_autocomplete)
        async def candle_slash(
            interaction: Interaction,
            ladder: str,
            player: str
        ) -> None:
            """Slash command version of !candle with ladder dropdown first"""
            ctx = SlashContext(interaction)
            await candle_impl(
                ctx=ctx,
                bot=self.bot,
                player=player,
                ladder=ladder,
                ladders=self.state.ladders,
                cnc_api_client=self.state.cnc_api_client
            )

        @self.bot.tree.command(name="create_qm_roles", description="Create QM ranking roles for a ladder (Admin only)")
        @app_commands.describe(ladder="Which ladder to create roles for")
        @app_commands.autocomplete(ladder=self._ladder_autocomplete)
        @app_commands.default_permissions(administrator=True)
        async def create_qm_roles_slash(interaction: Interaction, ladder: str) -> None:
            """Slash command version of !create_qm_roles with admin permission check"""
            ctx = SlashContext(interaction)
            await create_qm_roles_impl(ctx=ctx, bot=self.bot, ladder=ladder)

        @self.bot.tree.command(name="purge_bot_channel", description="Purge messages from the bot channel (Admin only)")
        @app_commands.default_permissions(administrator=True)
        async def purge_bot_channel_slash(interaction: Interaction) -> None:
            """Slash command version of !purge_bot_channel_command"""
            await interaction.response.defer(ephemeral=True)
            await self._purge_bot_channel(0)
            await interaction.followup.send("✅ Bot channel purged successfully!", ephemeral=True)

    async def _ladder_autocomplete(
        self,
        interaction: Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        """
        Provides autocomplete suggestions for ladder parameter.

        Args:
            interaction: The Discord interaction
            current: Current text typed by user

        Returns:
            List of matching ladder choices (max 25)
        """
        return [
            app_commands.Choice(name=ladder.upper(), value=ladder)
            for ladder in self.state.ladders
            if current.lower() in ladder.lower()
        ][:25]  # Discord limits to 25 choices

    async def _purge_bot_channel(self, keep_messages_count: int) -> None:
        """
        Purge messages from QM bot channels across all servers.

        Args:
            keep_messages_count: Number of messages to keep (0 = purge all)
        """
        from src.constants.constants import QM_BOT_CHANNEL_NAME
        from src.util.utils import send_message_to_log_channel
        import discord

        guilds = self.bot.guilds

        for server in guilds:
            for channel in server.channels:
                if QM_BOT_CHANNEL_NAME in channel.name:
                    try:
                        message_count = 0
                        async for _ in channel.history(limit=2):
                            message_count += 1
                            if message_count > keep_messages_count:
                                deleted = await channel.purge()
                                logger.debug(
                                    f"Deleted {len(deleted)} message(s) from: "
                                    f"server '{server.name}', channel: '{channel.name}'"
                                )
                                continue
                    except (discord.DiscordServerError, discord.errors.HTTPException) as e:
                        await send_message_to_log_channel(
                            bot=self.bot,
                            msg=f"Failed to delete message from server '{server.name}', {str(e)}"
                        )
