from apiclient import APIClient
from apiclient.exceptions import APIRequestError

from src.util.MyLogger import MyLogger

logger = MyLogger("CnCNetApiSvc")


class CnCNetApiSvc(APIClient):
    host = "https://ladder.cncnet.org"

    def fetch_stats(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/stats"
        return self.get_call(url)

    def fetch_ladders(self):
        url = f"{self.host}/api/v1/ladder"
        return self.get_call(url)

    def fetch_maps(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/maps/public"
        return self.get_call(url)

    def fetch_pros(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/pros"
        return self.get_call(url)

    def active_matches(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/active_matches"
        return self.get_call(url)

    def fetch_rankings(self):
        url = f"{self.host}/api/v1/qm/ladder/rankings"
        return self.get_call(url)

    def fetch_errored_games(self, ladder):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/erroredGames"
        return self.get_call(url)

    def fetch_recently_washed_games(self, ladder, hours):
        url = f"{self.host}/api/v1/qm/ladder/{ladder}/{hours}/recentlyWashedGames"
        return self.get_call(url)

    def get_call(self, url):
        try:
            return self.get(url)
        except APIRequestError or Exception as e:
            logger.error(f"Status code: '{e.status_code}', message: '{e.message}', Info: '{e.info}', Cause: '{e.__cause__}'")
            return e

