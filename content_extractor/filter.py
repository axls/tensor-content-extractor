from content_extractor.rules import Rules


class Filter:
    def __init__(self):
        self._rules = Rules()
        self._rules.load()

    def exclude(self, host: str, tag: str, attrs: list) -> bool:
        return self._rules.exclude(host, tag, attrs)

    def exclude2(self, tag: str, attrs: list) -> bool:
        if tag == "header":
            return True
        attrs_dict = dict(attrs)
        class_names = (attrs_dict["class"] if "class" in attrs_dict else "").lower().split()
        for cls in class_names:
            if "nav" == cls:
                return True
            if "footer" == cls:
                return True
            if cls.startswith("banner"):
                return True
            if cls.startswith("topline"):
                return True
            if cls.startswith("live-tv"):
                return True
            if "social" in cls:
                return True
            if "begun" in cls:
                return True
            if "yandex" in cls:
                return True
            if "google" in cls:
                return True
            if "feed" in cls:
                return True
            if "news" in cls:
                return True
            if "anons" in cls:
                return True
            if "tabs" in cls:
                return True
            if "footer" in cls:
                return True
            if "load" in cls:
                return True
            if "error" in cls:
                return True
            if "support" in cls:
                return True
            if "feedback" in cls:
                return True
        return False
