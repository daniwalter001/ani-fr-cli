from providers.hianime import HiAnime

hianime = HiAnime()

anime = "one piece"

search_results = hianime.search(anime)

for idx, result in enumerate(search_results):
    print(f"  {idx + 1}. {result['id']} - {result['title']}")

choice = input("Select a number: ")
choice = int(choice) - 1

eps = hianime.fetch_eps(search_results[choice]["id"])

for idx, ep in enumerate(eps):
    print(f"  {idx + 1}. {ep['title']}")

choice = input("Select a number: ")
choice = int(choice) - 1

servers = hianime.fetch_servers(eps[choice]["id"])

for idx, server in enumerate(servers):
    print(f"  {idx + 1}. {server['title']} - {server['data']['link']}")
