import json
import logging
import sys
import time
from urllib.parse import urljoin

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as BS

from main import download_txt, download_image, check_for_redirect


def save_json_file(book_descriptions):
    book_descriptions_json = json.dumps(book_descriptions, ensure_ascii=False)
    with open('book_description.json', 'w') as my_file:
        my_file.write(book_descriptions_json)


def parse_book_links(category_page_response, category_page_url):
    category_page_soup = BS(category_page_response.text, 'lxml')
    all_books_id = category_page_soup.find_all('table', class_='d_book')
    book_links_per_page = [urljoin(category_page_url, book_id.find('a')['href']) for book_id in all_books_id]
    return book_links_per_page


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
    book_text_link = urljoin(book_page_url, bookpage_soup.find('table', class_='d_book').find_all('a')[-3]['href'])
    book_description = {
        'title': title.strip(),
        'author': author.strip(),
        'book_cover_link': book_cover_link,
        'book_cover_filename': book_cover_filename,
        'book_text_link': book_text_link,
        'book_genres': book_genres,
        'book_comments': book_comments,
    }
    return book_description


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    book_urls = []
    book_descriptions = []
    err_statistics = []

    logging.info(f"Сбор ссылок на книги со страниц, по жанрам")

    for page_index in tqdm(range(1, 11), ncols=100):
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

            book_cover_img = requests.get(book_description['book_cover_link'])
            book_cover_img.raise_for_status()
            check_for_redirect(book_cover_img)
            download_image(book_cover_img, book_description['book_cover_filename'])

            book_text_response = requests.get(book_description['book_text_link'])
            book_text_response.raise_for_status()
            check_for_redirect(book_text_response)

            download_txt(book_text_response, book_description['title'])
        except requests.HTTPError:
            err_statistics.append(f"Похоже книгу {book_description['title']} не удалось скачать...")
            # print(f"Похоже книгу {book_url} не удалось скачать...\n", file=sys.stderr)
            continue
        except requests.ConnectionError:
            print('Похоже соединение с сайтом прервано, пробую продолжить работу...')
            time.sleep(10)
            continue
    [print(err_stats, file=sys.stderr) for err_stats in err_statistics]
    logging.info(f"Сохраняю, данные в JSON файл...\n")

    save_json_file(book_descriptions)
