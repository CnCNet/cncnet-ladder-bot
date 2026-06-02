"""
Demonstration of fetch_active_qms output format.
This shows what messages would be posted to Discord channels.
"""

import time

# Sample data that would be passed to fetch_active_qms
SAMPLE_STATS_JSON = {
    "ra2": {"queuedPlayers": 3},
    "yr": {"queuedPlayers": 5},
    "blitz": {"queuedPlayers": 0},
    "blitz-2v2": {"queuedPlayers": 2}
}

SAMPLE_ACTIVE_MATCHES_JSON = {
    "ra2": [
        {
            "ladderType": "1vs1",
            "mapName": "Tour of Egypt",
            "gameDuration": "5:23",
            "players": [
                {"playerName": "ProPlayer1", "playerFaction": "Soviet", "playerColor": 1, "twitchProfile": "proplayer1", "twitchLiveAtStart": True},
                {"playerName": "ProPlayer2", "playerFaction": "Allied", "playerColor": 2}
            ]
        }
    ],
    "yr": [
        {
            "ladderType": "1vs1",
            "mapName": "Heck Freezes Over",
            "gameDuration": "12:45",
            "players": [
                {"playerName": "YuriMaster", "playerFaction": "Yuri", "playerColor": 0},
                {"playerName": "AlliedPro", "playerFaction": "Allied", "playerColor": 3, "twitchProfile": "alliedpro", "twitchLiveAtStart": True}
            ]
        },
        {
            "ladderType": "1vs1",
            "mapName": "Cold Winter",
            "gameDuration": "3:12",
            "players": [
                {"playerName": "Rookie1", "playerFaction": "Soviet", "playerColor": 1},
                {"playerName": "Rookie2", "playerFaction": "Soviet", "playerColor": 2}
            ]
        }
    ],
    "blitz": [],
    "blitz-2v2": [
        {
            "ladderType": "2vs2",
            "mapName": "Battle in the Sky",
            "gameDuration": "8:34",
            "players": [
                {"playerName": "TeamA1", "playerFaction": "Allied", "playerColor": 0, "teamId": 1},
                {"playerName": "TeamA2", "playerFaction": "Soviet", "playerColor": 1, "teamId": 1},
                {"playerName": "TeamB1", "playerFaction": "Allied", "playerColor": 2, "teamId": 2, "twitchProfile": "teamb1stream", "twitchLiveAtStart": True},
                {"playerName": "TeamB2", "playerFaction": "Allied", "playerColor": 3, "teamId": 2}
            ]
        }
    ]
}


def players_in_queue(ladder_abbrev: str, stats_json: dict, num_active_matches: int) -> str:
    """Simulates the function from get_active_matches.py"""
    title = ladder_abbrev.upper()
    if ladder_abbrev == 'ra2-cl':
        title = 'RA2 Clan'

    in_queue = stats_json.get('queuedPlayers', 0)
    total_in_qm = in_queue + (num_active_matches * (4 if '2v2' in ladder_abbrev else 2))

    if total_in_qm == 0:
        return f"- **0** in **{title}** Ladder"
    return f"- **{total_in_qm}** in **{title}** Ladder, **{in_queue}** waiting in queue"


def simulate_output():
    """Simulates what fetch_active_qms would output"""

    # Simulate processing for a Discord server (DEV_DISCORD_ID)
    # Ladders for dev server: ["ra2", "yr", "blitz", "blitz-2v2"]
    ladder_abbrev_arr = ["ra2", "yr", "blitz", "blitz-2v2"]

    print("="*80)
    print("SIMULATED OUTPUT FROM fetch_active_qms")
    print("="*80)
    print("\nThis shows what would be posted/edited in the Discord #ladder-bot channel:")
    print()

    # Build summary lines
    summary_lines = []
    for ladder_abbrev in ladder_abbrev_arr:
        if ladder_abbrev not in SAMPLE_STATS_JSON:
            summary_lines = ["Active Ladder stats are temporarily unavailable. Alert admins if this persists."]
            break
        else:
            msg = players_in_queue(
                ladder_abbrev=ladder_abbrev,
                stats_json=SAMPLE_STATS_JSON[ladder_abbrev],
                num_active_matches=len(SAMPLE_ACTIVE_MATCHES_JSON.get(ladder_abbrev, []))
            )
            summary_lines.append(msg)

    # Add timestamp (Discord format)
    current_timestamp = int(time.time())
    time_updated_msg = f"*Updated* <t:{current_timestamp}:R>"
    summary_text = "\n".join(summary_lines) + "\n" + time_updated_msg

    print("-" * 80)
    print("MESSAGE CONTENT:")
    print("-" * 80)
    print(summary_text)
    print()

    # Show embeds info
    print("-" * 80)
    print("EMBEDS (Match Details):")
    print("-" * 80)
    print()

    total_embeds = 0
    for ladder_abbrev in ladder_abbrev_arr:
        matches = SAMPLE_ACTIVE_MATCHES_JSON.get(ladder_abbrev, [])
        if matches:
            for match in matches:
                total_embeds += 1
                print(f"Embed #{total_embeds}:")
                print(f"  Title: {ladder_abbrev.upper()}")
                print(f"  Description: {match['mapName']}")
                print(f"               {match['gameDuration']}")
                print(f"  Type: {match['ladderType']}")

                if match['ladderType'] == '1vs1':
                    for idx, player in enumerate(match['players'], 1):
                        color_name = {0: "Yellow", 1: "Red", 2: "Blue", 3: "Green"}.get(player['playerColor'], "Unknown")
                        twitch_info = ""
                        if player.get('twitchProfile') and player.get('twitchLiveAtStart'):
                            twitch_info = f" - Watch at: [{player['twitchProfile']}](https://www.twitch.tv/{player['twitchProfile']})"
                        print(f"  Player {idx}: [{color_name}] {player['playerName']} ({player['playerFaction']}){twitch_info}")
                elif match['ladderType'] == '2vs2':
                    teams = {}
                    for player in match['players']:
                        team_id = player.get('teamId', 'observer')
                        if team_id not in teams:
                            teams[team_id] = []
                        teams[team_id].append(player)

                    for team_id, players in teams.items():
                        team_name = f"Team {team_id}" if team_id != 'observer' else "Observer"
                        print(f"  {team_name}:")
                        for player in players:
                            color_name = ["Yellow", "Red", "Blue", "Green", "Orange", "Light Blue", "Purple", "Pink"][player['playerColor'] % 8]
                            twitch_info = ""
                            if player.get('twitchProfile') and player.get('twitchLiveAtStart'):
                                twitch_info = f" - Watch at: [{player['twitchProfile']}](https://www.twitch.tv/{player['twitchProfile']})"
                            print(f"    [{color_name}] {player['playerName']} ({player['playerFaction']}){twitch_info}")
                print()

    if total_embeds == 0:
        print("  (No active matches)")

    print("="*80)
    print("EXPLANATION:")
    print("="*80)
    print("""
The function does the following:
1. Aggregates queue/match stats for all ladders configured for the server
2. Calculates total players in QM (queued + in active matches)
3. Creates one message with:
   - Summary lines showing total players per ladder
   - Discord timestamp showing when last updated (updates every 30 seconds)
   - Embeds (up to 10) showing active match details with:
     * Map name and game duration
     * Player names, factions, and colors
     * Twitch stream links if player is live
4. Either edits existing message or posts new one (message caching)
5. Repeats for all authorized Discord servers the bot is in
""")

    print("\nNOTE: The Discord timestamps like '<t:1234567890:R>' render as")
    print("      relative times (e.g., '2 minutes ago') in actual Discord.")
    print()


if __name__ == "__main__":
    simulate_output()
