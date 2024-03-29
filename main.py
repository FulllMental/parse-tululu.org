import argparse
import os
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as BS
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def save_content(file_content, filename, dest_folder, folder):
    download_path = os.path.join(dest_folder, folder)
    os.makedirs(download_path, exist_ok=True)
    file_path = os.path.join(download_path, filename)
    with open(file_path, 'wb') as file:
        file.write(file_content.content)


def parse_book_page(book_page_response, book_page_url):
    bookpage_soup = BS(book_page_response.text, 'lxml')

    text_link_selector = 'table.d_book a'
    book_text_link = urljoin(book_page_url, bookpage_soup.select(text_link_selector)[-3]['href'])
    if '_votes' in book_text_link:
        raise requests.HTTPError()

    title_selector = 'h1'
    title, author = bookpage_soup.select(title_selector)[0].text.split('::')
    title = title.strip()

    genre_selector = 'span.d_book a'
    genres = bookpage_soup.select(genre_selector)
    book_genres = [genre.text for genre in genres]

    comments_selector = '.texts span.black'
    comments = bookpage_soup.select(comments_selector)
    book_comments = [comment.text for comment in comments]

    book_cover_selector = '.bookimage img'
    book_cover = bookpage_soup.select(book_cover_selector)[0]['src']
    book_cover_link = urljoin(book_page_url, book_cover)
    book_cover_filename = book_cover.split('/')[2]

    book_text_filename = sanitize_filename(title).replace(' ','_')

    book_description = {
        'title': title,
        'author': author.strip(),
        'book_cover_link': book_cover_link,
        'book_cover_filename': book_cover_filename,
        'book_text_filename': f'{book_text_filename}.txt',
        'book_text_link': book_text_link,
        'book_genres': book_genres,
        'book_comments': book_comments,
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
    parser.add_argument('--dest_folder', nargs='?', type=str, default='',
                        help='Папка для скачивания | Download folder')
    args = parser.parse_args()

    for book_index in range(args.start_id, args.end_id + 1):
        book_page_url = f"https://tululu.org/b{book_index}/"
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

            save_content(book_cover_img, book_description['book_cover_filename'], args.dest_folder, folder='images/')

            book_text_response = requests.get(book_description['book_text_link'], params=payload)
            book_text_response.raise_for_status()
            check_for_redirect(book_text_response)

            filename = f"{book_index}. {book_description['title']}"
            save_content(book_text_response, book_description['book_text_filename'], args.dest_folder, folder='books/')
        except requests.HTTPError:
            print(f'Книга с id {book_index} не найдена...\n', file=sys.stderr)
            continue
        except requests.ConnectionError:
            print('Похоже соединение с сайтом прервано, пробую продолжить работу...')
            time.sleep(10)
            continue
