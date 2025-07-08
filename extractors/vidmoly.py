import re
import requests


class Vidmoly:

    keywords = ["vidmoly"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://vidmoly.to",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in Vidmoly.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):
        try:
            if referer:
                Vidmoly.headers["referer"] = referer

            response = requests.get(url, headers=Vidmoly.headers, timeout=10)
            return response.text
        except Exception as e:
            print(e)
            input("stop...erreur")
            return False

    @staticmethod
    def extract(url: str, referer=None):

        pattern = r"player\.setup\(\s*{[\s\S]*?sources:\s*\[({[\s\S]*?})\][\s\S]*?}\)"

        html_content = Vidmoly.fetch(url, referer)

        if not html_content:
            return None

        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            return None

        config_block = match.group(1)

        # Recherche de l'URL dans les sources
        url_pattern = r'file\s*:\s*["\'](https?://[^\s"\']+)["\']'
        url_match = re.search(url_pattern, config_block)

        if url_match:
            return {"url": url_match.group(1), "referer": url}

        # Alternative pour les sources HLS
        sources_pattern = r"sources\s*:\s*\[([^\]]+)\]"
        sources_match = re.search(sources_pattern, config_block)

        if sources_match:
            sources_block = sources_match.group(1)
            file_pattern = r'file\s*:\s*"([^"]+)"'
            file_match = re.search(file_pattern, sources_block)
            if file_match:
                return {"url": file_match.group(1), "referer": url}

        # If not found in JWPlayer config, look for common video URL patterns
        video_patterns = [
            r'(https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))',
            r'src\s*:\s*["\'](https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))["\']',
            r'file\s*:\s*["\'](https?://[^\s"\']+\.(mp4|webm|ogg|mov|m3u8))["\']',
        ]

        for pattern in video_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                # Return the first match (first group if it's a tuple)
                match = matches[0]
                return (
                    {"url": match[0], "referer": url}
                    if isinstance(match, tuple)
                    else {"url": match, "referer": url}
                )

        return None
