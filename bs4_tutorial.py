import requests
from bs4 import BeautifulSoup as BS


def get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def get_article_title(soup):
    title_tag = soup.find('main').find('header').find('h1')
    title_text = title_tag.text
    return title_text


def get_article_image(soup):
    return soup.find('img', class_='attachment-post-image')['src']


def get_article_text(soup):
    return soup.find('div', class_='entry-content').text


if __name__=='__main__':
    url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
    response = get_page(url)
    soup = BS(response.text, 'lxml')

    title = get_article_title(soup)
    image_link = get_article_image(soup)
    article_text = get_article_text(soup)
    print(title, image_link, article_text, sep='\n')
