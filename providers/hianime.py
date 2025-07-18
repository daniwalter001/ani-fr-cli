import urllib.parse
import requests
from bs4 import BeautifulSoup, Tag
from parser.beautifulSoup import BeautifulScraper

from util.functions import check_anime


class HiAnime:
    url = "https://aniwatchtv.to"
    api = "https://aniwatchtv.to"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36",
        "referer": "https://aniwatchtv.to",
    }

    souper = BeautifulScraper()

    def get_first_from_selects(self, soup: BeautifulSoup | Tag, selector: list[str]):
        empty_tag = Tag(name="a") if "a" in selector else Tag(name="span")
        try:
            r = empty_tag
            for s in selector:
                r = soup.select(s, limit=1)
                if not r:
                    return empty_tag
                r = r[0]

            return r
        except:
            return empty_tag

    def search(self, query="", type=""):
        if not query:
            return []

        parseQuery = query.replace(" ", "+")
        api = urllib.parse.urljoin(self.url, "search?keyword=" + parseQuery)

        soup = self.souper.fetchAndParse(api, self.headers)

        if not soup:
            return []

        search_results = self.extract_search_results(soup)

        if not search_results:
            return []

        print(search_results)

        if not soup:
            return []

        return search_results

    def fetch(self, query="", type="TV", extra_titles: list = []):

        if not query:
            return None

        parseQuery = query.replace(" ", "+")
        api = urllib.parse.urljoin(self.url, "search?keyword=" + parseQuery)

        if type:
            if type == "Movie":
                api = api + "&type=1"
            elif type == "TV":
                api = api + "&type=2"

        soup = self.souper.fetchAndParse(api, self.headers)

        if not soup:
            return None

        search_results = self.extract_search_results(soup)

        if not search_results:
            return None

        if not soup:
            return None

        queries = [query]

        if extra_titles:
            queries.extend(extra_titles)

        # print("queries========")
        # print([i for i in queries])

        # print("search_results========")
        # print([i["title"] for i in search_results])

        # input("stop...")

        first_try = check_anime(queries, search_results)

        if not first_try:
            return search_results[0] if search_results else None

        return first_try

    def extract_search_results(self, soup: BeautifulSoup):

        res_nodes = soup.select("div.film_list-wrap div.flw-item", limit=30)

        if not res_nodes:
            return []

        results = []

        for i, node in enumerate(res_nodes):

            if not node:
                continue

            to_append = {
                "title": self.get_first_from_selects(node, ["h3.film-name"]).text,
                "url": urllib.parse.urljoin(
                    self.url,
                    self.get_first_from_selects(node, ["h3.film-name", "a"]).get(
                        "href"
                    ),  # type: ignore
                ),
                "image": self.get_first_from_selects(node, ["div.film-poster img"]).get(
                    "data-src"
                ),
                "description": self.get_first_from_selects(
                    node, ["div.fd-infor"]
                ).text.replace("\n", " "),
                "duration": self.get_first_from_selects(
                    node, ["div.fd-infor span.fdi-item.fdi-duration"]
                ).text,
                "type": self.get_first_from_selects(
                    node, ["div.fd-infor span.fdi-item"]
                ).text,
            }

            to_append["id"] = to_append["url"].split("-")[-1].replace("?ref=search", "")

            results.append(to_append)

        return results

    def fetch_eps(self, anime_id: str):
        if not anime_id:
            return []

        try:
            api = urllib.parse.urljoin(self.url, "/ajax/v2/episode/list/" + anime_id)

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return []

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []

            json_response = response.json()

            if not json_response or "html" not in json_response:
                print("Error: False positive response")
                return []

            html = response.json()["html"]

            soup = self.souper.parse(html)
            if not soup:
                return []

            eps = self.extract_eps(soup)

            if not eps:
                return []

            return eps

        except:
            return []

    def extract_eps(self, soup: BeautifulSoup):
        try:
            eps_nodes = soup.select("div.ss-list a")
            results = []

            for ep in eps_nodes:
                results.append(
                    {
                        "title": ep.get("title"),
                        "url": ep.get("href"),
                        "order": ep.get("data-number") or ep.text,
                        "id": ep.get("data-id"),
                    }
                )
            return results
        except:
            return []

    def fetch_servers(self, ep_id=""):

        if not ep_id:
            return []

        try:
            api = urllib.parse.urljoin(
                self.url, "/ajax/v2/episode/servers?episodeId=" + ep_id
            )

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return []

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []

            json_response = response.json()

            if not json_response or "html" not in json_response:
                print("Error: False positive response")
                return []

            html = response.json()["html"]

            soup = self.souper.parse(html)

            if not soup:
                return []

            servers = self.extract_servers(soup)

            if not servers:
                return []

            return servers

        except:
            return []

    def extract_servers(self, soup: BeautifulSoup):
        try:
            servers_nodes = soup.select("div.ps__-list div")
            results = []

            for server in servers_nodes:
                _to_return = {
                    "title": self.get_first_from_selects(server, ["a.btn"]).text,
                    "type": server.get("data-type") or "",
                    "id": server.get("data-id"),
                    "server-id": server.get("data-server-id"),
                }

                _to_return["data"] = self.fetch_server_data(_to_return["id"])

                results.append(_to_return)
            return results
        except:
            return []

    def fetch_server_data(self, server_id):
        if not server_id:
            return False

        api = urllib.parse.urljoin(self.url, "/ajax/v2/episode/sources?id=" + server_id)

        response = requests.get(api, headers=self.headers, timeout=10)

        if not response:
            print("Error: Invalid response")
            return False

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return False

        json_response = response.json()

        if not json_response or "link" not in json_response:
            print("Error: False positive response")
            return False

        return json_response
