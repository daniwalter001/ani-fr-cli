import os
import re
from extractors.oneupload import OneUpload
from extractors.sendvid import SendVid
from extractors.sibnet import Sibnet
from extractors.vidmoly import Vidmoly
from extractors.smoothpre import Smoothpre


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
    if "anime-sama" in url:
        return {"url": url, "referer": referer}
    elif SendVid.match(url):
        return SendVid.extract(url, referer)
    elif Sibnet.match(url):
        return Sibnet.extract(url, referer)
    elif Vidmoly.match(url):
        return Vidmoly.extract(url, referer=referer)
    elif Smoothpre.match(url):
        return Smoothpre.extract(url, referer=referer)
    else:
        return {"url": url, "referer": referer}


def stop(text: str = ""):
    input(text or "Press Enter to continue...")


def play_with_iina(url: str = "", referer: str = ""):

    if not url:
        return

    try:
        kill_all_process("iina")
        os.system(f"iina --referer='{referer}' '{url}'")
        input("Press Enter to continue...")

    except Exception as e:
        print(e)
        input("Press Enter to continue...")


def play_with_mpv(url: str = "", referrer: str = ""):

    if not url:
        return

    mpv_command = [
        "mpv",
        "--hwdec=auto-safe",
        "--vo=gpu",
        f"--referrer='{referrer}'",
        "--no-border",
        f"'{url}'",
        "--profile=fast",
        "--hwdec=auto",
    ]

    try:
        kill_all_process("mpv")
        os.system(" ".join(mpv_command))
        input("Press Enter to continue...")

    except Exception as e:
        print(f"MPV failed: {e}")
        input("Press Enter to continue...")


def kill_all_process(process_name=""):

    if not process_name:
        return

    # pgrep -i IINA | xargs kill -9
    os.system(f"pgrep -i '{process_name}' | xargs kill -9")

    os.system(f"pkill -i {process_name}")
