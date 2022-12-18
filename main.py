import argparse
import os
from urllib.parse import urljoin

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
    os.makedirs(folder, exist_ok=True)
    secure_book_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(secure_book_path, 'wb') as file:
        file.write(book_text.content)


def download_image(book_cover_img, book_cover_name, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    image_path = os.path.join(folder, book_cover_name)
    with open(image_path, 'wb') as file:
        file.write(book_cover_img.content)


def parse_book_page(book_page_response):
    bookpage_soup = BS(book_page_response.text, 'lxml')
    title, author = bookpage_soup.find('h1').text.split('::')
    parse_genres = bookpage_soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in parse_genres]
    parse_comments = bookpage_soup.find_all(class_='texts')
    book_comments = [comment.find('span', class_='black').text for comment in parse_comments]
    parse_book_cover = bookpage_soup.find('div', class_='bookimage').find('img')['src']
    book_cover_link = urljoin('https://tululu.org/', bookpage_soup.find('div', class_='bookimage').find('img')['src'])
    book_cover_filename = parse_book_cover.split('/')[2]
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
        book_text_url = f"https://tululu.org/txt.php?id={book_index}"
        try:
            book_page_response = get_site_response(book_page_url)
            check_for_redirect(book_page_response)

            book_description = parse_book_page(book_page_response)
            print(f'Заголовок: {book_index}. {book_description["title"]}\n\
                    Жанры: {book_description["book_genres"]}')

            book_cover_img = get_site_response(book_description['book_cover_link'])
            check_for_redirect(book_cover_img)

            download_image(book_cover_img, book_description['book_cover_filename'])

            book_text_response = get_site_response(book_text_url)
            check_for_redirect(book_text_response)

            filename = f"{book_index}. {book_description['title']}"
            download_txt(book_text_response, filename)
        except requests.HTTPError:
            continue
