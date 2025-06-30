from providers.provider import Provider


class Kitsu(Provider):
    api_base_url = ""

    def search(self, search_term: str):
        if self.check_api():
            return False
        if not search_term:
            return []

    def by_id(self, kitsu_id: str):
        if not kitsu_id:
            return False
