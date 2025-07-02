from iterfzf import iterfzf


def fuzzy_finder(
    options: list,
    prompt="Select an option:",
):

    selected = iterfzf(options, multi=False, prompt=prompt, ansi=True, cycle=True)

    if not selected:
        return False

    return options.index(selected)
