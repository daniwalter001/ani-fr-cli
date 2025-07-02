import json
import re
from typing import List, Dict, Tuple, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64


class MegaCloudExtractor:
    SERVER_URL = ["https://megacloud.blog", "https://rapid-cloud.co"]
    SOURCES_URL = [
        # "/embed-2/ajax/e-1/getSources?id=",
        "/embed-2/v2/e-1/getSources?id=",
        "/ajax/embed-6-v2/getSources?id=",
    ]
    SOURCES_SPLITTER = ["/e-1/", "/embed-6-v2/"]
    SOURCES_KEY = ["1", "6"]
    E1_SCRIPT_URL = "https://megacloud.blog/js/player/a/prod/e1-player.min.js"
    E6_SCRIPT_URL = "https://rapid-cloud.co/js/player/prod/e6-player-v2.min.js"

    _mutex = Lock()
    _should_update_key = False
    _pref_key_prefix = "megacloud_key_"
    _pref_key_default = "[[0, 0]]"

    def __init__(self, session: requests.Session, headers: dict, preferences: dict):
        self.session = session
        self.headers = headers
        self.preferences = preferences
        self.no_cache_session = requests.Session()
        self.no_cache_session.mount("https://", HTTPAdapter(max_retries=3))

    def _run_locked(self, func):
        with self._mutex:
            return func()

    def _get_key(self, key_type: str) -> List[List[int]]:
        def inner():
            if self._should_update_key:
                self._update_key(key_type)
                self._should_update_key = False
            pref_key = self._pref_key_prefix + key_type
            return json.loads(self.preferences.get(pref_key, self._pref_key_default))

        return self._run_locked(inner)

    def _update_key(self, key_type: str):
        script_url = self.E1_SCRIPT_URL if key_type == "1" else self.E6_SCRIPT_URL
        response = self.no_cache_session.get(script_url, headers=self.headers)
        script = response.text

        regex = re.compile(
            r"case\s*0x[0-9a-f]+:(?![^;]*=partKey)\s*\w+\s*=\s*(\w+)\s*,\s*\w+\s*=\s*(\w+);"
        )
        matches = list(regex.finditer(script))

        index_pairs = []
        for match in matches:
            var1, var2 = match.groups()

            regex_var1 = re.compile(rf",{var1}=((?:0x)?([0-9a-fA-F]+))")
            regex_var2 = re.compile(rf",{var2}=((?:0x)?([0-9a-fA-F]+))")

            match_var1 = regex_var1.search(script)
            match_var2 = regex_var2.search(script)

            if match_var1 and match_var2:
                val1 = match_var1.group(1).lstrip("0x")
                val2 = match_var2.group(1).lstrip("0x")
                try:
                    index_pairs.append([int(val1, 16), int(val2, 16)])
                except ValueError:
                    continue

        pref_key = self._pref_key_prefix + key_type
        self.preferences[pref_key] = json.dumps(index_pairs)

    def _cipher_text_cleaner(self, data: str, key_type: str) -> Tuple[str, str]:
        index_pairs = self._get_key(key_type)
        password = ""
        ciphertext = data
        offset = 0
        
        
        print(index_pairs)

        for pair in index_pairs:
            start = pair[0] + offset
            end = start + pair[1]
            print(start, end)
            pass_substr = data[start:end]
            print(pass_substr)
            password += pass_substr
            ciphertext = ciphertext.replace(pass_substr, "", 1)
            offset += pair[1]

        return ciphertext, password

    def _try_decrypting(self, ciphered: str, key_type: str, attempts: int = 0) -> str:
        if attempts > 2:
            raise Exception("Decryption failed after multiple attempts")

        ciphertext, password = self._cipher_text_cleaner(ciphered, key_type)
        
        print("ciphertext, password")
        print([ciphertext, password])
        
        decrypted = self._decrypt_aes(ciphertext, password)

        if not decrypted:
            self._should_update_key = True
            return self._try_decrypting(ciphered, key_type, attempts + 1)
        return decrypted

    def _decrypt_aes(self, ciphertext: str, key: str) -> str:
        try:
            key = key.encode("utf-8")  # type: ignore
            iv = key[:16]  # First 16 bytes as IV
            ciphertext = base64.b64decode(ciphertext)  # type: ignore
            cipher = AES.new(key, AES.MODE_CBC, iv)  # type: ignore
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            return decrypted.decode("utf-8")
        except Exception as e:
            return ""

    def get_videos_from_url(self, url: str, type: str, name: str) -> List[dict]:
        video = self._get_video_dto(url)
        master_url = video["sources"][0]["file"]

        subs = []
        if "tracks" in video:
            subs = [
                {"url": t["file"], "label": t.get("label", "")}
                for t in video["tracks"]
                if t.get("kind") == "captions"
            ]

        # You'll need to implement HLS extraction similar to PlaylistUtils
        return self._extract_from_hls(master_url, name, type, subs, url)

    def _get_video_dto(self, url: str) -> dict:
        print(url)
        type_idx = 0 if "megacloud.blog" in url else 1
        key_type = self.SOURCES_KEY[type_idx]

        splitter = self.SOURCES_SPLITTER[type_idx]
        id_start = url.find(splitter) + len(splitter)
        id_end = url.find("?", id_start)
        video_id = url[id_start : id_end if id_end != -1 else None]
        if not video_id:
            raise Exception("Invalid URL format")

        api_url = self.SERVER_URL[type_idx] + self.SOURCES_URL[type_idx] + video_id
        print(api_url)
        response = self.session.get(api_url, headers=self.headers)
        print(response.status_code)
        data = response.json()

        if not data.get("encrypted", True):
            return data

        ciphered = data["sources"]
        print(ciphered)

        if isinstance(ciphered, dict):
            ciphered = ciphered.get("__json_encoded", "") or json.dumps(ciphered)

        decrypted = self._try_decrypting(ciphered, key_type)
        return {"sources": json.loads(decrypted), "tracks": data.get("tracks")}

    def _extract_from_hls(
        self, master_url: str, name: str, type: str, subs: list, referer: str
    ) -> List[dict]:
        # Implement your HLS stream extraction logic here
        # This should return a list of video quality options
        return []


if __name__ == "__main__":
    session = requests.Session()
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://aniwatch.tv/",
    }
    extractor = MegaCloudExtractor(session=session, headers={}, preferences={})
    extractor.get_videos_from_url(
        "https://megacloud.blog/embed-2/v2/e-1/uZpOunTDPw90?k=1", "mp4", "test"
    )
