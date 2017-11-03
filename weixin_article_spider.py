#!/usr/bin/python
# coding: utf-8

from pyquery import PyQuery as pq
from pyExcelerator import *  # 导入excel相关包
import codecs
import requests
import time
import datetime
import os
import sys
from parse_article import parse_article

reload(sys)
sys.setdefaultencoding('utf-8')
'''
http://weixin.sogou.com/weixin?type=2&query=%E7%94%B7%E8%B6%B3&ie=utf8&s_from=input&_sug_=y&_sug_type_=
http://weixin.sogou.com/weixin?query=%E7%94%B7%E8%B6%B3&_sug_type_=&s_from=input&_sug_=y&type=2&page=2&ie=utf8
'''

class weixin_article_spider:

    def __init__(self, keywords, parse_article, page_size=1):
        self.parse_article = parse_article
        self.keywords = keywords
        self.page_size = page_size

        self.sogou_search_url_p1 = "http://weixin.sogou.com/weixin?query=" + \
                                   self.keywords + \
                                   "&_sug_type_=&s_from=input&_sug_=y&type=2&page="

        self.sogou_search_url_p2 = "&ie=utf8"
        # 爬虫伪装头部设置
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}

        # 设置操作超时时长
        self.timeout = 5

        # 爬虫模拟在一个request.session中完成
        self.s = requests.Session()

        # excel 第一行数据
        self.excel_data = [u'标题', u'公众号', u'发布时间', u'链接', u'关键字', u'城市', u'最近时间']

        # 行号
        self.excel_line_num = 0

        # 定义excel操作句柄
        self.excle_w = Workbook()

        # 以当前时间为名字建表
        self.excel_sheet_name = time.strftime('%Y-%m-%d')
        self.excel_content = self.excle_w.add_sheet(self.excel_sheet_name)

        # 日志
        self.log_file = open('logs/' + self.excel_sheet_name + '.log', 'a')
        # 抓取时间间隔 天
        self.delta_day = 7

    def __del__(self):
        self.s.close()
        self.log_file.write(u'程序结束')
        self.log_file.close()

    def log(self, msg):
        self.log_file.write('%s: %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))


# 创建关键字命名的文件夹
    def create_dir(self):
        if not os.path.exists(self.keywords.decode('utf-8')):
            os.makedirs(self.keywords.decode('utf-8'))

    def write_excel_head(self):
        i = 0
        for data in self.excel_data:
            self.excel_content.write(self.excel_line_num, i, data)
            i += 1
        self.excel_line_num += 1

    def get_search_result_by_keywords(self, sogou_search_url, number):
        self.log(u'搜索地址为：%s' % sogou_search_url)
        doc = self.s.get(sogou_search_url, headers=self.headers, timeout=self.timeout).content
        '''
        with open((self.keywords + '/' + self.keywords + '_' + str(number) + '.html').decode('utf-8'), 'w') as f:
            f.write(doc)
        '''
        return doc

        # 获得公众号主页地址

    def get_wx_url_by_sougou_search_html(self, sougou_search_html):
        doc = pq(sougou_search_html)
        # 以当前时间为名字建表
        urls = doc('.txt-box')('h3')('a')
        urls_array = []
        for item in urls.items():
            urls_array.append(item.attr('href'))

        WXHs = doc('.txt-box')('.s-p')('a.account')
        WXHs_array = []
        for item in WXHs.items():
            WXHs_array.append(item.text())

        release_time = doc('.txt-box')('.s-p')('.s2')('script')
        release_time_array = []

        for item in release_time.items():
            #获取数字型日期
            int_time = int(self.parse_article.get_number_from_string(item.text()))
            #再转化为datetime比较日期大小
            date = datetime.datetime.fromtimestamp(int_time)
            #比较两个日期之差
            delta = datetime.datetime.now() - date
            if abs(delta.days) > self.delta_day:
                release_time_array.append({'Time': date.strftime('%Y-%m-%d %H:%M:%S'), \
                                           'Flag': False})
            else:
                release_time_array.append({'Time': date.strftime('%Y-%m-%d %H:%M:%S'), \
                                           'Flag': True})


        size = min(len(urls_array), len(WXHs_array), len(release_time_array))
        weixinhao_article_array = []
        if size >= 0:
            for i in range(size):
                if release_time_array[i]['Flag']:
                    weixinhao_article_array.append({'WXH': WXHs_array[i],  \
                                                    'URL': urls_array[i],  \
                                                    'ReleaseTime': release_time_array[i]['Time']})
        else:
            self.log(u'未找到对应内容')

        return weixinhao_article_array

    def parse_article_by_url(self, article_array):
        for i in article_array:
            doc = self.s.get(i['URL'], headers=self.headers, timeout=self.timeout).content
            title = self.parse_article.get_title(doc)
            self.log(u'标题:%s' % title)
            province_list = self.parse_article.get_province(doc)
            self.log(u'获取到地名：%s' % province_list)
            self.log(u'开始写入EXCEL')
            # [u'标题', u'公众号', u'发布时间', u'链接', u'关键字', u'城市', u'最近时间']
            # 标题
            self.log(u'标题：%s' % title)
            self.excel_content.write(self.excel_line_num, 0, title.decode('utf-8'))
            # 公众号
            self.log(u'公众号：%s' % i['WXH'])
            self.excel_content.write(self.excel_line_num, 1, i['WXH'].decode('utf-8'))
            # 发布时间
            self.log(u'发布时间：%s' % i['ReleaseTime'])
            self.excel_content.write(self.excel_line_num, 2, i['ReleaseTime'].decode('utf-8'))
            # 链接
            self.log(u'链接：%s' % i['URL'])
            self.excel_content.write(self.excel_line_num, 3, i['URL'].decode('utf-8'))
            # 关键字
            self.log(u'关键字：%s' % self.keywords)
            self.excel_content.write(self.excel_line_num, 4, self.keywords.decode('utf-8'))
            # 城市
            self.log(u'城市：%s' % province_list)
            self.excel_content.write(self.excel_line_num, 5, province_list.decode('utf-8'))
            # 最近时间
            self.excel_line_num += 1
            print 'waiting 3 secs'
            time.sleep(3)

    def save_excel(self):
        self.log(u'保存excel:%s' % self.keywords + '/' + self.keywords + u'.xls')
        self.excle_w.save(self.keywords + '/' + self.keywords + '.xls'.decode('utf-8'))



    # 爬虫主函数
    def run(self):
        ' 爬虫入口函数 '
        # Step 0 ：  创建公众号命名的文件夹
        self.create_dir()
        self.write_excel_head()
        for num in range(self.page_size):

            # Step 1：GET请求到搜狗微信引擎，查询关键字
            print u'keyword:%s page%d : 1/3...' % (self.keywords.decode('utf-8'), num)
            self.log(u'开始获取，关键字为：%s' % self.keywords)
            self.log(u'开始调用sougou搜索引擎')
            sougou_search_html = self.get_search_result_by_keywords\
                (self.sogou_search_url_p1 + str(num+1) + self.sogou_search_url_p2, num+1)
            # Step 2：从搜索结果页中解析出文章链接
            print u'keyword:%s page%d : 2/3...' % (self.keywords.decode('utf-8'), num)
            self.log(u'获取sougou_search_html成功，开始抓取关键字对应的链接')
            articles = self.get_wx_url_by_sougou_search_html(sougou_search_html)
            # Step 3:根据链接抓取文章内容
            print u'keyword:%s page%d : 3/3...' % (self.keywords.decode('utf-8'), num)
            self.parse_article_by_url(articles)

            self.log(u'保存完成,请 等待5秒')

            print 'waiting 5 secs'
            time.sleep(5)

        self.save_excel()

if __name__ == '__main__':
    print ''' 
            *****************************************  
            **    Welcome to Spider of 公众号       **  
            **      Created on 2017-08-24          **  
            **      @author: zy                    **  
            ***************************************** 
    '''
    list_file = codecs.open("list.txt", "r", 'utf-8')
    print 'please waiting...'
    parse_article = parse_article()
    while 1:
        line = list_file.readline()
        if not line:
            break
        line = line.strip().replace("\n", "").replace("\r", "")
        if line:
            weixin_article_spider(line, parse_article, 10).run()
        else:
            continue

    list_file.close()

