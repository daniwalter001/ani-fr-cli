from providers.hianime import HiAnime
from providers.anime_ultra import AnimeUltra

from util.fzf_handler import fuzzy_finder
from util.functions import clear
from util.functions import play_with_mpv, play_with_iina
from util.services import extract

from providers.mal import MyAnimeList

from urllib import parse


hianime = HiAnime()
mal = MyAnimeList()
animeu = AnimeUltra()


while True:

    try:

        choice = fuzzy_finder(["continue", "quit"], prompt="WDYW?")

        if choice == 1:
            clear()
            break

        anime = input("Anime: ")

        if not anime:
            clear()
            break

        search_results = mal.search(anime)

        if not search_results:
            clear()
            continue

        choice = fuzzy_finder(
            [x["title"] for x in search_results],
            prompt="Select anime:",
        )

        if choice == False and choice != 0:
            clear()
            break

        anime_selected = search_results[choice]

        if not anime_selected:
            clear()
            continue

        titles = [x["title"] for x in anime_selected["titles"]]

        # vostfree

        anime_search_results = animeu.fetch(
            anime_selected["title"], type=anime_selected["type"], extra_titles=titles
        )

        print(anime_search_results)
        
        with open("anime_search_results.json", "w") as f:
            f.write(str(anime_search_results))

        input("Press Enter to continue...")

    ##vostfree
    except KeyboardInterrupt as e:
        clear()
        continue
clear()
