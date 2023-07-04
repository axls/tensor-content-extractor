from os.path import dirname

from content_extractor import ContentExtractor


def extract_from_file(file_name, host_name: str = "*", rules_file_name: str = None) -> str:
    extractor = ContentExtractor(f"{dirname(__file__)}/data/{rules_file_name}" if rules_file_name else None)
    text = extractor.extract_from_file(f"{dirname(__file__)}/data/{file_name}", host_name=host_name)
    print("\n-------------------")
    print(text)
    print("-------------------")
    return text


def extract_from_file_with_test_rules(file_name) -> str:
    return extract_from_file(file_name, host_name="test", rules_file_name="test_rules.txt")
