import urllib.request
from collections import deque
from enum import Enum

from .filter import Filter
from .writer import TextWriter
from .html import FilteredHtmlParser, HtmlParserListener


class ContentExtractor:
    def extract_from_url(self, url: str) -> str:
        html = self._load(url)
        writer = TextWriter()
        self._extract_from(html, writer)
        return writer.get_text()

    def _load(self, url: str) -> str:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        response_encoding = response.headers.get_content_charset(failobj="utf-8")
        return response.read().decode(response_encoding)

    def _extract_from(self, html: str, writer: TextWriter):
        listener = _HtmlParserListener(writer)
        parser = FilteredHtmlParser(listener)
        parser.feed(html)
        pass


class _State(Enum):
    Unknown = 0
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

class _HtmlParserListener(HtmlParserListener):
    def __init__(self, writer: TextWriter):
        self._writer = writer
        self._stack = deque()
        self._data_lines: list = []
        self._in_header_deep: int = 0
        self._in_ignored_deep: int = 0
        self._in_paragraph: bool = False
        self._state: _State = _State.Paragraph
        self._filter = Filter()

    def on_starttag(self, tag: str, attrs):
        super().on_starttag(tag, attrs)

        element_type: _HtmlElementType
        if self._is_header(tag, attrs):
            element_type = _HtmlElementType.Header
        elif self._is_paragraph(tag, attrs):
            element_type = _HtmlElementType.Paragraph
        else:
            element_type = _HtmlElementType.Unknown

        skip_element_content = self._should_skip(tag, attrs)
        self._stack.append(_HtmlElement(element_type, tag, attrs, skip_element=skip_element_content))
        if skip_element_content:
            self._in_ignored_deep += 1

        if self._in_ignored_deep > 0:
            return

        if tag == "a":
            self._on_link(attrs)
        elif tag == "br":
            self._writer.newline()
        elif element_type == _HtmlElementType.Header:
            if self._state == _State.Paragraph:
                self._writer.end_paragraph()
            self._in_header_deep = self._in_header_deep + 1
            if self._in_header_deep == 1:
                self._state = _State.Header
                self._writer.start_header()
        elif element_type == _HtmlElementType.Paragraph:
            if self._state == _State.Paragraph:
                self._writer.end_paragraph()
                self._writer.start_paragraph()

    def on_data(self, data: str):
        super().on_data(data)
        if self._in_ignored_deep > 0:
            return

        if self._state == _State.Header:
            self._writer.write_header(data)
        elif self._state == _State.Paragraph:
            self._writer.write_paragraph(data)

    def on_endtag(self, tag: str):
        super().on_endtag(tag)
        el: _HtmlElement = self._stack.pop()
        if el.skip_element:
            self._in_ignored_deep = max(self._in_ignored_deep - 1, 0)
            return

        if el.element_type == _HtmlElementType.Header:
            self._in_header_deep = max(self._in_header_deep - 1, 0)
            if self._in_header_deep == 0:
                self._finish_header()
                self._state = _State.Paragraph
        elif el.element_type == _HtmlElementType.Paragraph:
            if self._in_header_deep == 0:
                self._finish_paragraph()
                self._state = _State.Paragraph

    def _is_header(self, tag, attrs) -> bool:
        return tag in {"h1", "h2", "h3", "h5", "h6", "h7"}

    def _is_paragraph(self, tag, attrs):
        return tag in {"div", "p"}

    def _on_link(self, attrs):
        attrs_dict = dict(attrs)
        if "href" in attrs_dict:
            self._writer.write_link(attrs_dict["href"])

    def _on_start_header(self):
        pass

    def _on_start_paragraph(self):
        pass

    def _finish_header(self):
        pass

    def _finish_paragraph(self):
        pass

    def _should_skip(self, tag, attrs) -> bool:
        return self._filter.exclude("*", tag, attrs)

