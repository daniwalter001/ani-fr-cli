import urllib.parse
import requests
from bs4 import BeautifulSoup, Tag
from parser.beautifulSoup import BeautifulScraper
import re
import json

from util.functions import check_anime, extract_links, join_path, remove_special_chars


class AnimeUltra:
    url = "https://v8.animesultra.net/"
    search_api = "https://v8.animesultra.net/engine/ajax/controller.php?mod=search"
    eps = "https://v8.animesultra.net/engine/ajax/full-story.php?newsId=127&d=1752141531510"

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

        print(api)

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

        queries = [query]

        first_try = check_anime(queries, search_results)

        if not first_try:
            return search_results[0] if search_results else None  # type: ignore

        return first_try

    def extract_search_results(self, soup: BeautifulSoup):

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
                        self.get_first_from_selects(node, ["div.film-poster img"]).get(
                            "data-src"
                        )
                    ),
                ),
                "description": remove_special_chars(
                    self.get_first_from_selects(node, ["div.fd-infor"]).text.replace(
                        "\n", " "
                    )
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

    def get_id_from_url(self, url: str):
        pattern = r".+\/(\d+)-.+"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def fetch_saisons(self, anime_url: str):
        if not anime_url:
            return []

        try:
            api = (
                anime_url
                if anime_url.startswith("http")
                else urllib.parse.urljoin(self.url, anime_url)
            )

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return []

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []

            soup = self.souper.parse(response.text)
            if not soup:
                return []

            eps = self.extract_saisons(soup, anime_url)

            if not eps:
                return []

            return eps

        except Exception as e:
            print(f"Error: {e}")
            input("...stop...")
            return []

    def extract_saisons(self, soup: BeautifulSoup, anime_url: str):

        try:

            results = []

            # Trouver tous les h2 dans le document
            for h2 in soup.find_all("h2"):
                h2_text = h2.get_text(strip=True)

                if "Anime" in h2_text:
                    next_div = h2.find_next("div", class_="flex")
                    if next_div:
                        script = next_div.find("script")  # type: ignore
                        if script:
                            script_content = script.string  # type: ignore
                            pattern = r'panneauAnime\("([^"]+)",\s*"([^"]+)"\)'
                            matches = re.findall(pattern, script_content)  # type: ignore
                            for title, link in matches:
                                if title == "nom":
                                    continue
                                results.append(
                                    {
                                        "title": title,
                                        "link": join_path([anime_url, link]),
                                        "type": "kai" if "Kai" in h2_text else "anime",
                                    }
                                )

                elif "Manga" in h2_text:
                    next_div = h2.find_next("div", class_="flex")
                    if next_div:
                        script = next_div.find("script")  # type: ignore
                        if script:
                            script_content = script.string  # type: ignore
                            pattern = r'panneauScan\("([^"]+)",\s*"([^"]+)"\)'
                            matches = re.findall(pattern, script_content)  # type: ignore
                            for title, link in matches:
                                if title == "nom":
                                    continue
                                results.append(
                                    {"title": title, "link": link, "type": "manga"}
                                )

            return results
        except Exception as e:
            return []

    def fetch_eps(self, season_url: str):

        if not season_url:
            return []

        try:
            api = urllib.parse.urljoin(self.url, season_url)

            response = requests.get(api, headers=self.headers, timeout=10)

            if not response:
                print("Error: Invalid response")
                return []

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return []

            results = self.extract_eps(response.text)

            return results

        except Exception as e:
            print(f"Error: {e}")
            input("stop...")
            return []

    def extract_eps(self, content: str):
        pattern = r"var\s+(eps\w+)\s*=\s*\[([\s\S]*?)\];"

        try:
            matches = re.findall(pattern, content)

            # Créer un dictionnaire pour stocker les listes par source
            sources_dict = {}

            for var_name, array_content in matches:

                # Nettoyer le contenu du tableau
                array_content = array_content.strip()
                if array_content.endswith(","):
                    array_content = array_content[:-1]

                # Convertir en liste Python
                try:
                    json_array = extract_links(array_content)
                    sources_dict[var_name] = json_array

                except json.JSONDecodeError:
                    continue

            # Déterminer le nombre d'épisodes (max parmi toutes les sources)
            max_episodes = max(len(urls) for urls in sources_dict.values())

            # Construire la liste finale
            result = []
            for i in range(max_episodes):
                episode_sources = []
                # Parcourir les sources dans l'ordre (eps1, eps2, eps3, eps4)
                for j in sources_dict.keys():
                    source_name = j
                    if source_name in sources_dict and i < len(
                        sources_dict[source_name]
                    ):
                        episode_sources.append(sources_dict[source_name][i])
                result.append({"episode": i + 1, "sources": episode_sources})
            return result
        except Exception as e:
            print(f"Error: {e}")
            input("...stop...")
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
