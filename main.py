from providers.hianime import HiAnime

import controllers.anime_sama as asama
import controllers.anime_ultra as aultra

from util.fzf_handler import fuzzy_finder
from util.functions import clear
from util.functions import (
    play_with_mpv,
    play_with_iina,
    remove_special_chars,
    decode_url_unicode,
)
from util.services import extract

from providers.mal import MyAnimeList


mal = MyAnimeList()


while True:

    try:

        choice = fuzzy_finder(["search", "quit", "trending"], prompt="WDYW?")

        if choice != 0:
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

        while True:
            try:
                choice = fuzzy_finder(
                    [x["title"] for x in search_results],
                    prompt="Select anime:",
                )

                if choice == False and choice != 0:
                    clear()
                    break

                anime_selected = search_results[choice]

                providers = ["AnimeSama", "AnimeUltra"]

                while True:
                    try:
                        choice = fuzzy_finder(
                            [x for x in providers],
                            prompt="Select provider:",
                        )

                        if choice == False and choice != 0:
                            clear()
                            continue

                        if choice == 0:
                            asama.handle(anime_selected)
                        elif choice == 1:
                            aultra.handle(anime_selected)
                        else:
                            clear()
                            continue

                    except KeyboardInterrupt as e:
                        clear()
                        break
                    except Exception as e:
                        clear()
                        continue

            except KeyboardInterrupt as e:
                clear()
                break
            except Exception as e:
                clear()
                continue

    except KeyboardInterrupt as e:
        clear()
        continue
clear()
