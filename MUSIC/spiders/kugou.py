# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import uuid

class KugouSpider(scrapy.Spider):
    name = 'kugou'
    allowed_domains = ['kugou.com']
    #start_urls = ['https://www.kugou.com/yy/singer/index/1-a-1.html']

    def start_requests(self):
        #遍历大页
        for i in self.settings['PAGE_LIST']:
            #遍历小页
            for j in range(1,6):
                url = 'https://www.kugou.com/yy/singer/index/{}-{}-1.html'.format(j,i)
                yield scrapy.Request(
                    url,
                    callback=self.parse
                )

    def parse(self, response):
        #页面上部TOP18的明星
        singer_list1 = response.xpath("//ul[@id='list_head']/li")
        for singer in singer_list1:
            item = {}
            #歌手名字
            item['singer_name'] = singer.xpath("./a/@title").extract_first()
            #歌手主页
            item['home_url'] = singer.xpath("./a/@href").extract_first()
            yield scrapy.Request(
                item['home_url'],
                callback=self.parse_song_list,
                meta={'item':deepcopy(item)}
            )
        #页面下部19-50的明星
        ul_list = response.xpath("//div[@id='list1']/ul")
        for ul in ul_list:
            singer_list2 = ul.xpath("./li")
            for singer2 in singer_list2:
                item = {}
                item['singer_name'] = singer2.xpath("./a/@title").extract_first()
                item['home_url'] = singer2.xpath("./a/@href").extract_first()
                #print(item)
                yield scrapy.Request(
                    item['home_url'],
                    callback=self.parse_song_list,
                    meta={'item':deepcopy(item)}
                )


    def parse_song_list(self,response):
        item = response.meta['item']
        song_list = response.xpath("//ul[@id='song_container']/li")
        for song in song_list:
            #歌曲名字
            item['song_name'] = song.xpath("./a/span[@class='text']/@title").extract_first()
            #防止MongoDB存入时ID重复，自己生成_id
            item['_id'] = uuid.uuid1()
            yield item





