class Scraper(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_api(self):
        pass

    @abc.abstractmethod
    def get_data(self):
        pass

    @abc.abstractmethod
    def extract_data(self, page_data):
        pass

    @staticmethod
    def _construct_api(**kwargs):
        return {
            'title': kwargs['title'],
            'price_val': kwargs['price_value'],
            'price_curr': kwargs['price_curr'],
            'url': kwargs['base_url'],
            'rating_val': kwargs['rating_val'],
            'rating_over': kwargs['rating_over'],
            'rating': kwargs['rating'],
            'shipping': kwargs['shipping'],
            'short_url': kwargs['short_url']
        }


    @staticmethod
    def update_details(api, time_start, time_end):
        api.update({
            'details': {
                'exec_time': round((time_end - time_start), 2),
                'total_num': len(api['data'])
            }
        })
        return api

    @staticmethod
    def price_formatter(price_value):
        if ' ' in price_value:
            price_value = str(price_value).replace(' ', '')
        if ',' in price_value:
            price_value = price_value.replace(',', '')
        if '$' in price_value:
            price_value = price_value.replace('$', '')
        return float(price_value)

    @staticmethod
    def printer(api):
        api: dict
        for i in api['data']:
            print(f'Title: {i["title"]}')
            print(f'Price: {i["price_val"]}')
            print(f'Rating: {i["rating"]}')
            print('\n\n')