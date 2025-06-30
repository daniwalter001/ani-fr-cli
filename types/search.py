class SearchResult:
    title: str
    id: str
    image: str
    duration: str
    type: str
    description: str
    url: str

    def __init__(self, id, title, url, description, duration, image, type):
        self.id = id
        self.title = title
        self.url = url
        self.description = description
        self.type = type
        self.duration = duration
        self.image = image
