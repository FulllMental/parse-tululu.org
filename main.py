import argparse
import os
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as BS
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def download_txt(book_text, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    secure_book_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(secure_book_path, 'wb') as file:
        file.write(book_text.content)


def download_image(book_cover_img, book_cover_name, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    image_path = os.path.join(folder, book_cover_name)
    with open(image_path, 'wb') as file:
        file.write(book_cover_img.content)


def parse_book_page(book_page_response, book_page_url):
    bookpage_soup = BS(book_page_response.text, 'lxml')
    title, author = bookpage_soup.find('h1').text.split('::')
    genres = bookpage_soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in genres]
    comments = bookpage_soup.find_all(class_='texts')
    book_comments = [comment.find('span', class_='black').text for comment in comments]
    book_cover = bookpage_soup.find('div', class_='bookimage').find('img')['src']
    book_cover_link = urljoin(book_page_url, bookpage_soup.find('div', class_='bookimage').find('img')['src'])
    book_cover_filename = book_cover.split('/')[2]
    book_description = {
        'title': title.strip(),
        'author': author.strip(),
        'book_genres': book_genres,
        'book_comments': book_comments,
        'book_cover_link': book_cover_link,
        'book_cover_filename': book_cover_filename
    }
    return book_description


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Данная программа скачивает книги и их обложки с сайта "tululu.org", а так же информацию о
        названии книги, жанре, авторе и отзывы из комментариев.
        This program downloads books and their covers from the "tululu.org" website. As well it gather information about
        the title of the book, genre, author and reviews from the comments.'''
    )
    parser.add_argument('start_id', nargs='?', type=int, default=1,
                        help='Номер начальной страницы | First page\'s id')
    parser.add_argument('end_id', nargs='?', type=int, default=10,
                        help='Номер финальной страницы | Last page\'s id')
    args = parser.parse_args()

    for book_index in range(args.start_id, args.end_id + 1):
        book_page_url = f"https://tululu.org/b{book_index}/"
        book_text_url = 'https://tululu.org/txt.php'
        payload = {'id': book_index}
        try:
            book_page_response = requests.get(book_page_url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)

            book_description = parse_book_page(book_page_response, book_page_url)
            print(f'Заголовок: {book_index}. {book_description["title"]}\n\
                    Жанры: {book_description["book_genres"]}\n')

            book_cover_img = requests.get(book_description['book_cover_link'])
            book_cover_img.raise_for_status()
            check_for_redirect(book_cover_img)

            download_image(book_cover_img, book_description['book_cover_filename'])

            book_text_response = requests.get(book_text_url, params=payload)
            book_text_response.raise_for_status()
            check_for_redirect(book_text_response)

            filename = f"{book_index}. {book_description['title']}"
            download_txt(book_text_response, filename)
        except requests.HTTPError:
            print(f'Книга с id {book_index} не найдена...\n', file=sys.stderr)
            continue
