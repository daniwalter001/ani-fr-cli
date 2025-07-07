import re
import requests


class OneUpload:

    keywords = ["oneupload", "vidmoly"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "referer": "https://oneupload.com/",
    }

    @staticmethod
    def match(url: str):
        match = any(keyword in url for keyword in OneUpload.keywords)
        return match

    @staticmethod
    def fetch(url: str, referer=None):

        print(url)
        input("stop...")
        try:

            if referer:
                OneUpload.headers["referer"] = referer

            response = requests.get(url, headers=OneUpload.headers, timeout=10)
            return response.text
        except:
            return False

    @staticmethod
    def extract(url: str, referer=None):

        pattern = r'jwplayer\("vplayer"\)\.setup\(\s*{([^}]+)}'

        html_content = OneUpload.fetch(url, referer)
        if not html_content:
            return None

        match = re.search(pattern, html_content, re.DOTALL)

        print(match)

        if not match:
            return None

        config_block = match.group(1)

        # Recherche de l'URL dans les sources
        url_pattern = r'file\s*:\s*"([^"]+)"'
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

        return None


# # Exemple d'utilisation
if __name__ == "__main__":

    video_url = OneUpload.extract(
        "https://vidmoly.to/embed-nh7zisu5fagw.html", referer="https://vidmoly.to/"
    )
    if video_url:
        print("URL source trouvée:")
        print(video_url)
    else:
        print("Aucune URL source trouvée")
