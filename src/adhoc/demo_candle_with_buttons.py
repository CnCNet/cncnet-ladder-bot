"""
Demonstration of updated candle command with interactive Daily/Monthly buttons.
This shows what messages would be posted when users run the !candle or /candle command.
"""

from datetime import datetime, timezone
import time


def generate_candle_output(player: str, ladder: str, wins: int, losses: int, points: int, period: str = "daily"):
    """
    Simulates the candle command output from candle.py
    This replicates the exact logic from src/commands/candle.py with button support
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
        message += f"[CANDLE] No games played {no_games_msg}"
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
        message += "[FLAME]\n"

        # Add red blocks for losses (at the top)
        for i in range(red_blocks):
            message += "[RED]\n"

        # Add green blocks for wins (at the bottom)
        for i in range(green_blocks):
            message += "[GREEN]\n"

        # Add stats summary
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        points_display = f"+{points}" if points >= 0 else str(points)
        message += f"\n[CHART] **{wins}W - {losses}L** ({win_rate:.1f}% WR) | {points_display} points"

    return message


def print_scenario_with_buttons(title: str, player: str, ladder: str,
                                  daily_wins: int, daily_losses: int, daily_points: int,
                                  monthly_wins: int, monthly_losses: int, monthly_points: int):
    """Print a scenario showing both daily and monthly views with button simulation"""
    print("=" * 80)
    print(f"SCENARIO: {title}")
    print("=" * 80)
    print(f"Player: {player}, Ladder: {ladder}")
    print(f"Daily Stats: {daily_wins}W - {daily_losses}L, {daily_points} points")
    print(f"Monthly Stats: {monthly_wins}W - {monthly_losses}L, {monthly_points} points")
    print()

    # Show initial view (Daily - default)
    print("INITIAL VIEW (Daily button active):")
    print("-" * 80)
    daily_output = generate_candle_output(player, ladder, daily_wins, daily_losses, daily_points, "daily")
    print(daily_output)
    print()
    print("Buttons: [Daily (Active)] [Monthly]")
    print("-" * 80)
    print()

    # Show monthly view when user clicks Monthly button
    print("AFTER CLICKING 'Monthly' BUTTON:")
    print("-" * 80)
    monthly_output = generate_candle_output(player, ladder, monthly_wins, monthly_losses, monthly_points, "monthly")
    print(monthly_output)
    print()
    print("Buttons: [Daily] [Monthly (Active)]")
    print("-" * 80)
    print()


def main():
    """Run various candle scenarios with button interactions"""
    print("\n")
    print("="*80)
    print("CANDLE COMMAND WITH INTERACTIVE BUTTONS - DEMONSTRATION")
    print("="*80)
    print("\nThis shows the new candle command with Daily/Monthly toggle buttons.")
    print("Users can click buttons to switch between daily and monthly views.")
    print("Note: Emojis are replaced with [TEXT] for console compatibility.\n")

    # Scenario 1: Active grinder
    print_scenario_with_buttons(
        title="Active Grinder - Good Day, Great Month",
        player="ProGrinder",
        ladder="yr",
        daily_wins=8, daily_losses=2, daily_points=35,
        monthly_wins=120, monthly_losses=55, monthly_points=450
    )

    # Scenario 2: New player
    print_scenario_with_buttons(
        title="New Player - First Day",
        player="NewbiePlayer",
        ladder="ra2",
        daily_wins=2, daily_losses=3, daily_points=-5,
        monthly_wins=2, monthly_losses=3, monthly_points=-5
    )

    # Scenario 3: Comeback month
    print_scenario_with_buttons(
        title="Comeback Day - Rough Month",
        player="ComebackKid",
        ladder="blitz",
        daily_wins=6, daily_losses=1, daily_points=28,
        monthly_wins=45, monthly_losses=68, monthly_points=-95
    )

    # Scenario 4: No games today, active month
    print_scenario_with_buttons(
        title="Day Off - Active Month",
        player="WeekendWarrior",
        ladder="yr",
        daily_wins=0, daily_losses=0, daily_points=0,
        monthly_wins=78, monthly_losses=42, monthly_points=215
    )

    # Scenario 5: Perfect records
    print_scenario_with_buttons(
        title="Perfect Day & Month",
        player="UnstoppableForce",
        ladder="yr",
        daily_wins=10, daily_losses=0, daily_points=60,
        monthly_wins=250, monthly_losses=0, monthly_points=1500
    )

    print("="*80)
    print("KEY FEATURES:")
    print("="*80)
    print("""
NEW INTERACTIVE FEATURES:
1. **Daily/Monthly Buttons**: Users can toggle between daily and monthly views
2. **Active Button Highlighting**: The current view's button is highlighted (Primary style)
3. **5-Minute Timeout**: Buttons remain active for 5 minutes after message is sent
4. **Real-time Updates**: Clicking a button fetches fresh data from the API

DAILY VIEW:
- Shows stats for current UTC day (00:00 - 23:59)
- Timestamp shows "Day started X hours ago"
- Perfect for tracking today's performance

MONTHLY VIEW:
- Shows stats for current calendar month
- Timestamp shows "Month started X days ago"
- Displays month name (e.g., "June 2026")
- Great for long-term performance tracking

API ENDPOINTS USED:
- Daily: /api/v1/ladder/{ladder}/player/{player}/today
- Monthly: /api/v1/ladder/{ladder}/player/{player}/month

NOTE: In actual Discord, buttons appear as interactive UI elements below the message.
      The active button is blue (primary), inactive is gray (secondary).
""")


if __name__ == "__main__":
    main()
