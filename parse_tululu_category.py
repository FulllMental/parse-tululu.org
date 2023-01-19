import argparse
import json
import logging
import os
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as BS
from tqdm import tqdm

from main import save_content, check_for_redirect, parse_book_page


def save_json_file(book_descriptions, dest_folder):
    filename = 'book_description.json'
    if dest_folder:
        os.makedirs(dest_folder, exist_ok=True)
    book_descriptions_json = json.dumps(book_descriptions, ensure_ascii=False)
    folder_path = os.path.join(dest_folder, filename)
    with open(folder_path, 'w') as my_file:
        my_file.write(book_descriptions_json)


def parse_book_links(category_page_response, category_page_url):
    category_page_soup = BS(category_page_response.text, 'lxml')
    all_books_selector = '.d_book'
    all_books_id = category_page_soup.select(all_books_selector)
    book_links_per_page = [urljoin(category_page_url, book_id.a['href']) for book_id in all_books_id]
    return book_links_per_page


def check_for_errors(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
            except requests.HTTPError:
                err_statistics.append(args[0])
                break
            except requests.ConnectionError:
                print('\nПохоже соединение с сайтом прервано, пробую продолжить работу...', file=sys.stderr)
                time.sleep(10)
    return wrapper


@check_for_errors
def get_book_urls(page_index, book_urls):
        category_page_url = f'https://tululu.org/l55/{page_index}'
        category_page_response = requests.get(category_page_url)
        category_page_response.raise_for_status()
        check_for_redirect(category_page_response)
        book_urls.extend(parse_book_links(category_page_response, category_page_url))


@check_for_errors
def download_content(book_url, skip_imgs, skip_txt):
    book_page_response = requests.get(book_url)
    book_page_response.raise_for_status()
    check_for_redirect(book_page_response)
    book_description = parse_book_page(book_page_response, book_url)
    book_descriptions.append(book_description)

    if not skip_imgs:
        book_cover_img = requests.get(book_description['book_cover_link'])
        book_cover_img.raise_for_status()
        check_for_redirect(book_cover_img)
        save_content(book_cover_img, book_description['book_cover_filename'], args.dest_folder, folder='images/')

    if not skip_txt:
        book_text_response = requests.get(book_description['book_text_link'])
        book_text_response.raise_for_status()
        check_for_redirect(book_text_response)
        save_content(book_text_response, book_description['book_text_filename'], args.dest_folder, folder='books/')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    book_urls = []
    book_descriptions = []
    err_statistics = []

    parser = argparse.ArgumentParser(
        description='''Данная программа скачивает книги и их обложки с сайта "tululu.org" из раздела "фантастика", а так же информацию о
            названии книги, жанре, авторе и отзывы из комментариев, которая сохраняется в json файл.
            This program downloads sci-fi books and their covers from the "tululu.org" website. As well it gather information about
            the title of the book, genre, author and reviews from the comments and save it in json file.'''
    )
    parser.add_argument('--start_page', nargs='?', type=int, default=1,
                        help='Номер начальной страницы | First page\'s id')
    parser.add_argument('--end_page', nargs='?', type=int, default=702,
                        help='Номер финальной страницы | Last page\'s id')
    parser.add_argument('-skip_imgs', action='store_true',
                        help='Не скачивать картинки | Skip downloading images')
    parser.add_argument('-skip_txt', action='store_true',
                        help='Не скачивать текст | Skip downloading texts')
    parser.add_argument('--dest_folder', nargs='?', type=str, default='',
                        help='Папка для скачивания | Download folder')
    parser.add_argument('--json_path', nargs='?', type=str, default='',
                        help='Путь к *json файлу с результатами | The path to the *json file with the results')
    args = parser.parse_args()

    logging.info(f"Сбор ссылок на книги со страниц, по жанрам")
    for page_index in tqdm(range(args.start_page, args.end_page), ncols=100):
        get_book_urls(page_index, book_urls)

    logging.info(f"Сбор информации с указанных страниц / скачивание книг / обложек")
    for book_url in tqdm(book_urls, ncols=100):
        download_content(book_url, args.skip_imgs, args.skip_txt)

    logging.info(f"Сохраняю, данные в JSON файл...")
    save_json_file(book_descriptions, args.dest_folder)
    if err_statistics:
        logging.info(f"Кажется не удалось найти данные страницы:")
        [print(err_stats, file=sys.stderr) for err_stats in err_statistics]
    logging.info(f"Готово...\n")