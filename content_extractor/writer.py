import re
import textwrap

_SPACES_RE = re.compile(r"\s+")


class TextWriter:
    def __init__(self):
        self._max_line_length = 80
        self._is_new_data: bool = True
        self._lines = []
        self._buffer = ""

    def start_header(self):
        self._is_new_data = True
        if self._has_data():
            self.newline()
        # self._buffer += "\n#START HEADER\n"

    def end_header(self):
        # self._buffer += "\n#END HEADER\n"
        pass

    def write_header(self, text: str):
        header = text
        if self._is_new_data:
            header = "# " + header
        self._write_data(header)

    def write_paragraph(self, text: str):
        self._write_data(text)

    def start_paragraph(self):
        self._is_new_data = True
        if self._has_data():
            self.newline()
        # self._buffer += "\n#START PARAGRAPH\n"
        pass

    def end_paragraph(self):
        # self._buffer += "\n#END PARAGRAPH\n"
        pass

    def get_text(self) -> str:
        return "\n".join(self._lines) + "\n" + self._buffer

    def write_link(self, url: str):
        self._write(f"[{url}]")

    def newline(self):
        self._flush()
        if len(self._lines) > 0 and len(self._lines[-1]) > 0:
            self._lines.append("")

    def _has_data(self) -> bool:
        return len(self._lines) > 0 or len(self._buffer) > 0

    def _write_data(self, text: str):
        normalized = _SPACES_RE.sub(" ", text).strip()
        if self._is_new_data:
            self._is_new_data = False
        else:
            self._buffer += " "
        self._write(normalized)

    def _write(self, text: str):
        if len(text) == 0:
            return
        self._buffer += text
        buffer_lines = self._buffer.splitlines()
        wrapped_lines = []
        for line in buffer_lines:
            wrapped_lines.extend(textwrap.wrap(line, width=self._max_line_length))
        if len(wrapped_lines) > 1:
            self._lines.extend(wrapped_lines[:-1])
        self._buffer = wrapped_lines[-1]

    def _flush(self):
        buffer_lines = self._buffer.splitlines()
        wrapped_lines = []
        for line in buffer_lines:
            wrapped_lines.extend(textwrap.wrap(line, width=self._max_line_length))
        self._lines.extend(wrapped_lines)
        self._buffer = ""

