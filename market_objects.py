from selenium import webdriver
import os
from pydoc import browse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


class BasePage(object):
    PAGE_LOAD_TIMEOUT=30
    def __init__(self, driver, waiting=True):
        self.driver = driver
        if waiting:
            try:
                WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(\
                    lambda x: x.find_element_by_class_name("main"))
            except:
                pass
    
    class text_to_change(object):
        def hash(self, driver):
            return driver.find_element_by_class_name("b-page").get_attribute("data-reqid-chain")
        def __init__(self, driver):
            self.driver = driver
            self.text = self.hash(driver)
    
        def __call__(self, _):
            actual_text = self.hash(self.driver)
            return actual_text != self.text
        
    @staticmethod
    def action(function):
            def wrapper(self, *args, **kwargs):
                text_to_change = self.text_to_change(self.driver)
                function(self, *args, **kwargs)
                try:
                    WebDriverWait(self.driver, BasePage.PAGE_LOAD_TIMEOUT).until(text_to_change)
                except:
                    pass
            return wrapper
        
class BaseElement(BasePage):
    def __init__(self, driver, element):
        super().__init__(driver, waiting=False)
        self.element = element
        
class SpecList(BaseElement):
    def items(self):
        return self.element.find_elements_by_tag_name("li")
        
        
class ProductSummaryContent(BaseElement):
    def title(self):
        return self.element.find_element_by_class_name("title")
    def price(self):
        return self.element.find_element_by_class_name("price")
    def spec_list(self):
        return SpecList(self.driver, self.element.find_element_by_class_name("n-product-spec-list"))

class Image(BaseElement):
    def get(self):
        return self.element.find_element_by_class_name("image")
        
class SummaryGallery(BaseElement):
    def image(self):
        return Image(self.driver, \
                     self.element.find_element_by_class_name("n-gallery__image-container"))

class ProductToolbar(BaseElement):
    def wishlist_button(self):
        return self.element.find_elements_by_tag_name("a")[0]
    def hint_button(self):
        return self.element.find_elements_by_tag_name("a")[1]
    

    
class Header(BaseElement):
    def __init__(self, driver, init_element):
        super().__init__(driver, init_element.find_element_by_class_name("n-product-headline"))
    def product_toolbar(self):
        return ProductToolbar(self.driver, self.element.find_element_by_class_name("n-product-toolbar"))
    def image(self):
        return Image(self.driver, self.element.find_element_by_class_name("n-product-headline__view"))
    def title(self):
        return ProductSummaryContent(self.driver, self.element).title()
    def price(self):
        return ProductSummaryContent(self.driver, self.element).price()
    def offer_button(self):
        return self.element.find_element_by_class_name("n-offer-action").find_element_by_tag_name("a")
        
class MarketItemPage(BasePage):
    def summary(self):
        return ProductSummaryContent(self.driver, self.driver\
            .find_element_by_class_name("n-product-summary__content"))
    def summary_gallery(self):
        return SummaryGallery(self.driver, self.driver\
            .find_element_by_class_name("n-product-summary__gallery"))
    def average_price(self):
        return  self.driver.find_element_by_class_name("n-w-product-average-price__average-value")\
            .find_element_by_class_name("price")
    def product_toolbar(self):
        return ProductToolbar(self.driver, self.driver\
              .find_element_by_class_name("n-product-summary-toolbar")    \
              .find_element_by_class_name("n-product-toolbar"))
    def offer_button(self):
        return self.driver\
              .find_element_by_class_name("n-product-summary-toolbar") \
              .find_element_by_class_name("n-offer-action")\
              .find_element_by_tag_name("a")


class HeaderPage(BasePage):
    def header(self):
        return Header(self.driver, self.driver)
    
class HaractericricsPage(HeaderPage):
    def haractericrics_list(self):
        return self.driver.find_elements_by_class_name("n-product-spec-wrap__body")
    
    
class Button(BaseElement):
    @BasePage.action
    def click(self):
        return self.element.click()
    
    
class FilterPanel(BaseElement):
    def __price_body(self):
        return self.element.find_elements_by_class_name("n-filter-block__body")[0]
    def __send_keys(self, element, keys):
        element.clear()
        element.send_keys(str(keys))
    @BasePage.action
    def from_price(self, price):
        element = self.__price_body()\
            .find_elements_by_class_name("input")[0]\
            .find_element_by_class_name("input__control")
        self.__send_keys(element, price)
        
    @BasePage.action
    def to_price(self, price):
        element = self.__price_body().find_elements_by_class_name("input")[1].find_element_by_class_name("input__control")
        self.__send_keys(element, price)
        
    
    def submit_button(self):
        return Button(self.driver, self.element.find_element_by_class_name("button_action_n-filter-apply"))
    
class SnippetCard(BaseElement):
    def price(self):
        text = self.element.find_element_by_class_name("price").text
        price_str = []
        for item in text.split():
            try:
                int(item)
                price_str.append(item)
            except:
                pass
        return int(''.join(price_str))
    
class PricePage(HeaderPage):
    def results_window(self):
        return self.driver.find_elements_by_class_name("i-product-offers__content")[0]
    def filter_element(self):
        return FilterPanel(self.driver, \
                           self.driver.find_elements_by_class_name("n-filter-panel-aside__content")[1])
    def snippet_cards(self):
        return list(map(lambda x : SnippetCard(self.driver, x), \
                        self.results_window().find_elements_by_class_name("snippet-card")))
        
    def sort_price(self):
        script_params='{"n-filter-sorter":{"options":[{"id":"aprice","type":"asc"},{"id":"dprice","type":"desc"}],"place":"offers"}}'
        elements = self.driver.find_elements_by_class_name("n-filter-sorter")
        for e in elements:
            if (e.get_attribute("data-bem") == script_params):
                return Button(self.driver, e)
        return None
    
    def __button_next_elem(self):
        return self.driver.find_element_by_class_name("n-pager__button-next")
    def button_next(self):
        return Button(self.driver, self.__button_next_elem())
    def has_button_next(self):
        try:
            elem = self.__button_next_elem() 
            return True
        except:
            return False
    
class MapPage(HeaderPage):
    def __init__(self, driver):
        super().__init__(driver)
        WebDriverWait(driver, self.PAGE_LOAD_TIMEOUT).until(\
            lambda x: x.find_element_by_tag_name("ymaps"))
    def maps(self):
        return  self.driver.find_element_by_tag_name("ymaps")      
    
class ReviewsPage(HeaderPage):
    def reviews(self):                   
        return  self.driver.find_element_by_class_name("reviews-layout")
    
class ArticlesPage(HeaderPage):
    def articles(self):
        return  self.driver.find_element_by_class_name("product-articles")
    
class ForumPage(HeaderPage):
    def forum(self):
        return  self.driver.find_element_by_class_name("n-product-forum")
    
    
class CtlPanel(BaseElement):
    def __init__(self, driver):
        super().__init__(driver, driver.find_elements_by_class_name("n-product-tabs__item"))
        self.reload()
        
    def reload(self):
        self.element = self.driver.find_elements_by_class_name("n-product-tabs__item")
        self.tabs = [None] * 10
        for tab in self.element:
            data_name = tab.get_attribute("data-name")
            index = 0;
            dic = {
                "product" : 0,
                "spec" : 1,
                "offers" : 2,
                "geo" : 3,
                "reviews" : 4,
                "articles" : 5,
                "forums" : 6
            }
            self.tabs[dic[data_name]] = tab
        return self.element
    
    def get_items(self):
        return self.tabs
    
    def title_page(self):
        self.reload()
        Button(self.driver, self.get_items()[0]).click()
        return MarketItemPage(self.driver)
    
    def chracterictics_page(self):
        self.reload()
        Button(self.driver, self.get_items()[1]).click()
        return HaractericricsPage(self.driver)
    
    def prices_page(self):
        self.reload()
        Button(self.driver, self.get_items()[2]).click()
        return PricePage(self.driver)
    
    def map_page(self):
        self.reload()
        Button(self.driver, self.get_items()[3]).click()
        return MapPage(self.driver)
    
    def reviews_page(self):
        self.reload()
        Button(self.driver, self.get_items()[4]).click()
        return ReviewsPage(self.driver)
    
    def articles_page(self):
        self.reload()
        Button(self.driver, self.get_items()[5]).click()
        return ArticlesPage(self.driver)
    
    def forum_page(self):
        self.reload()
        Button(self.driver, self.get_items()[6]).click()
        return ForumPage(self.driver)