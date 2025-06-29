from bs4 import BeautifulSoup
import requests


class BeautifulScraper:
    content = ""

    def validateContent(self, content=""):
        return content

    def parse(self, _content=""):
        self.content = self.validateContent(_content)

        if not self.content:
            return False

        soup = BeautifulSoup(_content, "html.parser")

        return soup

    def fetchAndParse(self, url="", extra_headers={}):
        if not url:
            return False
        response = requests.get(url, headers=extra_headers)

        return self.parse(response.text)
