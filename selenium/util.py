from selenium import webdriver

def get_chrome_driver(headless=True):
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(chrome_options=chrome_options)
                                    
