import os.path

from content_extractor import ContentExtractor

if __name__ == '__main__':
    extractor = ContentExtractor()
    # extractor.extract_from_url("https://moslenta.ru/news/city/van-khelsing-01-07-2023.htm")
    # text = extractor.extract_from_url("file:///home/axl/tmp/van-khelsing-01-07-2023.htm")
    # text = extractor.extract_from_url("https://www.gazeta.ru/social/2023/07/03/17227874.shtml")
    # text = extractor.extract_from_url("file://" + os.path.dirname(__file__) + "/tests/data/lenta_ru_01.html")
    # text = extractor.extract_from_url("file://" + os.path.dirname(__file__) + "/tests/data/rbc_01.html")
    text = extractor.extract_from_url("file://" + os.path.dirname(__file__) + "/tests/data/gazeta_01.html")
    # text = extractor.extract_from_url("file://" + os.path.dirname(__file__) + "/tests/data/simple_01.html")
    # text = extractor.extract_from_url("file://" + os.path.dirname(__file__) + "/tests/data/simple_02.html")
    print("--------------------------------------")
    print(text)
    print("--------------------------------------")

