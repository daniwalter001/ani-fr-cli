from bs4 import BeautifulSoup
from urllib import parse
import requests
from extractors.extractor import Extractor


class Sibnet(Extractor):

    keywords = ["sibnet"]

    host = "https://video.sibnet.ru"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://video.sibnet.ru",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in Sibnet.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                Sibnet.headers = {"Referer": referer}

            response = requests.get(url, headers=Sibnet.headers, timeout=10)
            return response.text
        except:
            return False

    @staticmethod
    def extract(url):

        html_content = Sibnet.fetch(url)

        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        script_tags = soup.find_all("script", {"type": "text/javascript"})

        result = {"referer": None, "src": None}

        for script in script_tags:
            if script.string and "countersibnet" in script.string:  # type: ignore

                script_string = script.string  # type: ignore
                # Extraire le referer
                if "referrer" in script_string:
                    referer_start = script_string.find("'referrer' : '") + len(
                        "'referrer' : '"
                    )
                    referer_end = script_string.find("'", referer_start)
                    result["referer"] = script_string[referer_start:referer_end]  # type: ignore

                if "player.src" in script_string:
                    src_start = script_string.find('src: "') + len('src: "')
                    src_end = script_string.find('"', src_start)
                    result["src"] = script_string[src_start:src_end]  # type: ignore

                if result["referer"] and result["src"]:
                    result["src"] = parse.urljoin(Sibnet.host, result["src"])  # type: ignore
                    break

        return result if result["referer"] or result["src"] else None


# Exemple d'utilisation
# html_content = """[votre code HTML ici]"""
# extracted_data = extract_referer_and_src(html_content)
# print(extracted_data)
