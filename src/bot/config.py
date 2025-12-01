"""Bot configuration management"""
import os
from typing import Set
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Central configuration for the bot"""

    # Discord settings
    token: str
    debug: bool
    command_prefix: str = '!'

    # Task intervals (in seconds/minutes/hours)
    update_bot_channel_interval_seconds: int = 30
    update_bot_channel_error_interval_seconds: int = 90
    update_channel_name_interval_minutes: int = 10
    sync_roles_interval_hours: int = 8

    # Authorized servers
    authorized_servers: Set[int] = None

    @classmethod
    def from_env(cls) -> 'BotConfig':
        """
        Load configuration from environment variables.

        Returns:
            BotConfig instance with values from .env file
        """
        load_dotenv()

        from src.constants.constants import (
            YR_DISCORD_ID,
            CNCNET_DISCORD_ID,
            BLITZ_DISCORD_ID,
            DEV_DISCORD_ID
        )

        return cls(
            token=str(os.getenv('DISCORD_CLIENT_SECRET')),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            authorized_servers={
                YR_DISCORD_ID,
                CNCNET_DISCORD_ID,
                BLITZ_DISCORD_ID,
                DEV_DISCORD_ID
            }
        )
