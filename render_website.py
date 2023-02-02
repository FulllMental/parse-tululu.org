import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions(filename, dest_folder=''):
    json_path = os.path.join(dest_folder, filename)
    with open(json_path) as file:
        books_descriptions = json.load(file)
    return books_descriptions


def rebuild_page():
    logging.warning("Изменение index.html")
    template = env.get_template('template.html')
    rendered_page = template.render(
        grouped_books_descriptions = grouped_books_descriptions
    )
    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(['html', 'xml'])
    )

    filename = 'book_description.json'
    dest_folder = 'downloads'
    books_descriptions = get_book_descriptions(filename, dest_folder)
    grouped_books_descriptions = list(chunked(books_descriptions, 2))

    rebuild_page()

    server = Server()
    server.watch('template.html', rebuild_page)
    server.serve()
