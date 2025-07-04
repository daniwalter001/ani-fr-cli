from providers.hianime import HiAnime
from util.fzf_handler import fuzzy_finder
from util.functions import clear
from providers.mal import MyAnimeList


hianime = HiAnime()
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

        anime_from_hianime = hianime.fetch(
            search_results[choice]["title"], extra_titles=titles
        )

        if not anime_from_hianime:
            clear()
            continue

        eps = hianime.fetch_eps(anime_from_hianime["id"])

        if not eps:
            clear()
            continue

        choice = fuzzy_finder(
            [f"{x['order']}. {x['title']}" for x in eps], prompt="Select episode:"
        )

        if not choice and choice != 0:
            clear()
            continue

        servers = hianime.fetch_servers(eps[choice]["id"])

        if not servers:
            clear()
            continue

        choice = fuzzy_finder(
            [x["title"] for x in servers],
            prompt="Select server:",
        )

        if choice == False and choice != 0:
            clear()
            continue

        hianime.fetch_server_data(servers[choice]["id"])

        input("\nstop...")

    except KeyboardInterrupt as e:
        clear()
        continue
clear()
