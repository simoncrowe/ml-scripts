#!/usr/bin/env python3

import os
import time
import random
import json
from datetime import datetime

import click
import requests
from selenium import webdriver


def get_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(chrome_options=chrome_options)


def get_hashtag_url(hashtag):
    hashtag = hashtag[1:] if hashtag.startswith('#') else hashtag
    return f'https://www.instagram.com/explore/tags/{hashtag}/'


def save_image(url, name):
    image_response = requests.get(url)
    with open(f'{name}.jpg', 'wb') as image_file:
        image_file.write(image_response.content)


def save_image_text(text_dict):
    with open(datetime.now().isoformat() + '.json', 'w') as text_file:
        print('Saving image text...')
        text_file.write(json.dumps(text_dict))


@click.command()
@click.option('-h', '--hashtag', required=True)
@click.option('-n', '--number-of-images', type=int, required=True)
@click.option('-p', '--images-path', required=True, help='Where to save images.')
@click.option(
    '-r', 
    '--retry-count', 
    default=3, 
    required=False,
    help='How many times to retry when an exception is encountered.'
)
def scrape(hashtag, number_of_images, images_path, retry_count):
    os.chdir(images_path)
    

    drv = get_chrome_driver()
    drv.get(get_hashtag_url(hashtag))
    
    scraped_text = {}
    image_uuids = set()

    retries = 0
    while len(image_uuids) < number_of_images:
        
        try:
            all_images = drv.find_elements_by_xpath('//img')

            for image in all_images:
                if (
                        image.id not in image_uuids
                        and len(image_uuids) < number_of_images
                ):
                    image_name = f'{datetime.now().isoformat()}_{image.id}'
                    image_text = image.get_attribute('alt')
                    scraped_text[image_name] = image_text
                    
                    save_image(image.get_attribute('src'), image_name)
                    image_uuids.add(image.id)
                    print(f'Image {len(image_uuids):04d} of {number_of_images:04d} saved.')
                    
                    # Reset retries on success
                    retries = 0
       
        except Exception as exception:
            if retries < retry_count:
                print('An error occurred.', exception, 'Attempting to continue...')
                retries += 1
            else:
                print('Too many errors occured.', exception, 'Exiting...')
                save_image_text(scraped_text)
                exit(1)
        
        drv.execute_script("window.scrollTo(0, document.body.scrollHeight );")
        print('Scrolling to bottom of page...')
        time.sleep(3 + (random.random() * 3))

    save_image_text(scraped_text)


if __name__ == '__main__':
    scrape()
