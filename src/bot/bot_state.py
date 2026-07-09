"""Bot state management"""
from typing import Optional, List
import asyncio
from src.svc.cncnet_api_svc import CnCNetApiSvc
from src.util.logger import MyLogger
from src.util.utils import is_error, get_exception_msg

logger = MyLogger("bot_state")


class BotState:
    """Manages bot state and API client"""

    def __init__(self):
        self.cnc_api_client: Optional[CnCNetApiSvc] = None
        self.ladders: List[str] = []
        self._ladder_load_failed_count: int = 0

    def initialize_api_client(self) -> None:
        """Initialize the CnCNet API client"""
        self.cnc_api_client = CnCNetApiSvc()
        logger.log("API client initialized")

    def load_ladders(self, max_retries: int = 5, retry_delay: int = 10) -> bool:
        """
        Fetch and store available ladders from CnCNet API with retry logic.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds (uses exponential backoff)

        Returns:
            bool: True if ladders were successfully loaded, False otherwise

        Raises:
            RuntimeError: If API client is not initialized
        """
        if not self.cnc_api_client:
            raise RuntimeError("API client not initialized")

        for attempt in range(max_retries):
            ladders_json = self.cnc_api_client.fetch_ladders()

            # Check if the API returned an error
            if is_error(ladders_json):
                self._ladder_load_failed_count += 1
                logger.error(f"Failed to load ladders (attempt {attempt + 1}/{max_retries}): {get_exception_msg(ladders_json)}")

                if attempt < max_retries - 1:
                    # Exponential backoff: 10s, 20s, 40s, 80s
                    wait_time = retry_delay * (2 ** attempt)
                    logger.log(f"Retrying in {wait_time} seconds...")
                    import time
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to load ladders after {max_retries} attempts. Bot will retry via background task.")
                    return False

            # Success - process the ladder list
            try:
                new_ladders = []
                for item in ladders_json:
                    if item.get("private") == 0:
                        new_ladders.append(item["abbreviation"])

                # Only update if we got a valid list
                if new_ladders:
                    self.ladders = new_ladders
                    self._ladder_load_failed_count = 0
                    logger.log(f"Loaded {len(self.ladders)} ladders: {', '.join(self.ladders)}")
                    return True
                else:
                    logger.error("API returned empty ladder list")
                    return False

            except (KeyError, TypeError, AttributeError) as e:
                logger.error(f"Error parsing ladder data: {e}")
                return False

        return False

    async def refresh_ladders_async(self) -> bool:
        """
        Asynchronously refresh the ladder list without blocking.

        Returns:
            bool: True if ladders were successfully refreshed, False otherwise
        """
        logger.log("Refreshing ladder list...")

        # Run the synchronous load_ladders in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: self.load_ladders(max_retries=3, retry_delay=5))

        if result:
            logger.log("Ladder list refreshed successfully")
        else:
            logger.error("Failed to refresh ladder list")

        return result
