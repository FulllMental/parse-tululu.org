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

from main import download_txt, download_image, check_for_redirect, parse_book_page


def save_json_file(book_descriptions, dest_folder):
    filename = 'book_description.json'
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
    parser.add_argument('--skip_imgs', nargs='?', type=bool, default=False,
                        help='Папка для скачивания | Download folder')
    parser.add_argument('--skip_txt', nargs='?', type=bool, default=False,
                        help='Путь к *json файлу с результатами | The path to the *json file with the results')
    parser.add_argument('--dest_folder', nargs='?', type=str, default='',
                        help='Папка для скачивания | Download folder')
    parser.add_argument('--json_path', nargs='?', type=str, default='',
                        help='Путь к *json файлу с результатами | The path to the *json file with the results')
    args = parser.parse_args()

    logging.info(f"Сбор ссылок на книги со страниц, по жанрам")

    for page_index in tqdm(range(args.start_page, args.end_page), ncols=100):
        category_page_url = f'https://tululu.org/l55/{page_index}'
        category_page_response = requests.get(category_page_url)
        category_page_response.raise_for_status()
        book_urls.extend(parse_book_links(category_page_response, category_page_url))

    logging.info(f"Сбор информации с указанных страниц / скачивание книг / обложек")

    for book_url in tqdm(book_urls, ncols=100):
        try:
            book_page_response = requests.get(book_url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
            book_description = parse_book_page(book_page_response, book_url)
            book_descriptions.append(book_description)

            if not args.skip_imgs:
                book_cover_img = requests.get(book_description['book_cover_link'])
                book_cover_img.raise_for_status()
                check_for_redirect(book_cover_img)
                download_image(book_cover_img, book_description['book_cover_filename'], args.dest_folder)

            if not args.skip_txt:
                book_text_response = requests.get(book_description['book_text_link'])
                book_text_response.raise_for_status()
                check_for_redirect(book_text_response)

                download_txt(book_text_response, book_description['title'], args.dest_folder)
        except requests.HTTPError:
            err_statistics.append(f"Похоже книгу {book_description['title']} не удалось скачать...")
            continue
        except requests.ConnectionError:
            print('Похоже соединение с сайтом прервано, пробую продолжить работу...')
            time.sleep(10)
            continue
    [print(err_stats, file=sys.stderr) for err_stats in err_statistics]

    logging.info(f"Сохраняю, данные в JSON файл...")

    save_json_file(book_descriptions, args.dest_folder)

    logging.info(f"Готово...\n")