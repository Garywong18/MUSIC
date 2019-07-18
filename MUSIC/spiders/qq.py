# -*- coding: utf-8 -*-
import scrapy
import json
from copy import deepcopy

class QqSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['qq.com']
    start_urls = ['https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_tag_conf.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0']
    # 中分类基础url
    m_base_url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.01693556805001384&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&categoryId={}&sortId=5&sin={}&ein={}'
    # 小分类基础url
    s_base_url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={}&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
    # 需要重写父类添加referer，否则爬取数据为空
    referer = 'https://y.qq.com/portal/playlist.html'
    # 用于翻页
    i = 0
    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            headers={'referer':self.referer},
            callback=self.parse
        )
    # 处理分类
    def parse(self, response):
        dic = json.loads(response.text)
        b_cate_list = dic['data']['categories']
        # 去掉热门分类
        for b_cate in b_cate_list[1:6]:
            item = {}
            # 大分类名称
            item['b_cate_name'] = b_cate['categoryGroupName']
            m_cate_list = b_cate['items']
            for m_cate in m_cate_list:
                # 中分类名称
                item['m_cate_name'] = m_cate['categoryName']
                item['m_cate_Id'] = m_cate['categoryId']
                if item['m_cate_Id'] is not None:
                    item['m_cate_url'] = self.m_base_url.format(item['m_cate_Id'],0,29)
                    yield scrapy.Request(
                        item['m_cate_url'],
                        callback=self.parse_list,
                        headers={'referer':self.referer},
                        meta={'item':deepcopy(item)}
                    )
    # 处理歌单列表
    def parse_list(self,response):
        item = response.meta['item']
        dic = json.loads(response.text)
        s_cate_list = dic['data']['list']
        for s_cate in s_cate_list:
            # 小分类名称(歌单名称)
            item['s_cate_name'] = s_cate['dissname']
            # 播放量
            item['listen_num'] = s_cate['listennum']
            # 歌单id
            item['s_cate_Id'] = s_cate['dissid']
            if item['s_cate_Id'] is not None:
                s_cate_url = self.s_base_url.format(item['s_cate_Id'])
                # 此处需要单独构造referer
                base_referer = 'https://y.qq.com/n/yqq/playsquare/{}.html'
                yield scrapy.Request(
                    s_cate_url,
                    callback=self.parse_song_list,
                    headers={'referer':base_referer.format(item['s_cate_Id'])},
                    meta={'item':deepcopy(item)}
                )

        # 歌单翻页
        if len(s_cate_list) == 30:
            self.i = self.i + 1
            next_page_url = self.m_base_url.format(item['m_cate_Id'],0+30*self.i,29+30*self.i)
            yield scrapy.Request(
                next_page_url,
                callback=self.parse_list,
                headers={'referer':self.referer},
                meta={'item':item}
            )

    # 获取歌曲详情
    def parse_song_list(self,response):
        item = response.meta['item']
        dic = json.loads(response.text)
        song_list = dic['cdlist'][0]['songlist']
        for song in song_list:
            item['song_name'] = song['songname']
            item['song_singer'] = []
            for singer in song['singer']:
                item['song_singer'].append(singer['name'])
            item['song_album'] = song['albumname']
            item['song_id'] = song['songid']
            # mongodb出现ID重复，所以自己生成ID
            item['_id'] = str(item['song_id']) + str(item['m_cate_Id']) + str(item['s_cate_Id'])
            print(item)
            yield item


