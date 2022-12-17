import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, urlparse
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
    secure_book_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(secure_book_path, 'wb') as file:
        file.write(book_text.content)


def download_image(book_cover_link, folder='images/'):
    book_cover_name = urlparse(book_cover_link).path.split('/')[2]
    book_cover_img = get_site_response(book_cover_link)
    os.makedirs(folder, exist_ok=True)
    secure_image_path = os.path.join(folder, book_cover_name)
    with open(secure_image_path, 'wb') as file:
        file.write(book_cover_img.content)


def get_filename(book_index, frontpage_soup):
    title, author = frontpage_soup.find('h1').text.split('::')
    return f"{book_index}. {title.strip()}"


def get_image_link(frontpage_soup):
    return urljoin('https://tululu.org/', frontpage_soup.find('div', class_='bookimage').find('img')['src'])


def get_book_comments(frontpage_soup):
    comments = frontpage_soup.find_all(class_='texts')
    return comments


if __name__ == '__main__':
    for book_index in range(1, 11):
        book_text_url = f"https://tululu.org/txt.php?id={book_index}"
        book_text = get_site_response(book_text_url)

        try:
            check_for_redirect(book_text)
        except requests.HTTPError:
            continue

        book_description_url = f"https://tululu.org/b{book_index}/"
        frontpage_response = get_site_response(book_description_url)
        frontpage_soup = BS(frontpage_response.text, 'lxml')
        filename = get_filename(book_index, frontpage_soup)
        book_genres = frontpage_soup.find('span', class_='d_book').find_all('a')

        print(f'\nЗаголовок: {filename}')
        print([genre.text for genre in book_genres])

        # book_cover_link = get_image_link(frontpage_soup)

        # download_image(book_cover_link)
        # download_txt(book_text, filename)

        # comments = get_book_comments(frontpage_soup)
        # if not comments:
        #     continue
        # print([comment.find('span', class_='black').text for comment in comments])
