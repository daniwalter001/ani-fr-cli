from extractors.oneupload import OneUpload
from extractors.sendvid import SendVid
from extractors.sibnet import Sibnet
from extractors.smoothpre import Smoothpre
from extractors.vidmoly import Vidmoly
from extractors.vidcn import VidCdn



def extract(url: str, referer: str = ""):
    if not url:
        return None

    if OneUpload.match(url):
        return OneUpload.extract(url, referer)
    if "anime-sama" in url:
        return {"url": url, "referer": referer}
    elif SendVid.match(url):
        return SendVid.extract(url, referer)
    elif Sibnet.match(url):
        return Sibnet.extract(url, referer)
    elif Vidmoly.match(url):
        return Vidmoly.extract(url, referer=referer)
    elif Smoothpre.match(url):
        return Smoothpre.extract(url, referer=referer)
    elif VidCdn.match(url):
        return VidCdn.extract(url, referer=referer)
    else:
        return {"url": url, "referer": referer}

