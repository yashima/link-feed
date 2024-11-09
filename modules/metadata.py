from bs4 import BeautifulSoup
import re
from datetime import datetime
import requests

def get_website_title(url):    
    if not url:
        return ''
    elif not url.startswith('http'):
        url = 'https://' + url
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else None
        return title
    else:
        return ''


def update_meta_data(link):
    response = requests.get(link.get_address())
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')    

    canonical_link = soup.find('link', rel='canonical')    
    link.canonical_link=canonical_link['href'] if canonical_link else link.canonical_link
    link.canonical_link = link.canonical_link[:200] if link.canonical_link else None

    author = soup.find('meta', {'name': 'author'})
    link.author = author['content'] if author else link.author

    modified_date = parse_date(soup.find('meta', {'property': 'article:modified_time'}))
    link.document_modified_at = modified_date if modified_date else link.document_modified_at

    link.locale = soup.find('html')['lang'] if soup.find('html', {'lang': True}) else link.locale

    # Extract description
    description = soup.find('meta', {'property': 'og:description'})  # Facebook metadata
    description = description['content'] if description else None

    if not description:
        description = soup.find('meta', {'name': 'twitter:description'})  # Twitter metadata
        description = description['content'] if description else None

    link.summary=description[:512] if description else link.summary[:512]


    # Extract title from meta data if available
    title = soup.find('meta', {'property': 'og:title'})  # Facebook metadata
    title = title['content'] if title else None

    if not title:
        title = soup.find('meta', {'name': 'twitter:title'})  # Twitter metadata
        title = title['content'] if title else None

    # Extract title from <title> tag if not found in metadata
    if not title:
        title = soup.title.string if soup.title else ''

    link.title = title[:256] if title else link.title

    if link.domain:
        link.domain = link.domain.lstrip('www.') if link.domain.startswith('www') else link.domain

    return link


def parse_date(date_element):
    if not date_element:
        return None

    date_pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(date_pattern, date_element['content'])

    if match:
        date_substring = match.group()
        date_format = '%Y-%m-%d'
        parsed_date = datetime.strptime(date_substring, date_format)
        return parsed_date
    else:
        return None