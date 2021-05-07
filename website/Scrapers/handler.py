from website.Scrapers.scraper import Scraper
from website.Scrapers.amazon_scraper import amazon_scraper
from website.Scrapers.tapaz_scraper import tapaz_scraper
import requests
import time

class Handler:
    def __init__(self, **kwargs):
        self.PRICE_MAX = 1000000000
        self.currency = None if kwargs['currency'] == 'default' else kwargs['currency']
        self.min_price = 0 if kwargs['min_price'] is None else kwargs['min_price']
        self.max_price = self.PRICE_MAX if kwargs['max_price'] is None else kwargs['max_price']
        self.sort_price_option = None if kwargs['sort_price_option'] == 'default' else kwargs['sort_price_option']
        self.sort_rating_option = None if kwargs['sort_rating_option'] == 'default' else kwargs['sort_rating_option']

    def handle(self, scraper_data):
        if self.currency:
            scraper_data = Filter.by_currency(self, scraper_data)
        if self.min_price != 0 or self.max_price != self.PRICE_MAX:
            scraper_data = Filter.by_price_limits(self, scraper_data)
        if self.sort_price_option:
            scraper_data = Sorter.by_price_options(self, scraper_data)
        elif self.sort_rating_option:
            scraper_data = Sorter.by_rating_options(self, scraper_data)

        return scraper_data



class CurrencyConverter():
	def __init__(self):
		self.data= requests.get('https://api.exchangerate-api.com/v4/latest/USD').json() 
		self.currencies = self.data['rates']


	def convert(self, from_currency, to_currency, amount):
		if from_currency != 'AZN' : 
			amount = amount * self.currencies[from_currency] 
		amount = round(amount * self.currencies[to_currency], 2) 
		return amount 

class Filter(Handler):
    def by_currency(self,api):
        converter = CurrencyConverter()
        for data in api['data']:
            if self.currency == 'USD':
                if data['price_curr'] == 'AZN':
                    data['price_val'] = converter.convert('USD', 'AZN', data['price_val'])
                elif data['price_curr'] == 'RUB':
                    data['price_val'] = converter.convert('USD', 'RUB', data['price_val'])
                data['price_curr'] = 'USD'
            elif self.currency == 'AZN':
                if data['price_curr'] == 'USD':
                    data['price_val'] = converter.convert('AZN', 'USD', data['price_val'])
                elif data['price_curr'] == 'RUB':
                    data['price_val'] = converter.convert('AZN', 'USD', data['price_val'])
                data['price_curr'] = 'AZN'
            elif self.currency == 'RUB':
                if data['price_curr'] == 'USD':
                    data['price_val'] = converter.convert('RUB', 'USD', data['price_val'])
                elif data['price_curr'] == 'AZN':
                    data['price_val'] = converter.convert('RUB', 'AZN', data['price_val'])
                data['price_curr'] = 'RUB'

        return api
    
    def by_price_limits(self, api):
        api['data'] = filter(lambda x: self.max_price > x['price_val'] >= self.min_price, api['data'])
        return api    


class Sorter(Handler):

    def by_price_options(self, api):
        api['data'] = sorted(api['data'], key=lambda x: x['price_val'], reverse=(self.sort_price_option == 'descending'))
        return api

    def by_rating_options(self, api):
        api['data'] = sorted(api['data'], key=lambda x: x['rating_val'], reverse=(self.sort_rating_option == 'descending'))
        return api



class Distributor:
    def __call__(self, **kwargs):
        self.websites: list = kwargs['websites']
        self.full_api = {'tapaz': {}, 'amazon': {}}

        possible_websites = {'tapaz': Tapaz_scraper, 'amazon': Amazon_scraper}
        total_product_num = 0

        time_start = time.time()

        for website, iterscraper in possible_websites.items():
            if website in self.websites:
                scraper: Scraper = iterscraper(item=kwargs['item'], mode=kwargs['mode'])  
                options: Handler = Handler(currency=kwargs['currency'], min_price=kwargs['min_price'],
                                           max_price=kwargs['max_price'], sort_price_option=kwargs['sort_price_option'],
                                           sort_rating_option=kwargs['sort_rating_option'])

                scraped_data_api = scraper.get_api()
                handled = options.handle(scraped_data_api)

                self.full_api.update({website: handled})
                total_product_num += handled['details']['total_num']

        time_end = time.time()

        self.full_api.update({
            'details': {
                'exec_time': round(time_end - time_start, 2),
                'total_num': total_product_num
            }
        })

        return self.full_api