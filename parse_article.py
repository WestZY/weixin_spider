#!/usr/bin/python
# coding: utf-8
from pyquery import PyQuery as pq
import codecs
import re


class parse_article:
    @staticmethod
    def get_title(article):
        if article:
            doc = pq(article)
            return doc('html')('head')('title').text()
        else:
            return ''

    def __init__(self):
        self.province_array = []
        province_file = codecs.open("province.txt", "r", 'utf-8')
        while 1:
            line = province_file.readline()
            if not line:
                break
            line = line.strip().replace("\n", "").replace("\r", "")
            if line:
                self.province_array.append(line)
            else:
                continue
        province_file.close()

    def get_province(self, article):
        province_list = ''
        for item in self.province_array:
            if article.find(item) >= 0:
                province_list += (item+'|')

        return province_list

    def get_number_from_string(self, string):
        mode = re.compile(r'\d+')
        strings = mode.findall(string)
        if len(strings) > 0:
            return strings[0]
        else:
            return '0'
