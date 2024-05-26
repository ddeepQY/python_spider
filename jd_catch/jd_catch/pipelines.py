# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import time
from itemadapter import ItemAdapter
from urllib.parse import urlparse
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import pymongo
import fake_useragent
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

class JdCatchPipeline:
    def process_item(self, item, spider):
        return item

class MyImagesPipeline(ImagesPipeline):
    IMAGES_STORE = get_project_settings().get('IMAGES_STORE')
    def get_media_requests(self, item, spider):
        ua = fake_useragent.UserAgent()
        header = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
        header['User-Agent'] = ua.random
        yield scrapy.Request(url=item['goods_img'], meta={'item': item}, headers=header)
    def file_path(self, request, response=None, info=None,*,item=None):
            item = request.meta['item']
            parsed_url = urlparse(item['goods_img'])
            filename = (str(parsed_url.path.split('/')[-1]))
            return filename

    def item_completed(self, results, item, info):
        return item

class MyMongoDbPipeline:

    def __init__(self):
        self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_db = 'jd_database'
        self.mongo_collection = 'jd_collection'
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item["goods_comments"] = item["goods_comments"].replace('万', '0000')
        self.db[self.mongo_collection].insert_one(ItemAdapter(item).asdict())
        return item
