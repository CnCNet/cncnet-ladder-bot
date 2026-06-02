from datetime import datetime, timezone
import time
from src.util.logger import MyLogger

logger = MyLogger("Candle")


async def candle(ctx, bot, player, ladder, ladders, cnc_api_client):
    """Check a player's daily wins and losses for a specific ladder."""
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
    total_games = wins + losses

    # Get current UTC date and start of day timestamp
    now_utc = datetime.now(timezone.utc)
    utc_date = now_utc.strftime('%Y-%m-%d')

    # Calculate start of day (00:00 UTC) timestamp for Discord formatting
    start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_day_timestamp = int(start_of_day.timestamp())

    # Discord timestamp formatting - shows "X hours ago" to indicate day progress
    day_started_msg = f"<t:{start_of_day_timestamp}:R>"

    # Build the candle visualization
    message = f"**{player}** on **{ladder_actual.upper()}** - Today's Candle ({utc_date} UTC)\n"
    message += f"*Day started {day_started_msg}*\n\n"

    if total_games == 0:
        message += "🕯️ No games played today"
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

    await ctx.send(message)