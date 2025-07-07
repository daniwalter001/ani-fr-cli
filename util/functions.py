import os
import re
from extractors.oneupload import OneUpload
from extractors.sendvid import SendVid
from extractors.sibnet import Sibnet
from extractors.vidmoly import Vidmoly


def clear():
    os.system("cls" if os.name == "nt" else "clear")
    print("\033c", end="")


def exit():
    clear()
    exit()


def check_anime(anime: list, search_results: list):
    for result in search_results:
        if result["title"] in anime:
            return result

        cleaned_anime = [a.replace(":", "").replace("-", " ") for a in anime]
        cleaned_result = result["title"].replace(":", "").replace("-", " ")

        if cleaned_result in cleaned_anime:
            return result

    return None


def join_path(paths: list):
    args = [i for i in paths if i]
    return os.path.join(*args)


def extract_links(text):

    url_pattern = r"https?://[^\s\'\"]+"

    # Find all matches in the text
    urls = re.findall(url_pattern, text)

    return urls


def extract(url: str, referer: str = ""):
    if not url:
        return None

    if OneUpload.match(url):
        return OneUpload.extract(url, referer)
    elif SendVid.match(url):
        return SendVid.extract(url, referer)
    elif Sibnet.match(url):
        return Sibnet.extract(url)
    elif Vidmoly.match(url):
        return Vidmoly.extract(url)
    else:
        return url


def stop(text: str = ""):
    input(text or "Press Enter to continue...")
