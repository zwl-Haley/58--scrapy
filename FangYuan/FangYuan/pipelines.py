# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
import datetime

class FangyuanPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host = "127.0.0.1",
            port = 3306,
            db = "tongcheng",
            user = "root",
            passwd = "",
            charset = 'utf8',
            use_unicode = True
            )
        self.cursor = self.connect.cursor()
    print("连接数据库成功，正在存入数据库...")

    def process_item(self, item, spider):
        sql = "SELECT phone FROM info1 WHERE phone = %s;"%item['phone']
        status = self.cursor.execute(sql)
        if status == 0:
            self.cursor.execute(
                """insert into info1(create_time,cname, phone, city, post_time)
                value (%s,%s, %s, %s, %s)""",
                (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 item['name'],
                 item['phone'],
                 item["city"],
                 item['time']
                 ))
            self.connect.commit()
        else:pass
        return item

    def close_spider(self,spider):
        self.connect.close()


# CREATE TABLE info (
#     auto_id INT NOT NULL primary key AUTO_INCREMENT,
#     create_time DateTime NOT NULL,
#     cname VARCHAR(20),
#     phone VARCHAR(20),
#     city VARCHAR(20),
#     post_time VARCHAR(20));

