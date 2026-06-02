"""
Demonstration of candle command output.
This shows what messages would be posted when users run the !candle or /candle command.
"""

from datetime import datetime, timezone
import time


def generate_candle_output(player: str, ladder: str, wins: int, losses: int, points: int):
    """
    Simulates the candle command output from candle.py
    This replicates the exact logic from src/commands/candle.py
    """
    total_games = wins + losses

    # Get current UTC date and time elapsed
    now_utc = datetime.now(timezone.utc)
    utc_date = now_utc.strftime('%Y-%m-%d')

    # Calculate start of day (00:00 UTC) timestamp for Discord formatting
    start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_day_timestamp = int(start_of_day.timestamp())

    # Discord timestamp formatting - shows "X hours ago" to indicate day progress
    day_started_msg = f"<t:{start_of_day_timestamp}:R>"

    # Build the candle visualization
    message = f"**{player}** on **{ladder.upper()}** - Today's Candle ({utc_date} UTC)\n"
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

    return message


def print_scenario(title: str, player: str, ladder: str, wins: int, losses: int, points: int):
    """Print a scenario with its output"""
    print("=" * 80)
    print(f"SCENARIO: {title}")
    print("=" * 80)
    print(f"Input: player='{player}', ladder='{ladder}', wins={wins}, losses={losses}, points={points}")
    print()
    print("Output:")
    print("-" * 80)
    output = generate_candle_output(player, ladder, wins, losses, points)
    # Replace emojis with text for Windows console compatibility
    display_output = output
    display_output = display_output.replace("🕯️", "[CANDLE]")
    display_output = display_output.replace("🔥", "[FLAME]")
    display_output = display_output.replace("🟥", "[RED]")
    display_output = display_output.replace("🟩", "[GREEN]")
    display_output = display_output.replace("📊", "[CHART]")

    print(display_output)
    print("-" * 80)
    print()


def main():
    """Run various candle scenarios"""
    print("\n")
    print("="*80)
    print("CANDLE COMMAND OUTPUT DEMONSTRATION")
    print("="*80)
    print("\nThis shows the exact output format from the candle command.")
    print("Note: Emojis are replaced with [TEXT] for console compatibility,")
    print("but in Discord they appear as actual emoji symbols.\n")

    # Scenario 1: No games played
    print_scenario(
        title="No Games Today",
        player="IdlePlayer",
        ladder="yr",
        wins=0,
        losses=0,
        points=0
    )

    # Scenario 2: Perfect win streak
    print_scenario(
        title="Perfect Day - All Wins",
        player="ProPlayer",
        ladder="yr",
        wins=5,
        losses=0,
        points=25
    )

    # Scenario 3: Losing streak
    print_scenario(
        title="Rough Day - All Losses",
        player="NewbiePlayer",
        ladder="ra2",
        wins=0,
        losses=4,
        points=-20
    )

    # Scenario 4: Mixed results
    print_scenario(
        title="Mixed Results - Positive Record",
        player="RegularPlayer",
        ladder="blitz",
        wins=7,
        losses=3,
        points=15
    )

    # Scenario 5: Close to even
    print_scenario(
        title="Balanced Day",
        player="BalancedPlayer",
        ladder="yr",
        wins=6,
        losses=5,
        points=3
    )

    # Scenario 6: Scaled candle (more than 15 games)
    print_scenario(
        title="Very Active Day - Scaled (20 games)",
        player="GrindPlayer",
        ladder="yr",
        wins=14,
        losses=6,
        points=45
    )

    # Scenario 7: Extreme grind
    print_scenario(
        title="Extreme Grind - Scaled (50 games)",
        player="NoLifePlayer",
        ladder="yr",
        wins=35,
        losses=15,
        points=120
    )

    # Scenario 8: One game only - win
    print_scenario(
        title="Single Game Win",
        player="CasualPlayer",
        ladder="blitz-2v2",
        wins=1,
        losses=0,
        points=5
    )

    # Scenario 9: One game only - loss
    print_scenario(
        title="Single Game Loss",
        player="UnluckyPlayer",
        ladder="ra2-2v2",
        wins=0,
        losses=1,
        points=-5
    )

    print("="*80)
    print("KEY FEATURES:")
    print("="*80)
    print("""
1. UTC Date: Shows the current UTC date for the candle
2. Day Progress: Discord timestamp showing when the UTC day started (e.g., "14 hours ago")
3. Candle Visual:
   - Flame on top if there are games
   - Red blocks for losses (at top, below flame)
   - Green blocks for wins (at bottom)
   - Scaled down if > 15 total games
4. Stats: Win-loss record, win rate percentage, and points gained/lost
5. No Games: Special candle emoji if player hasn't played today

NOTE: In actual Discord, the timestamp '<t:1234567890:R>' renders as a
      relative time that updates automatically (e.g., "14 hours ago").
""")


if __name__ == "__main__":
    main()
