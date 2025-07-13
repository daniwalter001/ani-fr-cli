import urllib.parse
import requests
from bs4 import BeautifulSoup, Tag
from parser.beautifulSoup import BeautifulScraper
import re
import time

from util.functions import check_anime, extract_links, join_path, remove_special_chars


class AnimeUltra:
    url = "https://v8.animesultra.net/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36",
        "referer": "https://v8.animesultra.net/",
        "Cookie": "PHPSESSID=2ijhd9mmd6r8cp184i0f7hbf5",
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

        query = query.replace(":", "")
        query = query.replace(" ", "+")

        api = urllib.parse.urljoin(
            self.url, f"/?do=search&mode=advanced&subaction=search&story={query}"
        )

        soup = self.souper.fetchAndParse(api, extra_headers=self.headers)

        if not soup:
            return []

        search_results = self.extract_search_results(soup)

        # input("stop...")

        if not search_results:
            return []

        if not soup:
            return []

        return search_results

    def fetch(self, query="", type="TV", extra_titles: list = []):

        if not query:
            return None

        search_results = self.search(query, type)

        i = 0
        if len(search_results) == 0:
            while not search_results and i < len(extra_titles):
                print(extra_titles[i])
                search_results = self.search(extra_titles[i], type)
                i += 1
                if search_results:
                    break

        # queries = [query]

        # first_try = check_anime(queries, search_results)

        # if not first_try:
        #     return search_results[0] if search_results else None  # type: ignore

        # return first_try

        return search_results

    def extract_search_results(self, soup: BeautifulSoup):
        try:
            res_nodes = soup.select("div.flw-item", limit=30)

            if not res_nodes:
                return []

            results = []

            for i, node in enumerate(res_nodes):

                if not node:
                    continue

                to_append = {
                    "title": self.get_first_from_selects(
                        node, ["div.film-detail h3.film-name a"]
                    ).text,
                    "url": urllib.parse.urljoin(
                        self.url,
                        self.get_first_from_selects(node, ["div.film-detail h3.film-name a"]).get("href"),  # type: ignore
                    ),
                    "image": urllib.parse.urljoin(
                        self.url,
                        str(
                            self.get_first_from_selects(
                                node, ["div.film-poster img"]
                            ).get("data-src")
                        ),
                    ),
                    "description": remove_special_chars(
                        self.get_first_from_selects(
                            node, ["div.fd-infor"]
                        ).text.replace("\n", " ")
                    ),
                    "duration": remove_special_chars(
                        self.get_first_from_selects(node, ["span.fdi-duration"]).text
                    ),
                    "year": remove_special_chars(
                        self.get_first_from_selects(node, ["span.fdi-year"]).text
                    ),
                    "detail": remove_special_chars(
                        f"Dub: {self.get_first_from_selects(
                        node, ["div.tick-dub"]
                    ).text} | Eps: {self.get_first_from_selects(node, ['div.tick-eps']).text}"
                    ),
                    "type": None,
                }

                to_append["id"] = self.get_id_from_url(to_append["url"])

                results.append(to_append)

            return results
        except:
            return []

    def get_id_from_url(self, url: str):
        pattern = r".+\/(\d+)-.+"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def fetch_eps(self, anime_id: str):

        anime_url = f"/engine/ajax/full-story.php?newsId={anime_id}&d={int(time.time() * 1000)}"

        if not anime_url:
            return [], {}

        try:
            api = urllib.parse.urljoin(self.url, anime_url)

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return [], {}

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return [], {}

            json_response = response.json()

            if "html" not in json_response:
                return [], {}

            results = self.extract_eps(json_response["html"])
            sources = self.extract_sources(json_response["html"])

            return results, sources

        except Exception as e:
            print(f"Error: {e}")
            input("stop...")
            return [], {}

    def extract_eps(self, content: str):

        try:
            soup = self.souper.parse(content)
            if not soup:
                return []

            res_nodes = soup.select("div.ss-list a")

            if not res_nodes:
                return []

            results = []

            for i, node in enumerate(res_nodes):

                if not node:
                    continue

                to_append = {
                    "title": self.get_first_from_selects(node, ["div.ep-name"]).text,
                    "full_title": self.get_first_from_selects(
                        node, ["div.ep-name"]
                    ).get("title"),
                    "url": urllib.parse.urljoin(
                        self.url,
                        node.get("href"),  # type: ignore
                    ),
                    "season_name": node.get("title"),
                    "order": node.get("data-number")
                    or self.get_first_from_selects(node, ["div.ssli-order"]).text,
                    "id": node.get("data-id"),
                }

                results.append(to_append)

            return results
        except:
            return []

    def extract_sources(self, content: str):

        try:
            soup = self.souper.parse(content)
            if not soup:
                return {}

            res_nodes = soup.select("div.player_box")

            if not res_nodes:
                return {}

            results = dict()

            for i, node in enumerate(res_nodes):

                if not node:
                    continue

                to_append = {
                    "id": node.get("id"),
                    "content": node.text,
                }

                results[to_append["id"]] = to_append["content"]

            return results
        except:
            return {}

    def fetch_servers(self, url=""):

        if not url:
            return []

        try:
            api = url

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return []

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []

            html = response.text

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
            servers_nodes = soup.select("div.ps__-list div.item")
            results = []

            for server in servers_nodes:

                _to_return = {
                    "title": self.get_first_from_selects(server, ["a.btn"]).text,
                    "server": server.get("data-class") or "",
                    "type": server.get("data-type") or "",
                    "id": server.get("data-id"),
                    "server-id": server.get("data-server-id"),
                }
                _to_return["source-id"] = f"content_player_{_to_return['server-id']}"
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

    def switch_to_vf_or_vostfr(self, season):
        lang_vers = []

        if not season:
            return

        try:
            if season["link"].endswith("vostfr") or season["link"].endswith("vostfr/"):
                _t = {
                    "title": season["title"] + " VF",
                    "link": season["link"].replace("vostfr", "vf"),
                    "type": season["type"],
                }

                _t2 = {
                    "title": season["title"] + " VOSTFR",
                    "link": season["link"],
                    "type": season["type"],
                }

                lang_vers.append(_t)
                lang_vers.append(_t2)

            elif season["link"].endswith("vf") or season["link"].endswith("vf/"):
                _t = {
                    "title": season["title"] + " VOSTFR",
                    "link": season["link"].replace("vf", "vostfr"),
                    "type": season["type"],
                }

                _t2 = {
                    "title": season["title"] + " VF",
                    "link": season["link"],
                    "type": season["type"],
                }
                lang_vers.append(_t)
                lang_vers.append(_t2)

            return lang_vers
        except:
            return [season]

    def generate_embed_url(self, classserver: str, linktop: str) -> str:
        classserver = classserver.strip().lower()
        
        
        to_return = ""

        if classserver in ["mystream", "mystream nower"]:
            to_return = f"https://embed.mystream.to/{linktop}"
        elif classserver in ["streamtape", "streamtape nower"]:
            to_return = f"/dist/streamtap.php?id={linktop}"
            # to_return = f"/dist/streamtap.php?id={linktop}"
        elif classserver in ["uqload", "uqload nower"]:
            to_return = f"https://uqload.com/embed-{linktop}.html"
        elif classserver in ["cdnt2", "cdnt2 nower"]:
            to_return = f"https://mb.toonanime.xyz/dist/mpia.html?id={linktop}"
        elif classserver in ["vip", "vidcdn", "vid", "vip nower"]:
            to_return = linktop
        elif classserver in ["vidfast", "vidfast nower"]:
            to_return = f"https://vidfast.co/embed-{linktop}.html"
        elif classserver in ["verystream", "verystream nower"]:
            to_return = f"https://verystream.com/e/{linktop}"
        elif classserver in ["rapids", "rapids nower"]:
            to_return = f"https://rapidstream.co/embed-{linktop}.html"
        elif classserver in ["cloudvideo", "cloudvideo nower"]:
            to_return = f"https://cloudvideo.tv/embed-{linktop}.html"
        elif classserver in ["mytv", "mytv nower"]:
            to_return = f"https://www.myvi.tv/embed/{linktop}"
        elif classserver in ["myvi", "myvi nower"]:
            to_return = f"https://myvi.ru/player/embed/html/{linktop}"
        elif classserver in ["uptostream", "uptostream nower"]:
            to_return = f"https://uptostream.com/iframe/{linktop}"
        elif classserver in ["gtv", "gtv nower"]:
            to_return = f"https://iframedream.com/embed/{linktop}.html"
        elif classserver in ["fembed", "fembed nower"]:
            to_return = f"https://toopl.xyz/v/{linktop}.html"
        elif classserver in ["hydrax", "hydrax nower"]:
            to_return = f"https://hydrax.net/watch?v={linktop}"
        elif classserver in ["gou", "gou nower"]:
            to_return = f"/dist/indexgo.php?id={linktop}"
        elif classserver in ["cdnt", "cdnt nower"]:
            to_return = f"https://lb.toonanime.xyz/dist/aultra.html?id={linktop}"
        elif classserver in ["rapidvideo", "rapidvideo nower"]:
            to_return = f"https://www.rapidvideo.com/e/{linktop}"
        elif classserver in ["namba", "namba nower"]:
            to_return = linktop  # Cas spécial avec Flash, retourne le lien tel quel
        elif classserver in ["kaztube", "kaztube nower"]:
            to_return = f"https://kaztube.kz/video/embed/{linktop}"
        elif classserver in ["tune", "tune nower"]:
            to_return = f"https://tune.pk/player/embed_player.php?vid={linktop}"
        elif classserver in ["sibnet", "sibnet nower"]:
            # to_return = f"/dist/indexs.php?id={linktop}"
            to_return = f"https://video.sibnet.ru/shell.php?videoid={linktop}"
        elif classserver in ["netu", "netu nower"]:
            to_return = f"https://waaw.tv/watch_video.php?v={linktop}"
        elif classserver in ["rutube", "rutube nower"]:
            to_return = f"https://rutube.ru/play/embed/{linktop}"
        elif classserver in ["dailymotion", "dailymotion nower"]:
            to_return = (
                f"https://dailymotion.com/embed/video/{linktop}?logo=0&amp;info=0&amp;"
            )
        elif classserver in ["openload", "openload nower"]:
            to_return = f"https://openload.co/embed/{linktop}"
        elif classserver in ["yandex", "yandex nower"]:
            to_return = linktop  # Cas spécial avec Flash, retourne le lien tel quel
        elif classserver in ["ok", "ok nower"]:
            to_return = f"https://www.ok.ru/videoembed/{linktop}"
        elif classserver in [
            "vidspot",
            "vidspot nower",
            "vid",
            "vid nower",
            "cloudy",
            "cloudy nower",
            "google",
            "google nower",
            "youtube",
            "youtube nower",
            "moevideo",
            "moevideo nower",
        ]:
            to_return = linktop
        elif classserver in ["mail", "mail nower"]:
            to_return = f"https://videoapi.my.mail.ru/videos/embed/mail/{linktop}"
        elif classserver in ["mail2", "mail2 nower"]:
            to_return = f"https://my.mail.ru/video/embed/{linktop}"
        else:
            to_return = linktop  # Par défaut, retourne le lien tel quel

        to_return = remove_special_chars(to_return)
        return to_return