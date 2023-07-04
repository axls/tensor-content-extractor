import html.parser


class HtmlParserListener:
    def on_starttag(self, tag: str, attrs: list):
        # print("START :", tag)
        pass

    def on_endtag(self, tag: str):
        # print("END   :", tag)
        pass

    def on_data(self, data: str):
        # print("data  :", data)
        pass

class _HtmlElement:
    def __init__(self, tag: str, skip_element=False):
        self.tag: str = tag
        self.skip_element: bool = skip_element


class FilteredHtmlParser(html.parser.HTMLParser):
    _void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track",
                      "wbr"}
    _tags_to_skip = {"style", "script", "head", "iframe", "textarea", "template", "title", "button", "svg"}

    def __init__(self, listener: HtmlParserListener):
        super().__init__()
        self._listener = listener
        self._skip: bool = False
        self._in_body: bool = False

    def handle_starttag(self, tag, attrs):
        if tag in FilteredHtmlParser._void_elements:
            return
        if not self._in_body:
            if tag == "body":
                self._in_body = True
            return
        if tag in FilteredHtmlParser._tags_to_skip:
            self._skip = True
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

        if tag in FilteredHtmlParser._tags_to_skip:
            self._skip = False
            return
        self._listener.on_endtag(tag)

    def handle_startendtag(self, tag, attrs):
        if tag in FilteredHtmlParser._void_elements:
            return
        # print("STAEND:", tag)
        super().handle_startendtag(tag, attrs)

    def handle_data(self, data):
        if not self._in_body:
            return
        if self._skip:
            return
        self._listener.on_data(data)
