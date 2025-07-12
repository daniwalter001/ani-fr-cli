from providers.anime_ultra import AnimeUltra
from util.functions import clear, play_with_iina
from util.services import extract
from util.fzf_handler import fuzzy_finder


def handle(anime_selected: dict):
    animeu = AnimeUltra()
    while True:
        try:
            if not anime_selected:
                clear()
                continue

            titles = [x["title"] for x in anime_selected["titles"]]

            anime_search_results = animeu.fetch(
                anime_selected["title"],
                type=anime_selected["type"],
                extra_titles=titles,
            )

            if not anime_search_results:
                clear()
                continue

            if not anime_search_results:
                clear()
                continue

            choice = fuzzy_finder(
                [x["title"] for x in anime_search_results],
                prompt="Select suitable version:",
            )

            anime_fetched = anime_search_results[choice]

            if not anime_fetched:
                clear()
                continue

            eps, sources = animeu.fetch_eps(anime_fetched["id"])

            if not eps:
                clear()
                continue

            while True:
                try:
                    choice = fuzzy_finder(
                        [x["full_title"] for x in eps],
                        prompt="Select episode:",
                    )

                    if choice == False and choice != 0:
                        clear()
                        break

                    ep_selected = eps[choice]

                    if not ep_selected:
                        clear()
                        continue

                    servers = animeu.fetch_servers(ep_selected["url"])

                    if not servers:
                        clear()
                        continue

                    while True:
                        try:

                            # print(servers)
                            choice = fuzzy_finder(
                                [
                                    f"{x["server"]}. {x["title"]} - {sources[x["source-id"]]}"
                                    for x in servers
                                ],
                                prompt="Select server:",
                            )

                            server = servers[choice]

                            if not server:
                                clear()
                                break

                            server["content"] = animeu.generate_embed_url(
                                server["server"],
                                sources[server["source-id"]],
                            )

                            url_response = extract(
                                server["content"],
                                referer=ep_selected["url"],
                            )

                            if not url_response or "url" not in url_response:
                                clear()
                                continue

                            play_with_iina(
                                url=url_response["url"],
                                referer=url_response["referer"],
                            )

                        except KeyboardInterrupt as e:
                            print(e)
                            clear()
                            break
                        except Exception as e:
                            print(e)
                            input("Press Enter to continue...Exception")
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
            print(e)
            input("stop...")
            clear()
            continue
