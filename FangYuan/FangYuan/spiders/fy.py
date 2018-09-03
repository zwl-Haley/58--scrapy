# -*- coding: utf-8 -*-
import scrapy
import re
import jsonpath
from FangYuan.items import FangyuanItem
import time
from FangYuan.cityList import cityList

class ErshoufangSpider(scrapy.Spider):
    name = 'fy'
    allowed_domains = ['luna.58.com']

    # scrapy crawl fy -a city=武汉 接收参数
    def __init__(self, city=None,*args, **kwargs):
        super(ErshoufangSpider, self).__init__(*args, **kwargs)
        self.city = city

    def start_requests(self):
        city_code = jsonpath.jsonpath(cityList,"$..{}".format(self.city))[0].split("|")[0]
        start_urls = ['https://luna.58.com/m/autotemplate?city={}&temname=ershoufang_common'.format(city_code),'https://luna.58.com/m/autotemplate?city={}&temname=zufang_common'.format(city_code)]
        for url in start_urls:
            yield scrapy.Request(url,dont_filter = True)

    def parse(self, response):
        text = response.body.decode('utf-8') #将response转为字符串用正则提取linkUrl
        linkUrl = re.findall(r'"linkUrl":"(https://luna.58.com/list.shtml\?plat=m.*?)"',text)
        city = re.findall(r'href=".*?class="city">(.*?)</a>',text)[0]
        for link in linkUrl:
            #此处为ajex加载，pn表示页数，大概看了下所有商品不会超过20页
            links = [link + "&pn=" +str(pn) for pn in range(1,21)]
            for url in links: 
                yield scrapy.Request(url,callback=self.parse_shop,meta={"city":city})

    def parse_shop(self,response):
        text = response.body.decode('utf-8')
        try:
            shouID = re.findall(r'"infoId":"([0-9]*?)"',text)
            shouID = list(set(shouID))
            for id in shouID:
                shopUrl = "https://luna.58.com/info/"+id
                yield scrapy.Request(shopUrl,callback=self.parse_info,meta={"shopUrl":shopUrl,"city":response.meta["city"]})
        except Exception as e:
            print("parse_shop错误：",e)

    def parse_info(self,response):
        shopUrl = response.meta["shopUrl"]
        item = FangyuanItem()
        text = response.body.decode('utf-8')
        try:
            name = re.findall(r'"contactperson":"(.*?)"',text)[0]
            phone = re.findall(r'"phone":"([0-9]*?)"',text)[0]
            post_time = re.findall(r'"postdate":"([0-9-]*?)"',text)[0]
            cmmtype = re.findall(r'"cmmtype":"(\d)"',text)[0] #经纪人还是个人“1”表示个人,“0”表示经纪人

            timeArray = time.strptime(post_time, "%Y-%m-%d")   #转换成时间数组
            timestamp = time.mktime(timeArray)   #转换成时间戳
            now_time = int(time.time())
            if now_time-timestamp > 86400*30 or int(cmmtype)==0:
                print("此信息不符合条件,过滤")

            else:
                # item["shopUrl"] = shopUrl
                item["time"] = post_time
                item["name"] = name + "(个人)"
                item["phone"] = phone
                item["city"] = response.meta["city"]
                yield item
        except Exception as e:
            print("parse_info错误：",e)
