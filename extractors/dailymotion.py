from bs4 import BeautifulSoup
from urllib import parse
import requests
from extractors.extractor import Extractor
import re


class DailyMotion:

    keywords = ["dailymotion"]

    host = "https://www.dailymotion.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://video.sibnet.ru",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in DailyMotion.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                DailyMotion.headers = {"Referer": referer}

            response = requests.get(url, headers=DailyMotion.headers, timeout=10)
            return response.text
        except:
            return False

    @staticmethod
    def extract(url, referer=None):

        html_content = DailyMotion.fetch(url)

        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        pattern = r"player\.src\(\[\{src:\s*[\"\'](.+?)[\"\'],"

        result = {
            "referer": url,
        }

        temp_url = ""

        try:
            match = re.search(pattern, html_content)

            if match:
                temp_url = parse.urljoin(DailyMotion.host, match.group(1))

            while not result.get("url"):
                response = requests.get(
                    temp_url,
                    headers=DailyMotion.headers,
                    timeout=10,
                    allow_redirects=False,
                )

                if response.status_code == 200:
                    temp_url = response.headers["Location"]
                    result["url"] = temp_url
                    break

                elif response.status_code >= 300 and response.status_code < 400:
                    DailyMotion.headers["referer"] = "https://video.sibnet.ru/"
                    temp_url = response.headers["Location"]
                    if temp_url.startswith("//"):
                        temp_url = "http:" + temp_url
                    DailyMotion.headers["Host"] = parse.urlparse(temp_url).netloc

                    if response.headers.get("content-length"):
                        result["url"] = temp_url
                        break

                    continue

                else:
                    print(response.status_code)
                    input("stop...")
                    break

            return result
        except Exception as e:
            print(e)
            input("stop...")

    @staticmethod
    def get_cookie(video_id, referer=None):
        if not video_id:
            return None

        url = parse.urljoin(DailyMotion.host, f"/c.php?videoid={video_id}")
        headers_ = {"referer": referer, "host": parse.urlparse(referer).netloc}

        try:
            response = requests.head(url, headers=headers_, timeout=10)

            if response.status_code == 200:
                return response.headers["Set-Cookie"]

        except Exception as e:
            print(e)
            input("stop...")
            return
