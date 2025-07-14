import re
import requests
import jsbeautifier


class Smoothpre:

    keywords = ["smoothpre", "Smoothpre", "movearnpre"]
    beautifier = jsbeautifier.Beautifier()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://Smoothpre.com",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword.lower() in url.lower() for keyword in Smoothpre.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                Smoothpre.headers["referer"] = referer

            response = requests.get(url, headers=Smoothpre.headers, timeout=10)
            return response.text
        except Exception as e:
            print(e)
            input("stop...erreur")
            return False

    @staticmethod
    def extract(url: str, referer=None):

        try:
            upacker_pattern = r"(eval\(function\(p,a,c,k,e,d\).*)\s+"

            html_content = Smoothpre.fetch(url, referer)

            if not html_content:
                return None

            match = re.search(upacker_pattern, html_content, re.DOTALL)

            if not match:
                return None

            js_to_eval = match.group(1)

            if not js_to_eval:
                return None

            js_content = Smoothpre.beautifier.unpack(js_to_eval)

            if not js_content:
                return None

            # Recherche de l'URL dans les sources
            url_pattern = r"var\s*links\s*=\s*({.*?});"
            url_match = re.search(url_pattern, str(js_content), re.MULTILINE)

            if not url_match:
                return None

            links = Smoothpre.extract_links(url_match.group(1))

            if not links:
                return None

            return {"url": links[0], "referer": url}

        except Exception as e:
            print(e)
            input("stop...erreur")
            return None

    @staticmethod
    def extract_links(text):
        url_pattern = r"https?://[^\s\'\"]+"

        # Find all matches in the text
        urls = re.findall(url_pattern, text)

        return urls
