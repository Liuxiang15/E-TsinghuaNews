# -*- coding: utf-8 -*-
import scrapy
from TsinghuaNews.items import TsinghuanewsItem
from scrapy.selector import Selector

import html2text
h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = True


class ThunewsspiderSpider(scrapy.Spider):
    #爬虫名不能和项目名重复
    name = 'THUNewsSpider'
    allowed_domains = ['news.tsinghua.edu.cn']
    current_url = ""

    #头条http://news.tsinghua.edu.cn/publish/thunews/9648/index.html 39
    #综合新闻http://news.tsinghua.edu.cn/publish/thunews/10303/index.html  479
    #start_urls = ['http://news.tsinghua.edu.cn/publish/thunews/9648/2018/20181228102234212361194/20181228102234212361194_.html']
    def start_requests(self):
        #测试先获取10个网址
        
        #注意，只有编号1 2 4 6 7 8 9的网址可以用'//ul[@class="txtlist clearfix"]/li/div/a/@href'获取网址
        #for i in range(9670,9679):
        url_list = [9670, 9671, 9673, 9675, 9676, 9677, 9678]
        page_num_list = [68, 249, 109, 24, 36, 18, 136]
        for index, i in enumerate(url_list):
            for j in range(2, page_num_list[index] + 1):
                yield scrapy.Request(
                    url='http://news.tsinghua.edu.cn/publish/thunewsen/{}/index_{}.html'.format(i, j),
                    callback=self.get_eurls
                )

    
    def get_eurls(self, response):
        #定义一个列表，分别统计九种英语新闻的对应的页面数
        eurl_list = response.selector.xpath('//ul[@class="txtlist clearfix"]/li/div/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        for index, path in enumerate(eurl_list):
            print(domain_name+path)
            yield scrapy.Request(
                url=domain_name+path,
                callback=lambda response, url=domain_name+path:self.e_parse(response, url)
            )
        
    def e_parse(self, response, url):
        enews_item = TsinghuanewsItem()
        enews_item["url"] = url
        enews_item["title"] = response.selector.xpath("//h1/text()").extract_first()
        enews_item["keywords"] = ""
        date_str = url.replace("http://news.tsinghua.edu.cn/publish/thunewsen","")[11:19]
        date_list = []
        #分别添加年月日作为数组元素
        date_list.append(date_str[0:4])
        date_list.append(date_str[4:6])
        date_list.append(date_str[6:8])
        date = date_list[0] + "年" + date_list[1] + "月" + date_list[2] + "日"
        enews_item["date"] = date
        paragraph_list = response.selector.xpath('//article[1]/p').extract()
        content = ""
        for index, paragraph in enumerate(paragraph_list):
            paragraph = h.handle(paragraph)
            paragraph = paragraph.replace("\ue863", "")  # 去除乱码
            paragraph = paragraph.replace("\n", "")  # 去除换行符
            content += paragraph
            if (paragraph == ""):
                continue
            content += "\n"  # 加换行符
        enews_item["content"] = content
        print("-----------------英文解析的数据是：--------------")
        print(enews_item)
        yield enews_item

   
