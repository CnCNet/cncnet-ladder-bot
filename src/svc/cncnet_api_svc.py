
import requests
from src.util.logger import MyLogger

logger = MyLogger("CnCNetApiSvc")

class CnCNetApiSvc:
    host = "https://ladder.cncnet.org"
    timeout = 20  # seconds

    def get_json(self, url):
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"RequestException: {type(e).__name__}, URL: {url}, Message: {str(e)}, Args: {e.args}")
            return e

    def fetch_stats(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/stats"
        return self.get_json(url)

    def fetch_ladders(self):
        url = f"{self.host}/api/v1/ladder"
        return self.get_json(url)

    def fetch_maps(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/maps/public"
        return self.get_json(url)

    def fetch_pros(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/pros"
        return self.get_json(url)

    def active_matches(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/active_matches"
        return self.get_json(url)

    def fetch_rankings(self):
        url = f"{self.host}/api/v1/qm/ladder/rankings"
        return self.get_json(url)

    def fetch_errored_games(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/erroredGames"
        return self.get_json(url)

    def fetch_recently_washed_games(self, ladder, hours):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/{hours}/recentlyWashedGames"
        return self.get_json(url)

    def fetch_player_daily_stats(self, ladder, player):
        url = f"{self.host}/api/v1/ladder/{ladder}/player/{player}/today"
        return self.get_json(url)

