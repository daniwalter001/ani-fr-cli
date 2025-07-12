from providers.anime_sama import AnimeSama
from util.functions import clear, play_with_iina
from util.services import extract
from util.fzf_handler import fuzzy_finder


def handle(anime_selected: dict):
    animesama = AnimeSama()
    while True:
        try:
            if not anime_selected:
                clear()
                return

            if "titles" not in anime_selected:
                anime_selected["titles"] = []

            titles = [x["title"] for x in anime_selected["titles"]]

            anime_from_hianime = animesama.fetch(
                anime_selected["title"],
                extra_titles=titles,
                type=anime_selected["type"],
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

            choice = fuzzy_finder(
                [f"{x['type']}. {x['title']}" for x in saisons if x["type"] != "manga"],
                prompt="Select saison:",
            )

            season = saisons[choice]

            if not season:
                clear()
                continue

            lang_vers = animesama.switch_to_vf_or_vostfr(season)

            if not lang_vers:
                clear()
                continue

            choice = fuzzy_finder(
                [f"{x['title']}" for x in lang_vers],
                prompt="Select lang:",
            )

            season = lang_vers[choice]

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

                    choice = fuzzy_finder([x for x in sources], prompt="Select souces:")

                    source = sources[choice]

                    if not source:
                        clear()
                        continue

                    real_link = extract(source, referer=season["link"])

                    print(
                        f"Real URL: { "found" if real_link and "url" in real_link else "not found"} "
                    )

                    if (
                        not real_link
                        or "url" not in real_link
                        or "referer" not in real_link
                    ):
                        clear()
                        continue

                    play_with_iina(str(real_link["url"]), str(season["link"]))
                    # play_with_iina(str(real_link["url"]), str(real_link["referer"]))

                    input("\nPress Enter to continue...")

                except KeyboardInterrupt as e:
                    clear()
                    break
                except Exception as e:
                    print(e)
                    input("stop...")
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
