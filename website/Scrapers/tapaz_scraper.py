from bs4 import BeautifulSoup
import time
from website.Scrapers.driver import driver
from website.Scrapers.scraper import scraper

class tapaz_scraper(Scraper):
    def __init__(self, **kwargs):
        self.item = kwargs['item']
        self.mode = kwargs['mode']
        self.timeout = 0.4
        self.driver = tapaz_driver.get_driver()
        self.url = 'https://tap.az/elanlar?&keywords=' + self.item.replace('', '+')
        self.short_url = 'www.tap.az'
        self.product_api = {}

        def get_data(self):
        global time_start
        time_start = time.time()

        self.driver.get(self.url)

        if self.mode == 'fast':
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.timeout)
        elif self.mode == 'slow':
            number_of_scrolls = 0
            reached_page_end = False
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while not reached_page_end:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.timeout)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if last_height == new_height:
                    reached_page_end = True
                else:
                    last_height = new_height
                number_of_scrolls += 1

        return self.driver.page_source

    def extract_data(self, page_data):
        final_page = page_data
        start_string = '<div class="js-endless-container products endless-products">'
        end_string = '<div class="pagination_loading">'
        main_html = str(final_page)[str(final_page).find(start_string):]
        main_html = main_html[:main_html.find(end_string)]

        soup = BeautifulSoup(main_html, 'lxml')
        product_list = soup.select("div[class^=products-i]")
        api = {'data': []}

        rating_val = '0'
        rating_over = '5'
        rating = None
        shipping = None

        for item in product_list:
            for link in item.find_all('a', target='_blank', href=True):
                try:
                    base_url = 'https://tap.az/' + link['href']
                    title = link.find('div', class_='products-name').text
                    price_value = self.price_formatter(link.find('span', class_='price-val').text)
                    price_curr = link.find('span', class_='price-cur').text
                except:
                    continue

                api['data'].append(self._construct_api(title=title, price_value=price_value, price_curr=price_curr,
                                                      base_url=base_url, rating_val=rating_val, rating_over=rating_over,
                                                      rating=rating, shipping=shipping, short_url=self.short_url))

        time_end = time.time()
        self.update_details(api, time_start=time_start, time_end=time_end)
        return api

    def get_api(self):
        page_data = self.get_data()
        self.product_api = self.extract_data(page_data=page_data)
        return self.product_api