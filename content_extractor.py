import getopt
import os.path
import sys
import urllib.parse
from textwrap import dedent

from content_extractor import ContentExtractor

from content_extractor.saver import save_to_file


def _help():
    print(dedent("""
    Использование:
    
    content_extractor.py <параметры> <адрес страницы>
    
    Параметры:
      -h, --help                    показать страницу помощи
      -d <путь>, --directory=<путь> каталог для сохранения текстовых файлов
      -r <путь>, --rules=<путь>     путь до файла с правилами разбора html
                                    пример правил можно посмотреть в файле ./content_extractor/default_rules.txt
      -o, --stdout                  выводить текст в стандартный вывод вместо сохранения в файл
    """).strip("\n"))
    sys.exit()


class _Options:
    def __init__(self):
        self.output_directory = os.getcwd()
        self.rules_file = None
        self.resource_address = None
        self.write_to_stdout = False
        self.domain = None
        self.encoding = "utf-8"


def _parse_command_line() -> _Options:
    result = _Options()
    opts, args = getopt.getopt(sys.argv[1:], "hd:r:o", ["help", "directory=", "rules=", "stdout", "domain=",
                                                        "encoding="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            _help()
        elif opt in ("-d", "--directory"):
            result.output_directory = arg
        elif opt in ("-r", "--rules"):
            result.rules_file = arg
        elif opt in ("-o", "--stdout"):
            result.write_to_stdout = True
        elif opt == "--domain":
            result.domain = arg
        elif opt == "--encoding":
            result.encoding = arg

    if len(args) < 1:
        print("Ошибка: не задан адрес страницы\n")
        _help()
    result.resource_address = args[-1]

    return result


if __name__ == '__main__':
    options = _parse_command_line()

    extractor = ContentExtractor(rules_file_name=options.rules_file)

    url = urllib.parse.urlparse(options.resource_address)
    if not url.scheme:
        text = extractor.extract_from_file(options.resource_address, host_name=options.domain, encoding=options.encoding)
    else:
        text = extractor.extract_from_url(options.resource_address)

    if options.write_to_stdout:
        print(text)
    else:
        save_to_file(options.output_directory, options.resource_address, text)
