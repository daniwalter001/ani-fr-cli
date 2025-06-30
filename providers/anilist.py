from providers.provider import Provider


class Anilist(Provider):
    api_base_url: str

    def search(self, search_term: str):
        if self.check_api():
            return False
        if not search_term:
            return []

    def by_id(self, anilist_id: str):
        if not anilist_id:
            return False
