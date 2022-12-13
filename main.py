from pathlib import Path

import requests


def get_book(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def download_book(site_response, filename, folder_name):
    with open(f"{folder_name}/{filename}", 'wb') as file:
        file.write(site_response.content)


if __name__ == '__main__':
    folder_name = "books"
    Path(folder_name).mkdir(parents=True, exist_ok=True)

    for book_index in range(10):
        url = f"https://tululu.org/txt.php?id={book_index}"
        filename = f'id{book_index + 1}.txt'

        book = get_book(url)
        download_book(book, filename, folder_name)
