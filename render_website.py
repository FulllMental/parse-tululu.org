import argparse
import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions(filename, dest_folder):
    json_path = os.path.join(dest_folder, filename)
    with open(json_path, encoding='utf-8') as file:
        books_descriptions = json.load(file)
    return books_descriptions


def rebuild_page():
    logging.warning("Изменение index.html")
    template = env.get_template('template.html')
    dest_folder = 'pages'
    os.makedirs(dest_folder, exist_ok=True)
    total_pages = paginated_book_descriptions[-1][0]

    for books_descriptions in paginated_book_descriptions:
        current_page_number = books_descriptions[0]
        grouped_books_descriptions = books_descriptions[1]
        rendered_page = template.render(
            grouped_books_descriptions=grouped_books_descriptions,
            current_page_number=current_page_number,
            total_pages=total_pages
        )
        page_name = f'index{current_page_number}.html'
        pages_path = os.path.join(dest_folder, page_name)
        with open(pages_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


def paginate_book_descriptions(books_descriptions):
    cards_row = 2
    cards_on_page = 5
    grouped_books_descriptions = list(chunked(books_descriptions, cards_row))
    page_book_groups = list(chunked(grouped_books_descriptions, cards_on_page))
    paginated_book_descriptions = [enumerated_group for enumerated_group in enumerate(page_book_groups, 1)]
    return paginated_book_descriptions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Данная программа создаёт страницы исходя из собранных данных. 
            This program render site pages with downloaded data.'''
    )
    parser.add_argument('--json_folder', nargs='?', type=str, default='',
                        help='Директория файла *.json | *.json file directory')
    parser.add_argument('--json_file', nargs='?', type=str, default='book_description.json',
                        help='название файла *.json (с расширением) | *.json filename (with extension)')
    args = parser.parse_args()

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(['html', 'xml'])
    )

    filename = args.json_file
    logging.warning("Получение информации из *.json")
    books_descriptions = get_book_descriptions(filename, args.json_folder)
    paginated_book_descriptions = paginate_book_descriptions(books_descriptions)

    rebuild_page()

    server = Server()
    server.watch('template.html', rebuild_page)
    server.serve(default_filename='pages/index1.html')
