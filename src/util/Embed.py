import discord

player_color_to_emoji = {
    "red": "🔴",
    "blue": "🔵",
    "light blue": ":Cyan:",
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
    match = match_data

    embed = discord.Embed(
        title=ladder_abbrev.upper(),  # Ladder name as title
        description=f"{match['mapName']}\n{match['gameDuration']}",  # Map name and duration on separate lines
        color=game_color.get(ladder_abbrev.lower(), discord.Color.light_gray())
    )

    embed.set_thumbnail(url=match["mapUrl"])

    # Group players by team
    teams = {}
    for player in match['players']:
        team_id = player['teamId']

        if team_id not in teams:
            teams[team_id] = []
        teams[team_id].append(player)

    # Add a field for each team
    for team_id, players in teams.items():
        print(f"Team {team_id}:")
        print(str(players))
        player_list = ""
        for player in players:
            player_color = get_player_color_from_index(player['playerColor']).lower()
            color_emoji = player_color_to_emoji.get(player_color, "")  # fallback if color missing
            faction = player['playerFaction']
            player_name = player['playerName']

            twitch_profile = player.get('twitchProfile')
            if not team_id or str(team_id) == "observer":
                twitch_url = None
                if twitch_profile:
                    twitch_url = f"https://www.twitch.tv/{twitch_profile}"
                if twitch_profile and twitch_url:
                    player_details = f"{color_emoji} {player_name} - Watch at: [{twitch_profile}]({twitch_url})\n"
                else:
                    player_details = f"{color_emoji} {player_name}\n"
            else:
                player_details = f"{color_emoji} {player_name} ({faction})\n"
        
            player_list += player_details
                
        if not team_id or str(team_id).lower() == "observer":
            name = "Observer"
        else:
            name = f"Team {team_id}"

        embed.add_field(
            name=name,
            value=player_list,
            inline=False
        )

    return embed


def create_1v1_match_embed(ladder_abbrev: str, match_data: dict) -> discord.Embed:
    match = match_data

    embed = discord.Embed(
        title=ladder_abbrev.upper(),  # Ladder name as title
        description=f"{match['mapName']}\n{match['gameDuration']}",  # Map name and duration on separate lines
        color=game_color.get(ladder_abbrev.lower(), discord.Color.light_gray())
    )

    embed.set_thumbnail(url=match["mapUrl"])

    for index, player in enumerate(match['players'], start=1):
        player_color = get_player_color_from_index(player['playerColor']).lower()
        color_emoji = player_color_to_emoji.get(player_color, "")  # fallback if color missing
        player_string = f"{color_emoji} {player['playerName']} ({player['playerFaction']})"

        embed.add_field(
            name=f"Player {index}",
            value=player_string,
            inline=False
        )

    return embed
