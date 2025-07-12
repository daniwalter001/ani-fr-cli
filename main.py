from providers.hianime import HiAnime
from providers.anime_ultra import AnimeUltra

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

                if not anime_selected:
                    clear()
                    continue

                titles = [x["title"] for x in anime_selected["titles"]]

                # vostfree

                anime_search_results = animeu.fetch(
                    anime_selected["title"],
                    type=anime_selected["type"],
                    extra_titles=titles,
                )

                # with open("anime_search_results.json", "w") as f:
                #     f.write(str(anime_search_results))

                if not anime_search_results:
                    clear()
                    continue

                # search_results = animeu.fetch_eps(anime_search_results["id"])

                if not anime_search_results:
                    clear()
                    continue
                while True:
                    try:
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

                                        if (
                                            not url_response
                                            or "url" not in url_response
                                        ):
                                            clear()
                                            continue

                                        # print("============================")
                                        # print(url_response)
                                        # print("============================")
                                        # input("Press Enter to continue...")

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
                        clear()
                        continue

            except KeyboardInterrupt as e:
                clear()
                break
            except Exception as e:
                clear()
                continue

    ##vostfree
    except KeyboardInterrupt as e:
        clear()
        continue
clear()
