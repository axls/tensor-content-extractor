import pathlib
from os.path import splitext
from urllib.parse import urlparse


def save_to_file(directory_path: str, original_resource_address: str, text: str):
    url = urlparse(original_resource_address)
    host_name = url.hostname
    out_file_path = pathlib.Path(directory_path, host_name, splitext(url.path[1:])[0] + ".txt")
    out_file_path.parent.mkdir(exist_ok=True, parents=True)
    out_file_path.write_text(text)
    print(f"Текст страницы [{original_resource_address}] сохранен в файл: {out_file_path.absolute()}")
    pass
