import re
import requests

from util.functions import remove_special_chars

# import


# {\\?['\"]src\\?['\"]:\\?['\"](.+?)\\?['\"],


class VidCdn:

    keywords = ["vidcdn"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://play.vidcdn.xyz",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in VidCdn.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                VidCdn.headers["referer"] = referer

            response = requests.get(url, headers=VidCdn.headers, timeout=10)
            return response.text
        except Exception as e:
            print(e)
            input("stop...erreur")
            return False

    @staticmethod
    def extract(url: str, referer=None):
        try:
            pattern = r"{\\?['\"]src\\?['\"]:\\?['\"](.+?)\\?['\"],"

            html_content = VidCdn.fetch(url, referer)

            if not html_content:
                return None

            match = re.search(pattern, html_content, re.DOTALL)

            if not match:
                return None

            url_match = match.group(1)

            if not url_match:
                return None

            return {"url": remove_special_chars(url_match), "referer": url}
        except:
            return None
