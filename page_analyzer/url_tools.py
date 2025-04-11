from urllib.parse import urlparse

from bs4 import BeautifulSoup


def get_domain(url: str) -> str:
    domain = '://'.join([urlparse(url).scheme, urlparse(url).netloc])
    return domain


def url_parser(_response):
    soup = BeautifulSoup(_response.text, 'html.parser')
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.find('title').text if soup.find('title') else ''
    description = ''
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        if tag.get('name', '').lower() == 'description':
            description = tag.get('content', '')
            break
    status_code = _response.status_code
    return status_code, h1, title, description
