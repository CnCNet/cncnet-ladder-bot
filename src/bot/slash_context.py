"""Utility classes for slash command handling"""
from discord import Interaction


class SlashContext:
    """
    Adapter to make Discord Interactions compatible with existing
    command implementations that expect Context objects.

    This allows slash commands to reuse the same implementation
    as traditional prefix commands without code duplication.
    """

    def __init__(self, interaction: Interaction):
        """
        Initialize the context adapter.

        Args:
            interaction: Discord interaction from slash command
        """
        self.interaction = interaction
        self.channel = interaction.channel
        self.author = interaction.user
        self.guild = interaction.guild

    async def send(self, *args, **kwargs) -> None:
        """
        Send a message via interaction response or followup.

        Automatically handles whether the interaction has been
        responded to yet or requires a followup message.

        Args:
            *args: Positional arguments to pass to send_message
            **kwargs: Keyword arguments to pass to send_message
        """
        if not self.interaction.response.is_done():
            await self.interaction.response.send_message(*args, **kwargs)
        else:
            await self.interaction.followup.send(*args, **kwargs)
