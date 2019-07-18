# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from lxml import etree
from pymongo import MongoClient
import time
import uuid

client = MongoClient()
collection = client['music']['cloud']

start_url = 'https://music.163.com/discover/playlist/'
browser = webdriver.Chrome()
base_url = 'https://music.163.com'

# 获取html内容
def get_html(url):
    try:
        browser.get(url)
        #切换到iframe
        browser.switch_to_frame('contentFrame')
        html = browser.page_source
        return html
    except TimeoutException:
        print('请求超时')

#处理大分类
def parse_bcate_html(html):
    html = etree.HTML(html)
    #大分类列表
    bcate_list = html.xpath("//div[@id='cateListBox']/div[@class='bd']/dl")
    for bcate in bcate_list:
        item = {}
        #大分类名字
        item['bcate_name'] = bcate.xpath("./dt/text()")[0]
        #中分类列表
        mcate_list = bcate.xpath("./dd/a")
        for mcate in mcate_list:
            #中分类名字
            item['mcate_name'] = mcate.xpath("./text()")[0]
            #中分类url
            item['mcate_url'] = base_url + mcate.xpath("./@href")[0]
            mcate_html = get_html(item['mcate_url'])
            parse_mcate_html(mcate_html,item)

#处理中分类
def parse_mcate_html(html,item):
    html = etree.HTML(html)
    mcate_list = html.xpath("//ul[@id='m-pl-container']/li")
    for mcate in mcate_list:
        #歌单名字
        item['lcate_name'] = mcate.xpath("./div/a/@title")[0]
        #歌单url
        item['lcate_url'] =  base_url + mcate.xpath("./div/a/@href")[0]
        lcate_html = get_html(item['lcate_url'])
        parse_lcate_html(lcate_html,item)

#处理歌单
def parse_lcate_html(html,item):
    html = etree.HTML(html)
    song_list = html.xpath("//table[@class='m-table ']/tbody/tr")
    for song in song_list:
        item['song_title'] = song.xpath("./td[2]//b/@title")[0]
        item['song_length'] = song.xpath("./td[3]/span/text()")[0]
        item['song_singer'] = song.xpath("./td[4]/div/@title")[0]
        item['song_album'] = song.xpath("./td[5]/div/a/@title")[0]
        #生成独立ID
        item['_id'] = uuid.uuid1()
        #print(item)
        #数据插入mongo
        collection.insert(item)


def main():
   html = get_html(start_url)
   parse_bcate_html(html)

if __name__ == '__main__':
    main()

















