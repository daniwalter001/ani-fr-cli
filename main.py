from providers.hianime import HiAnime
from util.fzf_handler import fuzzy_finder
from util.functions import clear, exit


hianime = HiAnime()


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

        search_results = hianime.search(anime)

        search_results.reverse()

        choice = fuzzy_finder(
            [x["title"] for x in search_results],
            prompt="Select anime:",
        )

        if not choice:
            clear()
            break

        eps = hianime.fetch_eps(search_results[choice]["id"])

        eps.reverse()

        choice = fuzzy_finder(
            [f"{x['order']}. {x['title']}" for x in eps],
            prompt="Select episode:",
        )

        if not choice:
            clear()
            break

        servers = hianime.fetch_servers(eps[choice]["id"])

        for idx, server in enumerate(servers):
            print(f"  {idx + 1}. {server['title']} - {server['data']['link']}")

        input("")
    except Exception as e:
        clear()
        continue
clear()
