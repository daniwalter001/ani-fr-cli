from providers.anime_sama import AnimeSama
from util.functions import clear, play_with_iina, play_with_mpv
from util.services import extract
from util.fzf_handler import fuzzy_finder


anime_object = {}
animesama = AnimeSama()


def handle(anime_selected: dict):
    try:
        if not anime_selected:
            clear()
            return

        if "titles" not in anime_selected:
            anime_selected["titles"] = []

        titles = [x["title"] for x in anime_selected["titles"]]

        animes = animesama.fetch(
            anime_selected["title"],
            extra_titles=titles,
            type=anime_selected["type"],
        )

        if not animes:
            clear()
            return

        print(f"Title: {animes["title"]}, Type: {animes["type"]}")

        anime_object["title"] = animes["title"]
        anime_object["type"] = animes["type"]

        saisons = animesama.fetch_saisons(animes["url"])

        if not saisons:
            clear()
            return
        while True:

            choice = fuzzy_finder(
                [f"{x['type']}. {x['title']}" for x in saisons if x["type"] != "manga"],
                prompt="Select saison:",
            )
            season = saisons[choice]
            handle_season(season)

    except KeyboardInterrupt as e:
        clear()
        return
    except Exception as e:
        print(e)
        input("stop...")
        clear()
        return


def handle_season(season: dict):
    try:
        if not season:
            clear()
            return

        lang_vers = animesama.switch_to_vf_or_vostfr(season)

        if not lang_vers:
            clear()
            return

        while True:
            try:

                choice = fuzzy_finder(
                    [f"{x['title']}" for x in lang_vers],
                    prompt="Select lang:",
                )

                season = lang_vers[choice]
                anime_object["season"] = season

                eps = animesama.fetch_eps(season_url=season["link"])

                if not eps:
                    clear()
                    return

                while True:
                    try:

                        choice = fuzzy_finder(
                            [f"Episode. {x['episode']}" for x in eps],
                            prompt="Select eps:",
                        )

                        ep = eps[choice]

                        current_episode_order = choice

                        handle_eps(
                            ep,
                            referer=season["link"],
                            current_episode_order=current_episode_order,
                            eps=eps,
                        )
                    except KeyboardInterrupt as e:
                        clear()
                        break
                    except Exception as e:
                        print(e)
                        input("stop...")
                        clear()
                        continue

            except KeyboardInterrupt as e:
                break
            except Exception as e:
                print(e)
                input("stop...")
                clear()
                continue
    except Exception as e:
        return


def handle_eps(ep: dict, referer: str, current_episode_order: int, eps: list):
    _current_episode_order = current_episode_order

    if (
        not _current_episode_order and _current_episode_order != 0
    ) or _current_episode_order >= len(eps):
        _current_episode_order = 0

    auto_play = True
    try:
        if not ep:
            clear()
            return

        anime_object["episode"] = eps[_current_episode_order]

        # print(f"_current_episode_order, {_current_episode_order}")
        # print(f"eppp, {eps[_current_episode_order]}")

        # input("Press Enter to continue...")

        while True:
            try:
                sources = eps[_current_episode_order]["sources"]

                if not sources:
                    clear()
                    break

                if auto_play:
                    handle_sources(sources[0], referer)
                    auto_play = False
                    continue

                actions = [
                    "play",
                    "next",
                    "change episode",
                    "change source",
                    "quit",
                ]

                choice = fuzzy_finder([x for x in actions], prompt="What to do? ")

                action = actions[choice]

                if action == "play":
                    handle_sources(sources[_current_episode_order], referer)
                    continue

                if action == "next":
                    if _current_episode_order >= len(eps):
                        _current_episode_order = 0
                    _current_episode_order = _current_episode_order + 1
                    sources = eps[_current_episode_order]["sources"]
                    anime_object["episode"] = eps[_current_episode_order]
                    handle_sources(sources[0], referer)
                    continue

                if action == "quit":
                    clear()
                    break

                if action == "change episode":
                    clear()
                    break

                if action == "change source":
                    choice = fuzzy_finder([x for x in sources], prompt="Select souces:")
                    source = sources[choice]
                    anime_object["source"] = source
                    handle_sources(source, referer)

            except KeyboardInterrupt as e:
                clear()
                break
            except Exception as e:
                print(e)
                input("stop...")
                clear()
                continue

    except Exception as e:
        print(e)
        input("stop...")
        clear()
        return


def handle_sources(source: str, referer: str):

    try:

        if not source:
            clear()
            return

        real_link = extract(source, referer=referer)

        print(
            f"Real URL: { "found" if real_link and "url" in real_link else "not found"} "
        )

        if not real_link or "url" not in real_link or "referer" not in real_link:
            clear()
            return

        anime_object["stream_link"] = real_link

        title = f"{anime_object['title']} - {anime_object['season']['title']} - {anime_object['episode']['episode']}"

        #
        play_with_mpv(
            str(real_link["url"]), str(real_link["referer"] or referer), title=title
        )

        input("\nPress Enter to continue...")

    except Exception as e:
        return
