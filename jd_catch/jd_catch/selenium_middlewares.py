import time
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class SeleniumMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        options = Options()
        # options.add_argument('--headless')  # 启用无头模式
        self.driver = webdriver.Chrome(options=options)


    def spider_closed(self, spider):
        self.driver.quit()

    def process_request(self, request, spider):
       if request.meta.get("middleware")=="SeleniumMiddleware":
           self.driver.get(request.url)
           try:
               WebDriverWait(self.driver, 60).until(
                   EC.presence_of_element_located((By.XPATH, '//*[@class="text"]'))
               )
               self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
               time.sleep(0.5)
               body = self.driver.page_source.encode('utf-8')
               return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
           except TimeoutError:
               return False

