#!/usr/bin/python
# coding: utf-8

from pyquery import PyQuery as pq
from pyExcelerator import *  # 导入excel相关包
import codecs
import requests
import time
import os
# 这三行代码是防止在python2上面编码错误的，在python3上面不要要这样设置
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
''''' 
总的来说就是通过搜狗搜索中的微信搜索入口来爬取 
'''

class weixin_spider:
    def __init__(self, keywords, page_size=1):
        ' 构造函数 '
        self.keywords = keywords
        # 搜狐微信搜索链接入口
        # 翻页次数
        self.page_size = 1
        if 3 >= page_size > 0:
            self.page_size = page_size
        else:
            self.page_size = 3

        self.sogou_search_url_p1 = 'http://weixin.sogou.com/weixin?query=' + \
                                self.keywords + \
                                '&_sug_type_=&sut=1092&lkt=0%2C0%2C0&s_from=input&_sug_=y&type=1&sst0=1503747703266&page='

        self.sogou_search_url_p2 = '&ie=utf8&w=01019900&dr=1'
        # 爬虫伪装头部设置
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}

        # 设置操作超时时长
        self.timeout = 5

        # 爬虫模拟在一个request.session中完成
        self.s = requests.Session()

        # excel 第一行数据
        self.excel_data = [u'微信号']
        # 定义excel操作句柄
        self.excle_w = Workbook()
        # 以当前时间为名字建表
        self.excel_sheet_name = time.strftime('%Y-%m-%d')
        self.excel_content = self.excle_w.add_sheet(self.excel_sheet_name)
        # 行号
        self.line_num = 0
        # 日志
        self.log_file = open(u'logs/' + self.excel_sheet_name + '.log', 'a')
        # 微信号
        self.weixinhao_array = []

    def __del__(self):
        self.s.close()
        self.log_file.write(u'程序结束')
        self.log_file.close()

    # 自定义log函数，主要是加上时间

    def log(self, msg):
        self.log_file.write('%s: %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
        #print u'%s: %s' % (time.strftime(u'%Y-%m-%d %H:%M:%S'), msg.encode("GB18030"))

    # 创建公众号命名的文件夹
    def create_dir(self):
        if not os.path.exists(self.keywords.decode('utf-8')):
            os.makedirs(self.keywords.decode('utf-8'))

    def write_excel_head(self):
        i = 0
        self.line_num += 1
        for data in self.excel_data:
            self.excel_content.write(0, i, data)
            i += 1

    def get_search_result_by_keywords(self, sogou_search_url, number):
        self.log(u'搜索地址为：%s' % sogou_search_url)
        doc = self.s.get(sogou_search_url, headers=self.headers, timeout=self.timeout).content
        self.save_html_file(str(number), doc)
        return doc

        # 获得公众号主页地址

    def get_wx_url_by_sougou_search_html(self, sougou_search_html):
        doc = pq(sougou_search_html)
        # 以当前时间为名字建表

        # 获取微信号
        weixin_hao = doc('.gzh-box2')('.txt-box')('.info')('label')
        # 写入微信号内容

        for item in weixin_hao.items():
            flag = False
            self.log(u'写入微信号:%s' % item.text())
            for k in range(len(self.weixinhao_array)):
                value = self.weixinhao_array[k]
                if value == item.text():
                    self.log(u'微信号:%s已存在' % item.text())
                    flag = True
                    break
            if flag:
                continue
            self.weixinhao_array.append(item.text())
            self.parse_one_article(item.text())
            self.line_num += 1

    def parse_one_article(self, text):
        # 将这些简单的信息保存成excel数据
        self.excel_content.write(self.line_num, 0, text)

    def save_excel(self):
        self.log(u'保存excel:%s' % self.keywords + '/' + self.keywords + u'.xls')
        self.excle_w.save(self.keywords + '/' + self.keywords + '.xls'.decode('utf-8'))

    # 写入HTM了文件
    def save_html_file(self, number, content):
        ' 数据写入文件 '
        with open(self.keywords + '/' + self.keywords + '_'+ number + '.html'.decode('utf-8'), 'w') as f:
            f.write(content)

    # 爬虫主函数
    def run(self):
        ' 爬虫入口函数 '
        # Step 0 ：  创建公众号命名的文件夹
        self.create_dir()
        self.write_excel_head()
        for num in range(self.page_size):

            # Step 1：GET请求到搜狗微信引擎，以微信公众号英文名称作为查询关键字
            self.log(u'开始获取，微信公众号关键字为：%s' % self.keywords)
            self.log(u'开始调用sougou搜索引擎')
            sougou_search_html = self.get_search_result_by_keywords\
                (self.sogou_search_url_p1 + str(num+1) + self.sogou_search_url_p2, num+1)
            # Step 2：从搜索结果页中解析出公众号主页链接
            self.log(u'获取sougou_search_html成功，开始抓取公众号对应的主页wx_url')
            articles = self.get_wx_url_by_sougou_search_html(sougou_search_html)
            self.log(u'获取wx_url成功')

            self.log(u'保存完成,请 等待5秒')

            time.sleep(5)

        self.save_excel()

        # main


# 几个可供参考的公众号
# DataBureau
# python6359
# ArchNotes
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
    while 1:
        line = list_file.readline()
        if not line:
            break
        line = line.strip().replace("\n", "").replace("\r", "")
        if line:
            weixin_spider(line, 1).run()
        else:
            continue

    list_file.close()
