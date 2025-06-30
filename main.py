from providers.hianime import HiAnime
from util.fzf_handler import fuzzy_finder
from util.functions import clear


hianime = HiAnime()

while True:

    choice = fuzzy_finder(["continue", "quit"], prompt="WDYW?")

    if choice == 1:
        clear()
        break

    anime = input("Anime: ")

    if not anime:
        clear()
        break

    search_results = hianime.search(anime)

    choice = fuzzy_finder([x["title"] for x in search_results], prompt="Select anime:")

    eps = hianime.fetch_eps(search_results[choice]["id"])

    choice = fuzzy_finder(
        [f"{x['order']}. {x['title']}" for x in eps], prompt="Select episode:"
    )

    servers = hianime.fetch_servers(eps[choice]["id"])

    for idx, server in enumerate(servers):
        print(f"  {idx + 1}. {server['title']} - {server['data']['link']}")


clear()