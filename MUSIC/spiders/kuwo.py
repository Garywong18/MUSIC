# -*- coding: utf-8 -*-
import scrapy
import json
import uuid
class KuwoSpider(scrapy.Spider):
    name = 'kuwo'
    allowed_domains = ['kuwo.cn']
    start_urls = ['http://kuwo.cn/']

    def start_requests(self):
        for i in range(1,244):
            # 遍历歌手列表页
            url = 'http://www.kuwo.cn/api/www/artist/artistInfo?category=0&pn={}&rn=102'.format(i)
            yield scrapy.Request(
                url,
                callback=self.parse
            )

    def parse(self, response):
        res = response.text
        data = json.loads(res)
        # 遍历每页的歌手
        for singer in data['data']['artistList']:
            item = {}
            item['singer_name'] = singer['name']
            item['artistFans'] = singer['artistFans']
            item['singer_id'] = singer['id']
            # 歌手歌曲列表第一页
            home_url = 'http://www.kuwo.cn/api/www/artist/artistMusic?artistid={}&pn=1&rn=30'.format(item['singer_id'])
            yield scrapy.Request(
                home_url,
                callback=self.parse_song_list,
                meta={'item':item}
            )


    def parse_song_list(self,response):
        index = 1
        item = response.meta['item']
        res = response.text
        data = json.loads(res)
        # 获取歌曲总页数
        sum_page = int(data['data']['total'])//30 + 1
        # 遍历每页的歌曲
        for song in data['data']['list']:
            item['song_album'] = song['album']
            item['song_length'] = song['songTimeMinutes']
            item['song_name'] = song['name']
            item['song_id'] = song['rid']
            item['_id'] = uuid.uuid1()
            yield item
        # 翻页
        while index < sum_page:
            index += 1
            next_url = 'http://www.kuwo.cn/api/www/artist/artistMusic?artistid={}&pn={}&rn=30'.format(item['singer_id'],index)
            yield scrapy.Request(
                next_url,
                callback=self.parse_song_list,
                meta={'item':item}
            )

