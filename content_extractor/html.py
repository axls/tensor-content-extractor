import html.parser


class HtmlParserListener:
    def on_starttag(self, tag: str, attrs: list):
        pass

    def on_endtag(self, tag: str):
        pass

    def on_data(self, data: str):
        pass


class FilteredHtmlParser(html.parser.HTMLParser):
    _void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track",
                      "wbr"}

    def __init__(self, listener: HtmlParserListener):
        super().__init__()
        self._listener = listener
        self._in_body: bool = False

    def handle_starttag(self, tag, attrs):
        if tag in FilteredHtmlParser._void_elements:
            return
        if not self._in_body:
            if tag == "body":
                self._in_body = True
            return
        self._listener.on_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in FilteredHtmlParser._void_elements:
            return
        if not self._in_body:
            return
        elif tag == "body":
            self._in_body = False
            return

        self._listener.on_endtag(tag)

    def handle_startendtag(self, tag, attrs):
        if tag in FilteredHtmlParser._void_elements:
            return
        super().handle_startendtag(tag, attrs)

    def handle_data(self, data):
        if not self._in_body:
            return
        self._listener.on_data(data)
