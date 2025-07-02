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

        eps = hianime.fetch_eps(search_results[choice]["mal_id"])

        # eps = mal.get_eps_by_id(search_results[choice]["mal_id"])

        if not eps:
            clear()
            continue

        choice = fuzzy_finder(
            [f"{x['mal_id']}. {x['title']}" for x in eps],
            prompt="Select episode:",
        )

        if choice == False and choice != 0:
            clear()
            break

        servers = hianime.fetch_servers(eps[choice]["id"])

        for idx, server in enumerate(servers):
            print(f"  {idx + 1}. {server['title']} - {server['data']['link']}")

        input("")
    except KeyboardInterrupt as e:
        clear()
        continue
clear()
