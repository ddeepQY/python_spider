# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdCatchItem(scrapy.Item):
    goods_title = scrapy.Field()  # 商品名称
    goods_price = scrapy.Field()  # 价格
    goods_link = scrapy.Field()  # 商品链接
    goods_img = scrapy.Field()  # 商品图片
    goods_shop = scrapy.Field()  # 店铺名称
    goods_comments = scrapy.Field()  # 评价数
    goods_rating = scrapy.Field()  # 商品好评度
    goods_tags = scrapy.Field()  # 商品评价标签
    comment_detail = scrapy.Field()  # 当前商品评价信息
    is_self = scrapy.Field()  # 是否自营
    is_discount = scrapy.Field()  # 是否参加秒杀
    is_fullMinus = scrapy.Field()  # 是否参加满减
