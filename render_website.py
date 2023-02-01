import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_book_descriptions(filename, dest_folder=''):
    json_path = os.path.join(dest_folder, filename)
    with open(json_path) as file:
        books_descriptions = json.load(file)
    return books_descriptions


def rebuild_page():
    print('Пошла функция')
    template = env.get_template('template.html')
    rendered_page = template.render(
        books_descriptions = books_descriptions
    )
    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


if __name__ == '__main__':
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(['html', 'xml'])
    )

    filename = 'book_description.json'
    dest_folder = 'downloads'
    books_descriptions = get_book_descriptions(filename, dest_folder)

    rebuild_page()

    server = Server()
    server.watch('template.html', rebuild_page)
    server.serve()
