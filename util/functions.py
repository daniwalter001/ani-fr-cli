import os


def clear():
    os.system("cls" if os.name == "nt" else "clear")
    print("\033c", end="")


def exit():
    clear()
    exit()
