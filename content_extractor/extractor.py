import urllib.request
import urllib.parse
from collections import deque
from enum import Enum

from .rules import Rules
from .writer import TextWriter
from .html import FilteredHtmlParser, HtmlParserListener


class ContentExtractor:

    def __init__(self, rules_file_name: str = None):
        self._rules = Rules()
        self._rules.load(file_name=rules_file_name)

    def extract_from_url(self, url_text: str) -> str:
        url = urllib.parse.urlparse(url_text)
        html = self._load_by_url(url_text)
        return self._extract_from(url.hostname, html)

    def extract_from_file(self, file_name: str, encoding: str = "utf-8", host_name: str = "*") -> str:
        with open(file_name, encoding=encoding) as f:
            html = f.read()
            return self._extract_from(host_name, html)

    def _load_by_url(self, url: str) -> str:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        response_encoding = response.headers.get_content_charset(failobj="utf-8")
        return response.read().decode(response_encoding)

    def _extract_from(self, host: str, html: str) -> str:
        writer = TextWriter()
        parser = FilteredHtmlParser(_HtmlWalker(host, writer, self._rules))
        parser.feed(html)
        return writer.get_text()


class _State(Enum):
    Header = 1
    Paragraph = 2


class _HtmlElementType(Enum):
    Unknown = 0
    Header = 1
    Paragraph = 2


class _HtmlElement:
    def __init__(self, element_type: _HtmlElementType, tag: str, attrs: list, skip_element=False):
        self.element_type: _HtmlElementType = element_type
        self.tag: str = tag
        self.attrs: list = attrs
        self.data: str = ""
        self.skip_element: bool = skip_element

    def __str__(self) -> str:
        return f"<{self.tag} __skip_element={self.skip_element} attrs={self.attrs}/>"

    def __repr__(self) -> str:
        return f"<{self.tag} __skip_element={self.skip_element} attrs={self.attrs}/>"


class _HtmlWalker(HtmlParserListener):
    def __init__(self, host_name: str, writer: TextWriter, elements_filter: Rules):
        self._writer = writer
        self._stack = deque()
        self._in_header_node_deep: int = 0
        self._in_ignored_node_deep: int = 0
        self._state: _State = _State.Paragraph
        self._filter = elements_filter
        self._host_name = host_name

    def on_starttag(self, tag: str, attrs):
        super().on_starttag(tag, attrs)

        element_type = self._detect_element_type(attrs, tag)
        skip_element_content = self._should_skip(tag, attrs)
        self._stack.append(_HtmlElement(element_type, tag, attrs, skip_element=skip_element_content))

        if skip_element_content:
            self._in_ignored_node_deep += 1
        if self._in_ignored_node_deep > 0:
            return

        if tag == "a":
            self._on_link(attrs)
        elif tag == "br":
            self._writer.newline()
        elif element_type == _HtmlElementType.Header:
            self._in_header_node_deep = self._in_header_node_deep + 1
            is_header_started = self._in_header_node_deep == 1
            if is_header_started:
                self._state = _State.Header
                self._writer.start_header()
        elif element_type == _HtmlElementType.Paragraph:
            if self._state == _State.Paragraph:
                self._writer.start_paragraph()

    def on_data(self, data: str):
        super().on_data(data)
        if self._in_ignored_node_deep > 0:
            return

        if self._state == _State.Header:
            self._writer.write_header(data)
        elif self._state == _State.Paragraph:
            self._writer.write_paragraph(data)

    def on_endtag(self, tag: str):
        super().on_endtag(tag)
        el: _HtmlElement = self._stack.pop()
        if el.skip_element:
            self._in_ignored_node_deep = max(self._in_ignored_node_deep - 1, 0)
            return

        if el.element_type == _HtmlElementType.Header:
            self._in_header_node_deep = max(self._in_header_node_deep - 1, 0)
            if self._in_header_node_deep == 0:
                self._state = _State.Paragraph

    def _detect_element_type(self, attrs, tag):
        element_type: _HtmlElementType
        if self._is_header(tag, attrs):
            element_type = _HtmlElementType.Header
        elif self._is_paragraph(tag, attrs):
            element_type = _HtmlElementType.Paragraph
        else:
            element_type = _HtmlElementType.Unknown
        return element_type

    def _is_header(self, tag, attrs) -> bool:
        return self._filter.is_header(self._host_name, tag, attrs)

    def _is_paragraph(self, tag, attrs):
        return self._filter.is_paragraph(self._host_name, tag, attrs)

    def _on_link(self, attrs):
        attrs_dict = dict(attrs)
        if "href" in attrs_dict:
            self._writer.write_link(attrs_dict["href"])

    def _should_skip(self, tag, attrs) -> bool:
        return self._filter.exclude(self._host_name, tag, attrs)
