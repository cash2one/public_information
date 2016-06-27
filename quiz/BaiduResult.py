#-*- coding:utf-8 -*-
from baidu import baidu 
from BaiduPage import BaiduPage

class BaiduReslut(object):
	'''
		把百度搜索结果汇总起来，所有的页的URL都汇总起来
		考虑在这个类里面加上去掉无效link的功能
	'''
	cache_link_list = []
	real_link_list = []
	search_condition = ''
	result_page_list = []

	def __init__(self,input_word):
		self.search_condition = input_word
	# 运行	
	def run(self):
		result = baidu(self.search_condition)
		self.result_page_list = result.content_list

