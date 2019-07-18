# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from MUSIC.settings import UserAgent_List
import random

class RandomUserAgentMiddlewares():
    def process_request(self,request,spider):
        random_useragent = random.choice(UserAgent_List)
        request.headers['user-agent'] = random_useragent
