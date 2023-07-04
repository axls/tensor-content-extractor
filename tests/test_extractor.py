import unittest
from textwrap import dedent

from .utils import extract_from_file, extract_from_file_with_test_rules


class ContentExtractorTests(unittest.TestCase):
    def test_simple_01(self):
        text = extract_from_file("simple_01.html")
        self.assertEqual(dedent("""
        # Заголовок
        
        Первый параграф статьи. Который состоит из нескольких строк и [http://localhost]
        ссылки
        
        Еще один параграф статьи.
        """).strip("\n"), text)

    def test_host_specific_rule_applied(self):
        text = extract_from_file_with_test_rules("simple_01.html")
        self.assertEqual(dedent("""
        Навигация Home Profile

        # Заголовок
        
        Первый параграф статьи. Который состоит из нескольких строк и [http://localhost]
        ссылки
        
        Еще один параграф статьи.
        """).strip("\n"), text, "Должен включать блок с навигацией, в соответствии с кастомным правилом для домена "
                                "test")


if __name__ == '__main__':
    unittest.main()
