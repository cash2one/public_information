#-*- coding:utf-8 -*-
from baidu import baidu 
from BaiduPage import BaiduPage
import time
import pymysql

db_pass_word = 'Zh-L3z34IokS6fGze'
db_name = 'risk_assessment_system'

class BaiduResult(object):
	'''
		把百度搜索结果汇总起来，所有的页的URL都汇总起来
		考虑在这个类里面加上去掉无效link的功能
	'''
	items_count = 0
	cache_link_list = []
	real_link_list = []
	search_condition = ''
	result_page_list = []
	target_user_id = 0
	# name 和 company 用来检测页面是否有效
	name = ''
	company = ''
	def link_verify(self):
		print 'type of name:',
		print type(self.name)

		pass # end of the function
	def __init__(self,input_word,person_id):
		self.search_condition = input_word
		if '+' in input_word:
			index = input_word.find('+')
			self.name = input_word[:index]
			self.company = input_word[index+1:]
			pass # end of if +
		self.target_user_id = person_id
	# 运行	
	def run(self):
		result = baidu(self.search_condition)
		result.run()
		self.result_page_list = result.content_list
		# 先从第一个页面中获取有多少条搜索结果
		first = BaiduPage(result.first_page)
		self.items_count = first.find_items_count()
		# 获取搜索结果条目数结束
		print '找到相关信息：'+ str(self.items_count)
		# 下面该获取链接了
		for each_result in self.result_page_list:
			time.sleep(0.2)
			page = BaiduPage(each_result)
			page.run()
			for i in page.real_link_list:
				if i not in self.real_link_list:
					self.real_link_list.append(i)
					pass# end of if i 
				pass # end of for i 
			for i in page.cache_link_list:
				if i not in self.cache_link_list:
					self.cache_link_list.append(i)
					pass # end of i
				pass # end of for i
			# 到这里的时候，已经把链接存下来了
			# 经过多次修改百度的url参数，现在的搜索结果比以前准确了 
			pass # end of for each_result
		self.db_write_search_result()
		pass #end of the function run
	# 一个填表的函数
	def db_write_search_result(self):
		connection = pymysql.connect(
		host='127.0.0.1',
		user = 'root',
		password = db_pass_word,
		db = db_name,
		charset = 'utf8')
		try:
			# 来检查数据库中是否
			# 已经含有该记录，如果有的话
			# 删除，然后再填入新的记录
			exists = False
			with connection.cursor() as cursor:
				sql = u"SELECT * FROM `search_result` WHERE `search_condition_md5` = md5(%s)"
				para = (self.search_condition)
				# para = ('刘时勇+成飞') # for test 
				cursor.execute(sql,para)
				result = cursor.fetchone()
				if len(result) == 0:
					pass
				else:
					exists = True
				print exists
			cursor.close()
			if exists:
				with connection.cursor() as cursor:
					sql = "DELETE FROM `search_result` WHERE `search_condition_md5` = md5(%s)"
					para = para = (self.search_condition)
					cursor.execute(sql,para)
				connection.commit()
				cursor.close()
			else:
				pass
			# 下面是写入
			with connection.cursor() as cursor:
				# insert a new record
				sql = u"INSERT INTO `search_result` (`id`, `target_user_id`, `search_condition`, `item_count`, `search_condition_md5`) VALUES (NULL, %s, %s, %s, md5(%s))"
				para =  (str(self.target_user_id),self.search_condition,str(self.items_count),self.search_condition)
				cursor.execute(sql,para)
			connection.commit()
			cursor.close()
		finally:
			connection.close()
		pass # end of the function


	

def main():
	example = BaiduResult('刘时勇+成飞',6)
	example.run()
	# example.link_verify()
	
	# for i in example.real_link_list:
	# 	print i


if __name__ == '__main__':
	main()
		