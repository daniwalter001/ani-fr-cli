import os


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
    return None
