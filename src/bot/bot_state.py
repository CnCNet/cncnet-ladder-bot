"""Bot state management"""
from typing import Optional, List
from src.svc.cncnet_api_svc import CnCNetApiSvc
from src.util.logger import MyLogger

logger = MyLogger("bot_state")


class BotState:
    """Manages bot state and API client"""

    def __init__(self):
        self.cnc_api_client: Optional[CnCNetApiSvc] = None
        self.ladders: List[str] = []

    def initialize_api_client(self) -> None:
        """Initialize the CnCNet API client"""
        self.cnc_api_client = CnCNetApiSvc()
        logger.log("API client initialized")

    def load_ladders(self) -> None:
        """
        Fetch and store available ladders from CnCNet API.

        Raises:
            RuntimeError: If API client is not initialized
        """
        if not self.cnc_api_client:
            raise RuntimeError("API client not initialized")

        self.ladders = []
        ladders_json = self.cnc_api_client.fetch_ladders()

        for item in ladders_json:
            if item.get("private") == 0:
                self.ladders.append(item["abbreviation"])

        logger.log(f"Loaded {len(self.ladders)} ladders: {', '.join(self.ladders)}")
