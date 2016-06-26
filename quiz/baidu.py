#-*- coding:utf-8 -*-
import requests
import time
import random
import lxml.etree as etree
import HTMLParser

class baidu(object):
	'''
		重写的百度模块
		默认爬20页
		如果不到20页，有多少页，返回多少页
	'''
	_ACCEPT = '''text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'''
	_USER_AGENT = '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56'''
	content_list = []
	first_page = ''
	def __init__(self,key_word,pages = 20):
		self.key_word = key_word
		self.pages = pages
		# 下面是两个常量 
		
	def get_html(self,key_word,page_No):
		pn = str((page_No - 1) * 10)
		pay_load = {'wd':key_word,'rn':10,'ie':'utf-8','pn':pn}
		http_headers = {'Accept':self._ACCEPT,'User-Agent':self._USER_AGENT}
		r = requests.get('http://www.baidu.com/s',params = pay_load,headers = http_headers) 
		# print r.content
		return r.content
	def check_next(self,html):
		root = etree.HTML(html)
		nodes = root.xpath('''//a[@class="n"]''')
		if len(nodes) == 0:
			return False
		# 检测是不是“下一页”
		whole_str = ''
		for i in nodes:
			a_str = etree.tostring(i)
			h = HTMLParser.HTMLParser()
			a_str = h.unescape(a_str)
			whole_str = whole_str + a_str
		if u'下一页' in whole_str:
			return True
		else:
			return False
		pass
	# 运行
	def run(self):
		self.first_page = self.get_html(self.key_word,1) #第一页的内容含有搜索条数，比较重要，单独列出来
		self.content_list.append(self.first_page) # 把第一页加入列表
		if self.check_next(self.first_page):
			pass 
		else:
			return 'Finished'
		for i in range(2,self.pages + 1):
			# print i
			time.sleep(0.5+ 1.5 * random.random())
			# 先延时一段时间
			each_content = self.get_html(self.key_word,i)
			self.content_list.append(each_content)
			if not self.check_next(each_content):
				break
		pass


def main():
	# tsu = baidu('清华大学',6)
	tsu = baidu('edb1d57ad7106de0708b485dc134ae3a') # 该条搜索结果只有一页
	tsu.run()
	print len(tsu.content_list)
	pass


if __name__ == '__main__':
	main()