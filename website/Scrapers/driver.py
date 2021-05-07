from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions
from selenium import webdriver

class Driver:
    def __init__(self, headless):
        self.options = ChromeOptions()
        self.headless = headless
        self.options.add_argument("--window-size=1600, 490")
        self.options.add_argument("--disable-infobars")
        self.options.headless = self.headless
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
        self.driver.implicitly_wait(30)

    def get_driver(self):
        return self.driver

    def stop_driver(self):
        print('>> Quiting and closing the browser')
        self.driver.close()
        self.driver.quit()


amazon_driver = Driver(True)
tapaz_driver = Driver(True)