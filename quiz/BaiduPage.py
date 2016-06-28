#-*- coding:utf-8 -*-
# 引入自己写的模块
from baidu import baidu 
# from NaturalLanguageProcessing import nlp
# 还有一些别的需要的东西
import HTMLParser
import re
import lxml.etree as etree
# from UnRedirectUrl import getUnRedirectUrl # 已停用
from http30x import get_302_Location
import time


class BaiduPage(object):
	'''
		对百度的搜索结果页面进行处理
		用新的xpath处理多数内容
		只处理一页吧?
	'''
	page_number  = 0
	cache_link_list = []
	direct_link_list = []
	real_link_list = []
	# 条目数不是私有变量
	items_count = 0
	# 定义几个变量
	_html_content = ''
	search_condition = '' # 不知道在这里添加是否合适?
	def __init__(self,html_content,page_number = 1):
		self.page_number = page_number
		self._html_content = html_content
		self._root = etree.HTML(html_content)
		pass
	
	# 找出百度找到了多少条目
	def find_items_count(self):
		nodes = self._root.xpath("//div[@class='nums']")
		i = nodes[0]
		div_str = etree.tostring(i)
		h = HTMLParser.HTMLParser()
		div_str = h.unescape(div_str)
		# print div_str		
		pattern = re.compile('百度为您找到相关结果约(.*?)个</div>',re.S)
		items = re.findall(pattern,div_str.encode('utf-8'))
		# print items
		try:
			num_str = items[0].replace(',','')
			# print num_str
			self.items_count = int(num_str) # 这里，以前写成私有变量了，导致了一些错误
			# print str(num - 1)
			return self.items_count
		except:
			return 'NoREC'
		pass
	# 找出所有的百度快照的链接
	def find_cache_link(self):
		nodes = self._root.xpath("""//div[@class='result c-container ']//a[@data-click="{'rsv_snapshot':'1'}"]""")
		# print len(nodes)
		for i in nodes:
			div_str = etree.tostring(i)
			h = HTMLParser.HTMLParser()
			div_str = h.unescape(div_str)
			# print div_str
			# 下面应该在字符串中找cache link
			pattern = re.compile('href="(.*?)"',re.S)
			items = re.findall(pattern,div_str)
			try:
				# 将cache link 加入列表
				self.cache_link_list.append(items[0])
			except:
				pass
		# print div_str 
		pass
	def run(self,findCounts = False):
		# 首先找条目数，用来写数据库 
		if findCounts:
			self.find_items_count()
			pass
		self.find_cache_link()
		self.find_direct_link()
		self.link_transfer()
		
		pass
	# 找出百度的直接连接，这个连接应该还包含一些跳转的内容，之后再处理
	def find_direct_link(self):
		nodes = self._root.xpath("""//div[@class='result c-container ']//a[@data-click]""")# 用另外一给xpath来找这个类型的a标签
		# 另外，这个xpath会把百度快照和评论的内容也带进来，还要处理列表把这些内容删掉
		tmp_list = []
		for i in nodes:
			div_str = etree.tostring(i)
			h = HTMLParser.HTMLParser()
			div_str = h.unescape(div_str)
			tmp_list.append(div_str) # 全加进去之后再剔除，这么写影响效率但是看的清楚一些
			pass # end of for i 
		# print len(tmp_list)
		for x in tmp_list:
			if 'cache.baiducontent.com' in x:# 这句话能去掉百度快照的内容
				tmp_list.remove(x)
			if 'rsv_comment' in x:# 执行了这句话之后，评论的那些标签为什么还在！！？？
				tmp_list.remove(x) # 也不知道是怎么回事。。。
		# 下面的语句去评论部分
		for i in tmp_list:
			result = 'rsv_comment' in i
			# print result
			if result:
				tmp_list.remove(i)
		# 下面的语句去rsv_level
		for i in tmp_list:
			result = 'rsv_vlevel' in i
			# print result
			if result:
				tmp_list.remove(i)	
		# print tmp_list		
		for i in tmp_list:
			# print i.encode('utf-8')
			pattern = re.compile('href="(.*?)"',re.S)
			items_2 = re.findall(pattern,i)# FIXED A BUG 
			try:
				# print items_2[0].encode('utf-8')
				self.direct_link_list.append(items_2[0])
			except:
				pass
			pass
	def link_transfer(self):
		for i in self.direct_link_list:
			time.sleep(0.7)# 略微延迟
			location =  get_302_Location(i)
			if 'https://www.baidu.com/s?' not in location:
				self.real_link_list.append(location)
			# print location
			pass # end of for i 
		# 去重
		real_link_list = list(set(self.real_link_list))
		pass



def main():
	example = baidu('刘灵均+成飞')
	example.run()
	# print '得到'+str(len(example.content_list)) + '页结果'
	# content = example.first_page
	content = example.content_list[0]
	# print content
	page = BaiduPage(content,1)
	page.run(findCounts = True)
	# print str(page.items_count)
	# print page.cache_link_list
	for i in page.real_link_list:
		print i
	# print page.real_link_list
	print len(example.content_list)
	# for i in page.cache_link_list:
	# 	print i # 百度快照部分的解析还存在问题。。。




	pass

if __name__ == '__main__':
	main()
		