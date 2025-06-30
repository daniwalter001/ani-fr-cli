import requests
import time
import re


class MegaCloud:

    script = "https://megacloud.tv/js/player/a/v2/pro/embed-1.min.js?v="
    sources = "https://megacloud.blog/embed-2/v2/e-1/getSources?id="

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36",
            "referer": "https://hianime.to/",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
        }

    def parse(self, url="https://megacloud.blog/embed-2/v2/e-1/WQbjlJtGrC1S?k=1"):
        video_id = url.split("/").pop().split("?")[0]

        extractedDatas = {}

        self.headers["Referer"] = url

        response = requests.get(
            self.sources + video_id, headers=self.headers, timeout=10
        )

        if not response or response.status_code != 200:
            return False

        json_response = response.json()

        print(json_response)

        if not json_response or "sources" not in json_response:
            return False

        sources = json_response["sources"]

        if not sources:
            return False

        if not json_response.encrypted and json_response["sources"] is list:
            extractedDatas["intro"] = json_response["intro"]
            extractedDatas["outro"] = json_response["outro"]
            extractedDatas["tracks"] = json_response["tracks"]
            extractedDatas["sources"] = [
                {"url": x["file"], "type": x["type"]} for x in json_response["sources"]
            ]
            return extractedDatas

        data = requests.get(
            self.script + str(time.time()), headers=self.headers, timeout=10
        ).text

        if not data:
            return False

        vars = self.extract_variables(data)

        if not vars:
            return False

        secret, encryped_source = self.get_secret(str(sources), vars)

    def get_secret(self, encrypted: str, vars: list):
        secret = ""
        encrypted_source = ""
        encrypted_source_array = encrypted.split("")
        c_index = 0

        for index in vars:
            start = index[0] + c_index
            end = index[1] + start

            for i in range(start, end):
                secret += encrypted[i]
                encrypted_source_array[i] = ""
            c_index += index[1]

        encrypted_source = "".join(encrypted_source_array)

        return secret, encrypted_source

    def extract_variables(self, data: str):
        pattern = r"case\s*0x[0-9a-f]+:(?![^;]*=partKey)\s*\w+\s*=\s*(\w+)\s*,\s*\w+\s*=\s*(\w+);"
        matches = re.match(pattern, data, flags=re.MULTILINE)

        print(matches)

        if not matches:
            return []

        def parse_matching_key(match):
            m1 = self.macthing_key(match.group(1), data)
            m2 = self.macthing_key(match.group(2), data)

            if not m1 or not m2:
                return []

            try:
                return [int(m1, 16), int(m2, 16)]
            except:
                return []

        vars = [parse_matching_key(match) for match in matches if match]

        print(vars)

        return vars

    def macthing_key(self, value: str, script: str):
        pattern = f"{value}=((?:0x)?([0-9a-fA-F]+))"
        regex = re.compile(pattern, flags=re.MULTILINE)
        match = regex.match(script)

        if match:
            return match.group(1).replace("0x", "")
        return None
