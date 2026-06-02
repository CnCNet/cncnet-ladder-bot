from datetime import datetime, timezone
import time
import discord
from discord.ui import View, Button
from src.util.logger import MyLogger
from src.constants.constants import BUTTON_COOLDOWN_SECONDS

logger = MyLogger("Candle")


def build_candle_message(player: str, ladder: str, wins: int, losses: int, points: int, period: str = "daily"):
    """
    Build the candle visualization message.

    Args:
        player: Player name
        ladder: Ladder name
        wins: Number of wins
        losses: Number of losses
        points: Points gained/lost
        period: "daily" or "monthly"

    Returns:
        Formatted candle message string
    """
    total_games = wins + losses

    # Get current UTC date and time info
    now_utc = datetime.now(timezone.utc)
    utc_date = now_utc.strftime('%Y-%m-%d')

    # Build the header based on period
    if period == "daily":
        # Calculate start of day (00:00 UTC) timestamp for Discord formatting
        start_of_period = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_period_timestamp = int(start_of_period.timestamp())
        period_started_msg = f"<t:{start_of_period_timestamp}:R>"

        message = f"**{player}** on **{ladder.upper()}** - Today's Candle ({utc_date} UTC)\n"
        message += f"*Day started {period_started_msg}*\n\n"
    else:  # monthly
        # Calculate start of month timestamp
        start_of_month = now_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month_timestamp = int(start_of_month.timestamp())
        period_started_msg = f"<t:{start_of_month_timestamp}:R>"
        month_name = now_utc.strftime('%B %Y')

        message = f"**{player}** on **{ladder.upper()}** - This Month's Candle ({month_name})\n"
        message += f"*Month started {period_started_msg}*\n\n"

    if total_games == 0:
        no_games_msg = "today" if period == "daily" else "this month"
        message += f"🕯️ No games played {no_games_msg}"
    else:
        # Maximum candle height (excluding flame and stats)
        max_candle_height = 15

        # Calculate scaled blocks if needed
        if total_games > max_candle_height:
            # Scale down proportionally
            scale_factor = max_candle_height / total_games
            red_blocks = round(losses * scale_factor)
            green_blocks = round(wins * scale_factor)

            # Ensure at least 1 block if there are wins/losses
            if losses > 0 and red_blocks == 0:
                red_blocks = 1
            if wins > 0 and green_blocks == 0:
                green_blocks = 1

            # Adjust if total exceeds max (due to rounding)
            total_blocks = red_blocks + green_blocks
            if total_blocks > max_candle_height:
                if red_blocks > green_blocks:
                    red_blocks -= 1
                else:
                    green_blocks -= 1

        else:
            red_blocks = losses
            green_blocks = wins

        # Add flame at top if there are games
        message += "🔥\n"

        # Add red blocks for losses (at the top)
        for i in range(red_blocks):
            message += "🟥\n"

        # Add green blocks for wins (at the bottom)
        for i in range(green_blocks):
            message += "🟩\n"

        # Add stats summary
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        points_display = f"+{points}" if points >= 0 else str(points)
        message += f"\n📊 **{wins}W - {losses}L** ({win_rate:.1f}% WR) | {points_display} points"

    return message


class CandleView(View):
    """Interactive view with Daily/Monthly buttons for candle command."""

    def __init__(self, player: str, ladder: str, cnc_api_client, initial_period: str = "daily", cooldown_seconds: int = BUTTON_COOLDOWN_SECONDS):
        super().__init__(timeout=300)  # 5 minute timeout
        self.player = player
        self.ladder = ladder
        self.cnc_api_client = cnc_api_client
        self.current_period = initial_period
        self.cooldown_seconds = cooldown_seconds
        self.last_interaction_time = {}  # (user_id, button_id) -> timestamp

        # Update button styles based on current period
        self.update_button_styles()

    def is_on_cooldown(self, user_id: int, button_id: str) -> tuple[bool, float]:
        """
        Check if user is on cooldown for a specific button.

        Args:
            user_id: Discord user ID
            button_id: Button custom_id ("daily" or "monthly")

        Returns:
            Tuple of (is_on_cooldown: bool, remaining_seconds: float)
        """
        key = (user_id, button_id)
        if key not in self.last_interaction_time:
            return False, 0.0

        elapsed = time.time() - self.last_interaction_time[key]
        remaining = self.cooldown_seconds - elapsed

        if remaining > 0:
            return True, remaining
        return False, 0.0

    def update_button_styles(self):
        """Update button styles to show which period is active."""
        for child in self.children:
            if isinstance(child, Button):
                if child.custom_id == "daily":
                    child.style = discord.ButtonStyle.primary if self.current_period == "daily" else discord.ButtonStyle.secondary
                elif child.custom_id == "monthly":
                    child.style = discord.ButtonStyle.primary if self.current_period == "monthly" else discord.ButtonStyle.secondary

    @discord.ui.button(label="Daily", style=discord.ButtonStyle.primary, custom_id="daily")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle Daily button click."""
        # Check cooldown for this specific button
        on_cooldown, remaining = self.is_on_cooldown(interaction.user.id, "daily")
        if on_cooldown:
            await interaction.response.send_message(
                f"Please wait {remaining:.0f} seconds before clicking Daily again.",
                ephemeral=True
            )
            return

        # Update last interaction time for this button
        self.last_interaction_time[(interaction.user.id, "daily")] = time.time()

        await interaction.response.defer()

        # Fetch daily stats
        stats = self.cnc_api_client.fetch_player_daily_stats(self.ladder, self.player)

        if isinstance(stats, Exception):
            logger.error(f"Exception fetching daily stats for {self.player} on {self.ladder}: {type(stats).__name__}, {str(stats)}")
            await interaction.followup.send(f"Error: Could not fetch daily stats for {self.player}", ephemeral=True)
            return

        if "error" in stats:
            logger.error(f"API error fetching daily stats for {self.player} on {self.ladder}: {stats.get('error')}")
            await interaction.followup.send(f"Error: Could not fetch daily stats for {self.player}", ephemeral=True)
            return

        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        points = stats.get('points', 0)

        # Update current period and button styles
        self.current_period = "daily"
        self.update_button_styles()

        # Build and send updated message
        message = build_candle_message(self.player, self.ladder, wins, losses, points, "daily")
        await interaction.edit_original_response(content=message, view=self)

    @discord.ui.button(label="Monthly", style=discord.ButtonStyle.secondary, custom_id="monthly")
    async def monthly_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle Monthly button click."""
        # Check cooldown for this specific button
        on_cooldown, remaining = self.is_on_cooldown(interaction.user.id, "monthly")
        if on_cooldown:
            await interaction.response.send_message(
                f"Please wait {remaining:.0f} seconds before clicking Monthly again.",
                ephemeral=True
            )
            return

        # Update last interaction time for this button
        self.last_interaction_time[(interaction.user.id, "monthly")] = time.time()

        await interaction.response.defer()

        # Fetch monthly stats
        stats = self.cnc_api_client.fetch_player_monthly_stats(self.ladder, self.player)

        if isinstance(stats, Exception):
            logger.error(f"Exception fetching monthly stats for {self.player} on {self.ladder}: {type(stats).__name__}, {str(stats)}")
            await interaction.followup.send(f"Error: Could not fetch monthly stats for {self.player}", ephemeral=True)
            return

        if "error" in stats:
            logger.error(f"API error fetching monthly stats for {self.player} on {self.ladder}: {stats.get('error')}")
            await interaction.followup.send(f"Error: Could not fetch monthly stats for {self.player}", ephemeral=True)
            return

        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        points = stats.get('points', 0)

        # Update current period and button styles
        self.current_period = "monthly"
        self.update_button_styles()

        # Build and send updated message
        message = build_candle_message(self.player, self.ladder, wins, losses, points, "monthly")
        await interaction.edit_original_response(content=message, view=self)


async def candle(ctx, bot, player, ladder, ladders, cnc_api_client):
    """Check a player's daily wins and losses for a specific ladder with interactive period selection."""
    if not player:
        await ctx.send("Usage: `!candle <player> <ladder>`")
        return

    # Case-insensitive ladder matching
    ladder_lower = ladder.lower()
    ladder_map = {l.lower(): l for l in ladders}

    if ladder_lower not in ladder_map:
        await ctx.send(f"Invalid ladder '{ladder}'. Available ladders: {', '.join(ladders)}")
        return

    # Use the exact ladder name from the API
    ladder_actual = ladder_map[ladder_lower]

    # Fetch initial daily stats
    stats = cnc_api_client.fetch_player_daily_stats(ladder_actual, player)

    if isinstance(stats, Exception):
        logger.error(f"Exception fetching daily stats for {player} on {ladder_actual}: {type(stats).__name__}, {str(stats)}")
        await ctx.send(f"Error: Could not fetch stats for {player} on {ladder_actual.upper()}")
        return

    if "error" in stats:
        logger.error(f"API error fetching daily stats for {player} on {ladder_actual}: {stats.get('error')}")
        await ctx.send(f"Error: Could not fetch stats for {player} on {ladder_actual.upper()}")
        return

    wins = stats.get('wins', 0)
    losses = stats.get('losses', 0)
    points = stats.get('points', 0)

    # Build the initial candle message (daily view)
    message = build_candle_message(player, ladder_actual, wins, losses, points, "daily")

    # Create the interactive view with buttons
    view = CandleView(player, ladder_actual, cnc_api_client, initial_period="daily")

    # Send message with interactive buttons
    await ctx.send(message, view=view)
