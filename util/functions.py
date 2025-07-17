import os
import re
import html
from urllib.parse import unquote


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


def stop(text: str = ""):
    input(text or "Press Enter to continue...")


def play_with_iina(url: str = "", referer: str = "", title=""):

    if not url:
        return

    try:
        kill_all_process("iina")
        os.system(
            f"iina --referer='{referer}' --mpv-force-media-title='{title}' '{url}'"
        )

    except Exception as e:
        print(e)
        input("Press Enter to continue...")


def play_with_mpv(url: str = "", referer: str = "", title=""):

    if not url:
        return

    mpv_command = [
        "mpv",
        "--hwdec=auto-safe",
        "--vo=gpu",
        "--no-border",
        f"'{remove_special_chars(url)}'",
        # "--profile=fast",
        "--hwdec=auto",
    ]
    if referer:
        mpv_command.extend([f"--referrer='{referer}'"])

    if title:
        mpv_command.extend(
            [f"--force-media-title='{title}'", f"--term-status-msg='Title: {title}'"]
        )

    # mpv_command.extend(
    #     ["--cache=yes", "--demuxer-max-bytes=500MiB", "--demuxer-max-back-bytes=100MiB"]
    # )

    # print(" ".join(mpv_command))

    try:
        kill_all_process("mpv")
        os.system(" ".join(mpv_command))

    except Exception as e:
        print(f"MPV failed: {e}")
        input("Error: Press Enter to continue...")


def kill_all_process(process_name=""):

    if not process_name:
        return

    # pgrep -i IINA | xargs kill -9
    os.system(f"pgrep -i '{process_name}' | xargs kill -9")

    os.system(f"pkill -i {process_name}")


def remove_special_chars(text: str):

    try:
        decoded_text = re.sub(
            r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text
        )

        decoded_text = decoded_text.replace("\u00a0", " ")

        decoded_text = html.unescape(decoded_text)

        decoded_text = re.sub(r"\s+", " ", decoded_text)
        decoded_text = re.sub(r":\/+", "://", decoded_text, flags=re.MULTILINE)

        return decoded_text
    except Exception as e:
        return text


def decode_url_unicode(url):
    # Remplace les \u0026 par %u0026 pour urllib.parse.unquote
    corrected_url = re.sub(r"\\u([0-9a-fA-F]{4})", r"%u\1", url)
    # Décodage des séquences Unicode (%uXXXX)
    decoded_url = unquote(corrected_url)
    return decoded_url


def remove_duplicates(list: list, key="title"):
    unique_list = []
    for item in list:
        if item[key] not in [x[key] for x in unique_list]:
            unique_list.append(item)
    return unique_list
