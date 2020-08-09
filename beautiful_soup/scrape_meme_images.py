import json
from os import makedirs, path
import random
import time
from uuid import uuid4

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

MEMES_BASE_URL = 'https://knowyourmeme.com/memes'


def full_size_image_sources_and_alt_text_from_tags(tags):
    for tag in tags:
        src = tag.get('data-src')
        alt_text = tag.get('alt')
        if src and '/photos/images/masonry/' in src:
            full_size_src = src.replace('masonry', 'original')
            yield full_size_src, alt_text


def get_page_data(meme_slug, page_number, user_agent):
    print(f'Getting page {page_number}...')
    page_url = f'{MEMES_BASE_URL}/{meme_slug}/photos/page/{page_number}'
    page_response = requests.get(page_url, headers={'User-Agent': user_agent})

    if page_response.status_code == 200:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        print(f'Parsed HTML for {page_url}')
        return soup
    else:
        print(f'Unable to get {page_url} Status: {page_response.status_code}')


def scrape_meme(output_dir, meme_slug):
    if not path.exists(output_dir):
        makedirs(output_dir)
    
    user_agent = random.choice(COMMON_USER_AGENTS)
    alt_text_path = path.join(output_dir, 'alt_text.json')
    page_number = 1

    all_src_alt_pairs = set()
    all_image_alt_text = dict()

    page = get_page_data(meme_slug, page_number, user_agent)
    image_tags = page.find_all('img')
    scraped_src_alt_pairs = set(full_size_image_sources_and_alt_text_from_tags(image_tags))
    new_src_alt_pairs = scraped_src_alt_pairs.difference(all_src_alt_pairs)

    while new_src_alt_pairs:
        all_src_alt_pairs.update(new_src_alt_pairs)
        
        for src, alt in new_src_alt_pairs:
            image_response = requests.get(src, headers={'User-Agent': user_agent})
            
            if image_response.status_code == 200:
                image_uuid = str(uuid4())
                _, extension = path.splitext(src)
                output_path = path.join(output_dir, f'{image_uuid}{extension}')

                print(f'Saving image {src} to {output_path}')
                with open(output_path, 'wb') as file_handle:
                    file_handle.write(image_response.content)
                
                print(f'Adding alt text: {alt}')
                all_image_alt_text[image_uuid] = alt
                
                duration = 0.37 + (random.random() * 2.34)
                print(f'Sleeping for {duration:.2f} seconds...')
                time.sleep(duration)
            else:
                print('Unable to get {src} Status: {image_response.status_code}')
        
        print(f'Saving alt text to {alt_text_path}')
        with open(alt_text_path, 'w') as file_handle:
            json.dump(all_image_alt_text, file_handle)

        page_number += 1
        page = get_page_data(meme_slug, page_number, user_agent)
        
        image_tags = page.find_all('img')
        scraped_src_alt_pairs= set(full_size_image_sources_and_alt_text_from_tags(image_tags))
        new_src_alt_pairs = scraped_src_alt_pairs.difference(all_src_alt_pairs)
    
        print(f'Sleeping for {duration:.2f} seconds...')
        time.sleep(duration)
        duration = 3 + (random.random() * 3)
        

@click.command()
@click.option('-d', '--output-dir', required=True)
@click.option(
    '-m', 
    '--meme-slugs', 
    required=True, 
    help='Comma-separated list of URL slugs for meme names.'
)
def scrape_memes(output_dir, meme_slugs):
    split_slugs = (slug.strip() for slug in meme_slugs.split(',') if slug)

    for slug in split_slugs:
        filename_friendly_slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        meme_output_dir = path.join(output_dir, filename_friendly_slug)
        
        print(f'Saving images and text for {slug} in {meme_output_dir}')
        scrape_meme(meme_output_dir, slug)


if __name__ == '__main__':
    scrape_memes()
