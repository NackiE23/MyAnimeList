import requests
import re
from bs4 import BeautifulSoup


def parse_season_page():
    text = requests.get('https://myanimelist.net/anime/season').text
    soup = BeautifulSoup(text, 'lxml')

    names = [name.text for name in soup.select('.h2_anime_title .link-title')]
    releases = [release.text.strip() for release in soup.select('.info .item:first-child')]
    descriptions = [description.text.strip() for description in soup.select('.synopsis .preline')]
    categories = [[cat.text.strip() for cat in category.select('.genre')] for category in soup.select('.genres .genres-inner')]
    img_paths = [img.get('src', img.get('data-src', '#')) for img in soup.select('.image a:first-child img')]
    links = [link.get('href', '#') for link in soup.select('.h2_anime_title .link-title')]

    result = {
        'name': names,
        'release': releases,
        'description': descriptions,
        'categories': categories,
        'img_path': img_paths,
        'link': links,
    }

    return result


def parse_mal_anime_page(url):
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'lxml')

    # Name/Alternative Name
    name = soup.find('p', class_='title-english')
    alternative_name = soup.find('h1', class_='title-name')
    
    if name and alternative_name:
        name = name.text
        alternative_name = alternative_name.text
    elif alternative_name and not name:
        name = alternative_name.text
        alternative_name = ""
    elif name and not alternative_name:
        name = name.text
        alternative_name = ""
    
    # Release
    release = soup.find('span', string='Aired:')

    if not release:
        release = soup.find('span', string='Published:')
    if release:
        release = release.parent.text
        release = re.search(r'[A-Z][a-z]{2} \d{1,2}, \d{4}', release).group().replace(',', '')
    else:
        release = 'Jan 01 2000'

    # Description/Categories/Img Url
    description = soup.find('p', itemprop='description').text
    categories = [cat.text.strip() for cat in soup.find_all('span', itemprop='genre')]
    img_url = soup.select_one('.leftside > div:nth-child(1) > a:nth-child(1) > img:nth-child(1)').get('data-src', '#')

    result = {
        'name': name,
        'alternative_name': alternative_name,
        'release': release,
        'description': description,
        'categories': categories,
        'img_url': img_url,
    }

    return result
