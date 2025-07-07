from bs4 import BeautifulSoup
import re
import requests
from extractors.extractor import Extractor


class SendVid(Extractor):

    # sendvid

    keywords = ["sendvid"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://sendvid.com/",
    }
    
    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in SendVid.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                SendVid.headers = {"Referer": referer}

            response = requests.get(url, headers=SendVid.headers, timeout=10)
            return response.text
        except:
            return False

    @staticmethod
    def extract(url: str, referer=None):

        html_content = SendVid.fetch(url, referer=referer)

        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        video_sources = []

        # Common video URL patterns to look for
        video_patterns = [
            r'(https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))',
            r'src\s*:\s*["\'](https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))["\']',
            r'file\s*:\s*["\'](https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))["\']',
            r'video_source\s*:\s*["\'](https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))["\']',
        ]

        try:
            for script in soup.find_all("script"):
                script_string = script.string  # type: ignore
                print(script_string)
                if script_string:
                    for pattern in video_patterns:
                        matches = re.findall(pattern, script_string, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                video_sources.append(match[0])  # First group is the URL
                            else:
                                video_sources.append(match)

            for meta in soup.find_all("meta"):
                meta_attrs = meta.attrs  # type: ignore
                if "content" in meta_attrs:
                    content = str(meta_attrs["content"])
                    for pattern in video_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                video_sources.append(match[0])
                            else:
                                video_sources.append(match)

            for video in soup.find_all("video"):
                video_attrs = video.attrs  # type: ignore
                if "src" in video_attrs:
                    video_sources.append(video_attrs["src"])
                for source in video.find_all("source"):  # type: ignore
                    source_attrs = source.attrs  # type: ignore
                    if "src" in source_attrs:
                        video_sources.append(source_attrs["src"])

            # Remove duplicates while preserving order
            seen = set()
            unique_sources = []
            for url in video_sources:
                if url not in seen:
                    seen.add(url)
                    unique_sources.append(url)

            return unique_sources
        except:
            return None
