import scrapy
from ..items import JdCatchItem
import re

class JdSpiderSpider(scrapy.Spider):
    name = "jd_spider"
    start_urls = ["https://search.jd.com/Search?keyword=%E5%B0%8F%E7%B1%B314pro&pvid=403d89c1a3104542bfca9214fc7fb8b8&isList=0&page=1"]
    page=1

    def start_requests(self) :
        url=self.start_urls[0]
        yield scrapy.Request(url,meta={'middleware':'SeleniumMiddleware'})
    # 爬取商品搜索页
    def parse(self, response):
        goods_list=response.css('.gl-item')
        for node in goods_list:
            item=JdCatchItem()
            # 获取商品标题
            goods_title=node.xpath('./div/div[4]/a/em//text()').extract()
            goods_title=' '.join(goods_title).strip()
            item['goods_title']=goods_title
            # 获取商品图片
            goods_img = node.xpath('./div/div[1]/a/img/@src').get() if node.xpath('./div/div[1]/a/img/@src').get() else node.xpath('./div/div[1]/a/img/@data-lazy-img').get()
            if goods_img.endswith('.avif'):
                goods_img = goods_img.replace('.avif', '')
            item['goods_img']=f'https:{goods_img}'
            # 获取商品详情页链接
            goods_link="https:"+node.xpath('./div/div[1]/a/@href').get()
            item['goods_link']=goods_link
            # 获取商品价格
            goods_price='￥'+node.xpath('./div/div[3]/strong/i/text()').get()
            item['goods_price']=goods_price
            #获取评价数
            goods_comments=node.xpath('./div/div[5]/strong/a/text()').get()
            item['goods_comments']=f'{goods_comments}条评论'
            #获取店铺名称
            goods_shop=node.xpath("./div/div[7]/span/a/text()").get()
            item['goods_shop']= goods_shop
            # 获取商品标签
            goodsD=node.xpath('./div/div[8]').get()
            pattern = r'<i[^>]*>(.*?)</i>'
            goodsD = re.findall(pattern, goodsD)
            goodsD=' '.join(goodsD)
            if goodsD:
                if '自营' in goodsD:
                    item['is_self']=1
                else:
                    item['is_self']=0
                if '满' or '券' in goodsD:
                    item['is_fullMinus']=1
                else:
                    item['is_fullMinus']=0
                if '秒' in goodsD:
                    item['is_discount']=1
                else:
                    item['is_discount']=0
            else:
                item['is_self'] = 0
                item['is_discount'] = 0
                item['is_fullMinus'] = 0
            yield scrapy.Request(url=f'{item["goods_link"]}#comment',meta={'item': item,'middleware':'SeleniumMiddleware'}, callback=self.goodsParse, errback=self.errback_httpbin)
        if self.page<3:
            self.page+=2
            yield scrapy.Request(url=self.start_urls[0].replace('page=1',f'page={self.page}'),meta={'middleware':'SeleniumMiddleware'},errback=self.errback_httpbin)
    # 详情页
    def goodsParse(self,response):
        item=response.meta['item']
        html=response
        #获取好评度
        goods_rating=html.xpath('//*[@id="comment"]/div[2]/div[1]/div[1]/div/text()').extract()
        goods_rating=goods_rating[0] if goods_rating else '0'
        item['goods_rating']=f'{goods_rating}%'
        # 获取商品标签
        goods_tags=html.xpath('//*[@id="comment"]/div[2]/div[1]/div[2]/div//span/text()').extract()
        goods_tags=" ".join(goods_tags)
        goods_tags=goods_tags if goods_tags else "暂无标签"
        item['goods_tags']=goods_tags
        # 获取好评数
        goods_comment_good=html.xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[5]/a/em/text()').get()
        # 获取中评数
        goods_comment_normal=html.xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[6]/a/em/text()').get()
        # 获取差评数
        good_comment_bad=html.xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[7]/a/em/text()').get()
        # 评论内容处理
        comment_detail={"总评数":item['goods_comments'],"好评数":goods_comment_good,"中评数":goods_comment_normal,"差评数":good_comment_bad,"商品评价":[]}
        comment_list=html.css(".comment-item")
        item['comment_detail']=[]
        # 评论详情内容处理
        for comment in comment_list:
            # 获取评论星数
            comment_star = comment.xpath('./div[2]/div[1]/@class').get()
            pattern = r'\d+'
            comment_star = f'{re.search(pattern, comment_star).group()}星'
            # 获取评论文本内容
            comment_text=comment.xpath('./div[2]/p/text()').get()
            # 获取评论图片链接
            comment_img=comment.xpath('./div[2]/div[2]/a/img/@src').extract()
            if(comment_img):
                for i,img in enumerate(comment_img):
                    if img[0:6]!="https:" :
                        comment_img[i]=f'https:{img}'
            # 获取评论商品链接
            comment_video=comment.xpath('./div[2]/div[4]/div/@src').extract()
            comment_content={"评价星数":comment_star,"评论内容":comment_text,"评论图片":comment_img,"评价视频":comment_video}
            comment_detail["商品评价"].append(comment_content)
        item['comment_detail']=comment_detail
        print(f'已爬取{item["goods_link"]} {item["goods_img"]}')
        yield item

    def errback_httpbin(self, failure):
        self.logger.info(repr(failure))




