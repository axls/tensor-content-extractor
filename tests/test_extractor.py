import unittest
import textwrap

from content_extractor import ContentExtractor


class MyTestCase(unittest.TestCase):
    def test_something(self):
        extractor = ContentExtractor()
        text = extractor.extract_from_url("https://moslenta.ru/news/city/van-khelsing-01-07-2023.htm")
        print(text)
        self.assertEqual(True, True)  # add assertion here

    def test_textwrap(self):
        line = "   Длинная       длинная           строка, которая содержит разделители   \n   строк"
        lines = textwrap.wrap(line, width=25, )
        print("\n".join(lines))


if __name__ == '__main__':
    unittest.main()
