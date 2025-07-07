from providers.hianime import HiAnime
from providers.anime_sama import AnimeSama

from util.fzf_handler import fuzzy_finder
from util.functions import clear
from util.functions import extract

from providers.mal import MyAnimeList

from urllib import parse


hianime = HiAnime()
animesama = AnimeSama()
mal = MyAnimeList()

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

        titles = [x["title"] for x in search_results[choice]["titles"]]

        anime_from_hianime = animesama.fetch(
            search_results[choice]["title"],
            extra_titles=titles,
            type=search_results[choice]["type"],
        )

        if not anime_from_hianime:
            clear()
            continue

        print(
            f"Title: {anime_from_hianime["title"]}, Type: {anime_from_hianime["type"]}"
        )

        saisons = animesama.fetch_saisons(anime_from_hianime["url"])

        if not saisons:
            clear()
            continue

        while True:
            try:
                choice = fuzzy_finder(
                    [
                        f"{x['type']}. {x['title']}"
                        for x in saisons
                        if x["type"] != "manga"
                    ],
                    prompt="Select saison:",
                )

                season = saisons[choice]

                if not season:
                    clear()
                    continue

                eps = animesama.fetch_eps(season_url=season["link"])

                if not eps:
                    clear()
                    continue

                while True:
                    try:

                        choice = fuzzy_finder(
                            [f"Episode. {x['episode']}" for x in eps],
                            prompt="Select eps:",
                        )

                        sources = eps[choice]["sources"]

                        if not sources:
                            clear()
                            continue

                        choice = fuzzy_finder(
                            [x for x in sources], prompt="Select souces:"
                        )

                        source = sources[choice]

                        if not source:
                            clear()
                            continue

                        real_link = extract(source, referer=season["link"])

                        print("real_link: ")
                        print(real_link)

                        input("\nstop...")

                    except KeyboardInterrupt as e:
                        clear()
                        break
                    except:
                        clear()
                        continue

            except KeyboardInterrupt as e:
                clear()
                break
            except:
                clear()
                continue

    except KeyboardInterrupt as e:
        clear()
        continue
clear()
