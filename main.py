import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup as BS
from pathvalidate import sanitize_filename


def get_site_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def check_for_redirect(response):
    if response.url == "https://tululu.org/" or response.history:
        raise requests.HTTPError()


def download_txt(book_text, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    secure_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(secure_path, 'wb') as file:
        file.write(book_text.content)


def get_filename(book_index):
    book_description_url = f"https://tululu.org/b{book_index}/"
    frontpage_response = get_site_response(book_description_url)
    soup = BS(frontpage_response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    return f"{book_index}. {title.strip()}"


if __name__ == '__main__':
    for book_index in range(1, 11):
        book_text_url = f"https://tululu.org/txt.php?id={book_index}"
        book_text = get_site_response(book_text_url)

        try:
            check_for_redirect(book_text)
        except requests.HTTPError:
            continue

        filename = get_filename(book_index)
        download_txt(book_text, filename)
