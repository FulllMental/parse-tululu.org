import json
import os
import collections

from pprint import pprint

from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_book_descriptions(filename, dest_folder=''):
    json_path = os.path.join(dest_folder, filename)
    with open(json_path) as file:
        books_descriptions = json.load(file)
    return books_descriptions


if __name__ == '__main__':
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(['html', 'xml'])
    )
    filename = 'book_description.json'
    dest_folder = 'downloads'
    books_descriptions = get_book_descriptions(filename, dest_folder)

    template = env.get_template('template.html')

    rendered_page = template.render(
        books_descriptions = books_descriptions
    )

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()