# -*- coding: utf-8 -*-
import os
import sys

citys = sys.argv[1:]

for city in citys:
    cmd = "scrapy crawl fy -a city={}".format(city)
    os.system(cmd)

