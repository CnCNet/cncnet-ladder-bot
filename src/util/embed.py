import discord

player_color_to_emoji = {
    "red": "🔴",
    "blue": "🔵",
    "light blue": ":light_blue:",
    "green": "🟢",
    "yellow": "🟡",
    "purple": "🟣",
    "black": "⚫",
    "white": "⚪",
    "orange": "🟠",
    "brown": "🟤",
    "pink": "🌸",  # No good circle emoji for pink, optional alternative
    # Add more mappings if needed
}

game_color = {
    "ra2": discord.Color.red(),
    "ra2-2v2": discord.Color.dark_red(),
    "ra": discord.Color.green(),
    "blitz": discord.Color.orange(),
    "yr": discord.Color.purple(),
    # "black": "⚫",
    # "white": "⚪",
    "blitz-2v2": discord.Color.teal(),
    # "brown": "🟤",
    # "pink": "🌸",  # No good circle emoji for pink, optional alternative
    # Add more mappings if needed
}


def _create_base_embed(ladder_abbrev: str, match_data: dict) -> discord.Embed:
    """Create the base embed with title, description, and thumbnail."""
    embed = discord.Embed(
        title=ladder_abbrev.upper(),
        description=f"{match_data['mapName']}\n{match_data['gameDuration']}",
        color=game_color.get(ladder_abbrev.lower(), discord.Color.light_gray())
    )
    embed.set_thumbnail(url=match_data["mapUrl"])
    return embed


def _format_player_string(player: dict, is_observer: bool) -> str:
    """Format a player's display string with color emoji, faction, and Twitch link."""
    player_name = player['playerName']
    twitch_profile = player.get('twitchProfile')
    twitch_live_at_start = player.get('twitchLiveAtStart', False)

    # Observers don't show color emoji or faction
    if is_observer:
        color_emoji = ""
        faction = None
        show_twitch = bool(twitch_profile)  # Show Twitch if profile exists (no live check)
    else:
        player_color = get_player_color_from_index(player['playerColor']).lower()
        color_emoji = player_color_to_emoji.get(player_color, "")
        faction = player['playerFaction']
        show_twitch = bool(twitch_profile and twitch_live_at_start)  # Show Twitch only if live

    # Build the player string
    if show_twitch:
        twitch_url = f"https://www.twitch.tv/{twitch_profile}"
        twitch_link_text = twitch_profile
        if is_observer:
            return f"{player_name} - Watch at: [{twitch_link_text}]({twitch_url})"
        else:
            return f"{color_emoji} {player_name} ({faction}) - Watch at: [{twitch_link_text}]({twitch_url})"
    else:
        if is_observer:
            return player_name
        else:
            return f"{color_emoji} {player_name} ({faction})"


def create_embeds(ladder_abbrev: str, match_data: list) -> list:
    embeds = []

    for match in match_data:
        if match['ladderType'] == "1vs1":
            embed = create_1v1_match_embed(ladder_abbrev=ladder_abbrev, match_data=match)
        elif match['ladderType'] == "2vs2":
            embed = create_team_match_embed(ladder_abbrev=ladder_abbrev, match_data=match)
        else:
            raise ValueError(f"Unexpected ladderType: {match['ladderType']}")  # More specific exception
        embeds.append(embed)

        if len(embeds) >= 10:
            break

    return embeds


def get_player_color_from_index(color_index: int):
    if color_index == 0:
        return "yellow"
    elif color_index == 1:
        return "red"
    elif color_index == 2:
        return "blue"
    elif color_index == 3:
        return "green"
    elif color_index == 4:
        return "orange"
    elif color_index == 5:
        return "light blue"
    elif color_index == 6:
        return "purple"
    elif color_index == 7:
        return "pink"
    raise ValueError(f"Unexpected color index: {str(color_index)}")


def create_team_match_embed(ladder_abbrev: str, match_data: dict) -> discord.Embed:
    embed = _create_base_embed(ladder_abbrev, match_data)

    # Group players by team
    teams = {}
    for player in match_data['players']:
        team_id = player['teamId']
        if team_id not in teams:
            teams[team_id] = []
        teams[team_id].append(player)

    # Add a field for each team
    for team_id, players in teams.items():
        is_observer = not team_id or str(team_id) == "observer"

        player_list = []
        for player in players:
            player_string = _format_player_string(player, is_observer)
            player_list.append(player_string)

        team_name = "Observer" if is_observer else f"Team {team_id}"

        embed.add_field(
            name=team_name,
            value="\n".join(player_list),
            inline=False
        )

    return embed


def create_1v1_match_embed(ladder_abbrev: str, match_data: dict) -> discord.Embed:
    embed = _create_base_embed(ladder_abbrev, match_data)

    # Separate observers from regular players
    observers = []
    players = []

    for player in match_data['players']:
        player_team = player.get('playerTeam')
        player_faction = player.get('playerFaction')

        # Detect observer by team field or faction
        if player_team == 'observer' or player_faction == 'Observer':
            observers.append(player)
        else:
            players.append(player)

    # Add regular players (numbered sequentially, excluding observers)
    for index, player in enumerate(players, start=1):
        player_string = _format_player_string(player, is_observer=False)

        embed.add_field(
            name=f"Player {index}",
            value=player_string,
            inline=False
        )

    # Add observers section
    if observers:
        observer_list = []
        for player in observers:
            player_string = _format_player_string(player, is_observer=True)
            observer_list.append(player_string)

        embed.add_field(
            name="Observer",
            value="\n".join(observer_list),
            inline=False
        )

    return embed
