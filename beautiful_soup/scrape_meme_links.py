from os import path
import random
import time

from bs4 import BeautifulSoup
import click
import requests


COMMON_USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0 ',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
)


MEMES_PAGE_BASE_URL = 'https://knowyourmeme.com/memes/page/'

def meme_links_from_anchor_tags(anchor_tags):
    for tag in anchor_tags:
        href = tag.get('href')
        if href and '/memes/' in href and 'page/' not in href:
            yield href


def get_page_data(page_number, user_agent):
    print(f'Getting page {page_number}...')
    page_url = f'{MEMES_PAGE_BASE_URL}{page_number}'
    page_response = requests.get(page_url, headers={'User-Agent': user_agent})

    if page_response.status_code == 200:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        print(f'Parsed HTML for {page_url}')
        return soup
    else:
        print(f'Unable to get {page_url} Status: {page_response.status_code}')


@click.command()
@click.argument('output_dir')
def get_links(output_dir):
    output_path = path.join(output_dir, 'meme_links.txt')
    user_agent = random.choice(COMMON_USER_AGENTS)

    all_links = set()
    page_number = 1
    
    page = get_page_data(page_number, user_agent)
    
    anchor_tags = page.find_all('a')
    new_links = set(meme_links_from_anchor_tags(anchor_tags))
    print('Found meme links:')
    print('\n'.join(new_links))

    while new_links.difference(all_links):
        all_links.update(new_links)
        print(f'Saving {len(all_links)} links in flat file: {output_path}\n')
        with open(output_path, 'w') as file_handle:
            file_handle.write('\n'.join(all_links))
        
        time.sleep(0.5 + (random.random() * 1))
        page_number += 1
        
        page = get_page_data(page_number, user_agent)
        anchor_tags = page.find_all('a')
        new_links = set(meme_links_from_anchor_tags(anchor_tags))
        
        print('Found meme links:')
        print('\n'.join(new_links))


if __name__ == '__main__':
    get_links()
