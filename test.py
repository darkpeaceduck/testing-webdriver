import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from market_objects import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
import time
import os
import sys

class MarketObjectTest(unittest.TestCase):
    URL = "https://market.yandex.ru/product/1720217048?hid=91491&track=tabs"
    DRIVER_PATH ="chromedriver"
    def setUp(self):
        driver_path =os.path.abspath(self.DRIVER_PATH)
        self.driver = webdriver.Chrome(driver_path) 

    def not_none(self, obj):
        return self.assertTrue(obj != None)
    
    def header_test(self, header):
        self.not_none(header.title())
        self.not_none(header.price())
        self.not_none(header.image().get())
        self.not_none(header.product_toolbar().wishlist_button())
        self.not_none(header.product_toolbar().hint_button())
        self.not_none(header.offer_button())

    def __test_haractericrics_tab(self, page):
        self.assertTrue(len(page.haractericrics_list()) > 0)
        self.header_test(page.header())

    def __price_tab_test_range(self, page, range_from, range_to):
        page.filter_element().from_price(range_from)
        page.filter_element().to_price(range_to)
        page.filter_element().submit_button().click()
        for item in page.snippet_cards():
            price = item.price()
            self.assertTrue(range_from <= price and price <= range_to)
#      
    def __test_price_tab(self, page):
        self.header_test(page.header())
        self.not_none(page.results_window())
          
        ranges = [(0, 100000), (100000, 0), (1000, 2000), (2000, 5000), (5000, 10000)]
        for (fr, to) in ranges:
            self.__price_tab_test_range(page, fr , to)

    def __test_maps_tab(self, page): 
        self.header_test(page.header())
        self.not_none(page.maps())
#         
    def __test_reviews_tab(self, page): 
        self.header_test(page.header())
        self.not_none(page.reviews())
#     
    def __test_articles_tab(self, page): 
        self.header_test(page.header())
        self.not_none(page.articles())
# 
    def __test_forum_tab(self, page): 
        self.header_test(page.header())
        self.not_none(page.forum())
#         
    def __test_title_tab(self, page):
        self.not_none(page.summary().title())
        self.not_none(page.summary().price())
        self.not_none(page.summary().spec_list())
        self.not_none(page.summary_gallery().image().get())
        self.not_none(page.average_price())
        self.not_none(page.product_toolbar().wishlist_button())
        self.not_none(page.product_toolbar().hint_button())
        self.not_none(page.offer_button())


    def test_ctl(self):
        self.driver.get(self.URL)
        panel = CtlPanel(self.driver)
        self.not_none(panel.get_items())
        
        
        self.__test_haractericrics_tab(panel.chracterictics_page())
        self.__test_price_tab(panel.prices_page())
        self.__test_maps_tab(panel.map_page())
        self.__test_reviews_tab(panel.reviews_page())
        self.__test_articles_tab(panel.articles_page())
        self.__test_forum_tab(panel.forum_page())
        self.__test_title_tab(panel.title_page())

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("using [URL] [DRIVER RELATIVE PATH]")
    else:
        MarketObjectTest.URL= sys.argv[1]
        MarketObjectTest.DRIVER_PATH= sys.argv[2]
        sys.argv.pop()
        sys.argv.pop()
        unittest.main()