from os import path
import random
import time

import click
from selenium import webdriver

from util import get_chrome_driver

MEMES_BASE_URL = 'https://knowyourmeme.com'
MEMES_PAGE_BASE_URL = 'https://knowyourmeme.com/memes/page/'
GDPR_BUTTON_XPATH = '//*[@id="qcCmpButtons"]/button[2]'

def meme_links_from_anchor_tags(anchor_tags):
    for tag in anchor_tags:
        href = tag.get_attribute('href')
        if href and '/memes/' in href and 'page/' not in href:
            yield href


@click.command()
@click.argument('output_dir')
@click.option('--headless', is_flag=True)
def get_links(output_dir, headless):
    output_path = path.join(output_dir, 'meme_links.txt')
    
    driver = get_chrome_driver(headless)
    page_number = 1
    print(f'Getting page {page_number}...')
    driver.get(f'{MEMES_PAGE_BASE_URL}{page_number}')
    
    gdpr_button = driver.find_element_by_xpath(GDPR_BUTTON_XPATH)
    gdpr_button.click()
    time.sleep(2)

    all_links = set()
    anchor_tags = driver.find_elements_by_tag_name('a')
    new_links = set(meme_links_from_anchor_tags(anchor_tags))
    print('Found meme links:')
    print('\n'.join(new_links))

    while new_links.difference(all_links):
        all_links.update(new_links)
        print(f'Saving {len(all_links)} links in flat file: {output_path}\n')
        with open(output_path, 'w') as file_handle:
            file_handle.write('\n'.join(all_links))
        
        page_number += 1
        print(f'Getting page {page_number}...')
        driver.get(f'{MEMES_PAGE_BASE_URL}{page_number}')    
        time.sleep(10 + (random.random() * 6))

        anchor_tags = driver.find_elements_by_tag_name('a')
        new_links = set(meme_links_from_anchor_tags(anchor_tags))
        print('Found meme links:')
        print('\n'.join(new_links))


if __name__ == '__main__':
    get_links()
