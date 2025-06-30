class Provider:
    api_base_url: str

    def check_api(self):
        return not not self.api_base_url
