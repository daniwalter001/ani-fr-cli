import urllib.parse
from providers.provider import Provider
import requests
import urllib


class MyAnimeList(Provider):
    api_base_url: str = "https://api.myanimelist.net/v2"
    jikan_base_url: str = "https://api.jikan.moe/v4"
    api_key = "b7e49a08ccf2a3a01a9382fd33abb63d"
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://myanimelist.net/",
            "X-Requested-With": "XMLHttpRequest",
            "X-MAL-CLIENT-ID": api_key,
        }
    )

    def search(self, search_term: str):

        limit = 25

        if not self.check_api():
            return False
        if not search_term:
            return False

        try:
            url = f"{self.jikan_base_url}/anime?q={urllib.parse.quote(search_term)}&limit={limit}&order_by=popularity"
            response = self.session.get(url)

            if response.status_code != 200:
                return False

            json_response = response.json()

            if json_response and "data" in json_response:
                return list(json_response["data"])

            return False

        except Exception as e:
            print(e)
            return False

    def by_id(self, anilist_id: str):
        if not anilist_id:
            return False

        try:
            url = f"{self.api_base_url}/anime/{anilist_id}?fields=id,title,main_picture,alternative_titles,synopsis,studios,pictures,background"
            response = self.session.get(url)

            if response.status_code != 200:
                return False

            json_response = response.json()

            if json_response and "id" in json_response:
                return dict(json_response)

        except:
            return False

    def get_eps_by_id(self, anilist_id: str):
        if not anilist_id:
            return False

        try:
            url = f"{self.jikan_base_url}/anime/{anilist_id}/episodes"
            response = self.session.get(url)

            if response.status_code != 200:
                return False

            json_response = response.json()

            if json_response and "data" in json_response:
                return list(json_response["data"])
        except:
            return False
