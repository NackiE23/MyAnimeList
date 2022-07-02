import requests
from bs4 import BeautifulSoup


def parse_season_page():
    text = requests.get('https://myanimelist.net/anime/season').text
    soup = BeautifulSoup(text, 'lxml')

    names = [name.text for name in soup.select('.h2_anime_title .link-title')]
    releases = [release.text.strip() for release in soup.select('.info .item:first-child')]
    descriptions = [description.text.strip() for description in soup.select('.synopsis .preline')]
    categories = [[cat.text.strip() for cat in category.select('.genre')] for category in soup.select('.genres .genres-inner')]
    img_paths = [img.get('src', img.get('data-src', '#')) for img in soup.select('.image a:first-child img')]

    result = {
        'name': names,
        'release': releases,
        'description': descriptions,
        'categories': categories,
        'img_path': img_paths,
    }

    return result
