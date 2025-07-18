from providers.anime_ultra import AnimeUltra
from util.functions import clear, play_with_iina, play_with_mpv
from util.services import extract
from util.fzf_handler import fuzzy_finder

animeu = AnimeUltra()

anime_object = {}


def handle(anime_selected: dict):
    try:
        if not anime_selected:
            clear()
            return

        titles = [x["title"] for x in anime_selected["titles"]]

        anime_search_results = animeu.fetch(
            anime_selected["title"],
            type=anime_selected["type"],
            extra_titles=titles,
        )

        if not anime_search_results:
            clear()
            return

        while True:
            choice = fuzzy_finder(
                [x["title"] for x in anime_search_results],
                prompt="Select suitable version:",
            )

            anime_fetched = anime_search_results[choice]
            anime_object["title"] = anime_fetched["title"]

            print(f"Title: {anime_fetched['title']}")

            handle_version(anime_fetched)

    except KeyboardInterrupt as e:
        clear()
        return
    except Exception as e:
        print(e)
        input("stop...")
        clear()
        return


def handle_version(anime_fetched: dict):
    try:
        if not anime_fetched:
            clear()
            return

        eps, sources = animeu.fetch_eps(anime_fetched["id"])

        if not eps:
            clear()
            return

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

                anime_object["episode"] = ep_selected

                handle_ep(ep_selected, sources, choice, eps)

            except KeyboardInterrupt as e:
                clear()
                break
            except Exception as e:
                clear()
                continue

    except Exception as e:
        print(e)
        input("...stop...")


def handle_ep(ep_selected: dict, sources: dict, current_ep_order: int, eps: list):

    _current_ep_order = current_ep_order

    if (not _current_ep_order and _current_ep_order != 0) or _current_ep_order >= len(
        eps
    ):
        _current_ep_order = 0

    auto_play = True

    try:
        if not ep_selected:
            clear()
            return

        servers = animeu.fetch_servers(ep_selected["url"])

        if not servers or len(servers) == 0:
            clear()
            return

        while True:

            if auto_play:
                anime_object["servers"] = servers
                handle_source(servers[0], sources, ep_selected["url"])
                auto_play = False

            try:
                actions = [
                    "play",
                    "next",
                    "change episode",
                    "change source",
                    "quit",
                ]

                choice = fuzzy_finder(
                    [f"{x}" for x in actions],
                    prompt="Wtdo ?:",
                )
                action = actions[choice]

                if action == "play":
                    anime_object["servers"] = servers
                    handle_source(servers[0], sources, ep_selected["url"])

                elif action == "next":
                    if _current_ep_order >= len(eps):
                        _current_ep_order = 0
                    _current_ep_order += 1
                    ep_selected = eps[_current_ep_order]
                    servers = animeu.fetch_servers(ep_selected["url"])
                    anime_object["servers"] = servers
                    anime_object["episode"] = ep_selected
                    handle_source(servers[0], sources, ep_selected["url"])
                    continue

                elif action == "change episode":
                    clear()
                    break

                elif action == "change source":
                    clear()
                    choice = fuzzy_finder(
                        [
                            f'{x["server"]}. {x["title"]} - {sources[x["source-id"]]}'
                            for x in servers
                        ],
                        prompt="Select server:",
                    )

                    server = servers[choice]

                    if not server:
                        clear()
                        break
                    anime_object["server"] = server

                    handle_source(server, sources, ep_selected["url"])

                    continue

                elif action == "quit":
                    clear()
                    break

            except KeyboardInterrupt as e:
                print(e)
                clear()
                break
            except Exception as e:
                print(e)
                input("Press Enter to continue...Exception")
                clear()
                continue

    except Exception as e:
        print(e)
        clear()
        return


def handle_source(server: dict, sources: dict, referer: str):

    try:
        server["content"] = animeu.generate_embed_url(
            server["server"],
            sources[server["source-id"]],
        )

        url_response = extract(server["content"], referer=referer)

        if not url_response or "url" not in url_response:
            clear()
            return

        print(
            f"Real URL: { "found" if url_response and "url" in url_response else "not found"} "
        )

        title = f"{anime_object['title']} - {anime_object['episode']['full_title']}"

        play_with_mpv(
            url=url_response["url"],
            referer=str(url_response["referer"] or referer),
            title=title,
        )

    except:
        clear()
        return
