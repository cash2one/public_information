#-*- coding:utf-8 -*-

# time: 6/18/2016 AT BeiJing
# time: 6/20/2016 AT ChengDu

# bosonnlp的相关导入
from __future__ import print_function, unicode_literals
from bosonnlp import BosonNLP
# bosonnlp 相关导入结束
import codecs
import json
import requests
import os 
import hashlib
import re
# 该模块用来负责  自然语言处理
# 目前暂时使用 bosonnlp 模块
try:
	import MySQLdb
	has_MySQLdb = True
except:
	has_MySQLdb = False
# 添加了新的数据库处理模块 
# pymysql
try:
	import pymysql
	has_pymysql = True
except:
	has_pymysql = False
	pass

import sys
db_passw0rd = '#FIR8B*SinMSFN41xr#'
db_pass_word = 'Zh-L3z34IokS6fGze'
db_name = 'risk_assessment_system'


class nlp(object):
	"""
		自然语言处理
		亟需增加写入数据库模块
	"""
	# 类变量定义
	url = 'DEFAULT URL'
	token = '' # bosonnlp的 token
	content = '' # content就是需要处理的
	sha256 = ''
	# 下面是分析结果存储
	# 存储的是原始的分析结果
	sentiment = []
	ner = {} # 命名实体结果
	# 此外还存储数字型分析结果和字符串结果
	sentiment_positive = 0
	sentiment_negative = 0
	# 命名实体识别相关
	words = []
	entities = []
	# 下面是分析结果的字符串格式
	sentiment_str = ''
	theme = ''
	str_company = '检测到公司名称：'
	str_product = '检测到产品名称：'
	str_person = '检测到人名：'
	str_location = '检测到地点：'
	str_job = '检测到职业名称：'
	str_org = '检测到组织名称：'
	# 以下是命名实体识别的未去重列表
	locations  = []
	person_name = []
	company_name = []
	product_name = []
	job_title = []
	org_name = []
	# 变量定义结束
	# 一个方法用来获取token
	def get_TOKEN(self):
		# 存在文件里的
		pwd = "/var/tokens/boson_nlp.txt"
		with codecs.open(pwd,'r','utf-8') as f:
			token_str = f.read()
			f.close()
		self.token = token_str
		return token_str # 返回值作测试用
		pass
	@staticmethod
	def get_TEXT():
		# 存在文件里的
		pwd = "../src/text_1.txt"
		with codecs.open(pwd,'r','utf-8') as f:
			text_str = f.read()
			f.close()
		return text_str # 返回值作测试用
		pass
	def set_content(self,input_string):
		self.content = input_string
		# 设置内容用的
		m = hashlib.sha256() 
		m.update(input_string.encode('utf-8'))
		self.sha256 = m.hexdigest()
		'''
			中文字符在Python中是以unicode存在的。至此，所有的疑问都得以解除了。
			在hash前要求进行编码转换，是因为同一个字符串在不同的编码体系下有不同的值，为确保不发生歧义必须要进行一次显性转换。
		'''
		# 以上完成散列纸的计算
		pass
	def set_url(self,input_url):
		self.url = input_url
		pass

	# init函数，相当于构造函数
	def __init__(self,content = '',url = 'DEFAULT URL'):
		# super(nlp, self).__init__()
		# self.arg = arg
		self.set_content(content)
		# print (type(content))
		self.get_TOKEN() # 初始化的时候就读token
		self.set_url(url)
		pass
	# OK,下面就是各种语言处理用的函数了
	def sentiment(self):
		my_nlp = BosonNLP(self.token)
		self.sentiment = my_nlp.sentiment(self.content)
		# print (self.sentiment) # 测试用print
		positive = self.sentiment[0][0] * 100
		# 都转化为百分比的形式
		negative = self.sentiment[0][1] * 100
		# print (str(self.sentiment_positive))
		if positive > 80:
			status = '正面概率很大，约为:'+ str(positive) + '%。'
		elif positive >55:
			status = '正面概率较大，约为:'+ str(positive) + '%。'
		elif positive > 45:
			status ='情感倾向适中，其中正面概率约为:'+ str(positive) + '%。'
		elif positive > 30:
			status = '负面概率较大，约为:'+ str(negative) + '%。'
		else:
			status = '负面概率很大，约为:'+ str(negative) + '%。'
			pass
		# 下面开始写入类数据
		self.sentiment_str = status #字符串
		self.sentiment_positive = positive
		self.sentiment_negative = negative
		# print (status)
		pass
	def ner(self,sensitivity = 3): # 命名实体识别！
		'''
		{ # 返回数据格式举例
			'entity': [[0, 2, 'product_name'],
        		       [2, 3, 'job_title'],
            		   [3, 4, 'person_name']
            		  ],
  			'tag': ['ns', 'n', 'n', 'nr'],
  			'word': ['成都', '商报', '记者', '姚永忠']
  		}
  		'''
		my_nlp = BosonNLP(self.token) 
		# 下面这个的结果是字典
		ner_result = my_nlp.ner(self.content,sensitivity)[0]
		self.ner = ner_result
		# ner_result 是一个字典
		# 回去学一下字典的操作吧，，，忘了
		# print (ner_result)
		# print (ner_result['word'])
		words = ner_result['word']
		entities = ner_result['entity']
		# 定义两个自己的列表
		tmp_words = []
		tmp_entities = []
		for entity in entities:
			# print(''.join(words[entity[0]:entity[1]]), entity[2])
			tmp_words.append(''.join(words[entity[0]:entity[1]]))
			tmp_entities.append(entity[2])
			pass # end of for entity
		#  写入成自己习惯的格式。。。
		# for i in range(len(tmp_words)):
		# 	print (tmp_words[i] + '---> ' + tmp_entities[i])
		# 	pass # end of for i
		self.words = tmp_words
		self.entities = tmp_entities
		# 下面就要对ner作下一步处理了
		# print (len(self.words) == len(self.entities) ) ＃ 名称肯定是一样的
		for i in range(len(self.entities)):
			entity_type = tmp_entities[i]
			entity_word = tmp_words[i] 
			if entity_type == 'company_name':
				self.company_name.append(entity_word)
			elif entity_type == 'location':
				self.locations.append(entity_word)
			elif entity_type == 'product_name':
				self.product_name.append(entity_word)
			elif entity_type == 'person_name':
				self.person_name.append(entity_word)
			elif entity_type == 'org_name':
				self.org_name.append(entity_word)
			elif entity_type == 'job_title':
				self.job_title.append(entity_word)
			else:
				pass
			pass # end of for i in range
		self.ner_process()
		# shold i do something else?
	def ner_process(self):
		# 下面开始数据去重：
		# 还需要考虑列表为空的情况
		tmp_company = list(set(self.company_name))
		if tmp_company == []:
			self.str_company = '未检测到公司名称。、'
		for i in tmp_company:
			i = i + '、'
			self.str_company += i 
			pass 
		tmp_locations = list(set(self.locations))
		if tmp_locations == []:
			self.str_location = '未检测到地点名称。、'
		for i in tmp_locations:
			i = i + '、'
			self.str_location += i
			pass
		tmp_org = list(set(self.org_name))
		if tmp_org == []:
			self.str_org = '未检测到组织名称。、'
		for i in tmp_org:
			i = i + '、'
			self.str_org += i
			pass
		tmp_product = list(set(self.product_name))
		if tmp_product == []:
			self.str_product = '未检测到产品名称。、'
		for i in tmp_product:
			i = i + '、'
			self.str_product += i
			pass
		tmp_person = list(set(self.person_name))
		if tmp_person == []:
			self.str_person = '未检测到人名。、'
		for i in tmp_person:
			i = i + '、'
			self.str_person += i
			pass
		tmp_job = list(set(self.job_title))
		if tmp_job == []:
			self.str_job = '未检测到职业名称。、'
		for i in tmp_job:
			i = i + '、'
			self.str_job += i
		# 去重完毕
		# 修正字符串的最后一个顿号
		self.str_person = self.str_person[:-1] + '。'
		self.str_job = self.str_job[:-1]+ '。'
		self.str_product = self.str_product[:-1] + '。'
		self.str_company = self.str_company[:-1] + '。'
		self.str_org = self.str_org[:-1] + '。'
		self.str_location = self.str_location[:-1] +  '。'
		pass#end of the method ner
	# 新闻分类
	def classify(self):
		my_nlp = BosonNLP(self.token)
		result = my_nlp.classify([self.content])[0]
		# print (str(result * result))
		theme_list = ['体育','教育','财经','社会','娱乐','军事','国内','科技','互联网','房产','国际','女人','汽车','游戏']
		self.theme = theme_list[result]
		pass
	# 自然语言处理完毕，下面是数据展示
	def show(self):
		print ('\n自然语言分析结果：')
		print ('散列值：' + self.sha256)
		print (self.sentiment_str)
		print ('主题分类为：' + self.theme)
		print (self.str_company)
		print (self.str_org)
		print (self.str_product)
		print (self.str_location)
		print (self.str_job)
		print (self.str_person)
		pass
	# 展示完成， 下面写数据库
	# 先是写字符串吧，这个是给前段看的
	# now support pymysql
	def write_db_str(self):
		if not has_MySQLdb:
			# 就是没有这个模块
			# return 'NO MySQLdb'
			pass # 因为还可能有pymysql
		else:
			parameter = (self.url,self.sha256,self.str_company,self.str_org,self.str_job,self.str_product,self.str_person,self.str_location,self.sentiment_str,self.theme)
			# go
			conn = MySQLdb.connect('localhost','root',db_passw0rd,'nlp',charset="utf8")
			cursor = conn.cursor()
			cursor.execute("INSERT INTO `nlp`.`result` (`url`, `sha256`, `company`, `org`, `job`, `product`, `person_name`, `locations`, `positive`, `theme`) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')"%parameter)
			cursor.close()
			conn.commit()
			conn.close()
			return 'Use MySQLdb'
		if not has_pymysql:
			# print ('HERE')
			return 'NO pymysql'
		else:
			# print ('go')
			connection = pymysql.connect(
			host='127.0.0.1',
			user = 'root',
			password = db_pass_word,
			db = db_name,
			charset = 'utf8')
			try:
				with connection.cursor() as cursor:
					sql = u"INSERT INTO `nlp_result` (`url`, `sha256`, `company`, `org`, `job`, `product`, `person_name`, `locations`, `positive`, `theme`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
					para = (self.url,self.sha256,self.str_company,self.str_org,self.str_job,self.str_product,self.str_person,self.str_location,self.sentiment_str,self.theme)
					cursor.execute(sql,para)
				connection.commit()
				cursor.close()
			finally:
				connection.close()
				return 'DONE by pymysql'
		pass # end of the function
	# 然后是写到后端的表中
	# now support pymysql
	def write_db_storage(self):
		# 写入数据库的字符串和给前段看的还有一些不一样
		db_company = '/' + '//'.join(self.company_name) + '/'
		db_org = '/' + '//'.join(self.org_name) + '/'
		db_product = '/' + '//'.join(self.product_name) + '/'
		db_person = '/' + '//'.join(self.person_name) + '/'
		db_locations = '/' + '//'.join(self.locations) + '/'
		db_job = '/' + '//'.join(self.job_title) + '/'
		# print (db_company)
		if not has_MySQLdb:
			# 就是没有这个模块
			# return 'NO MySQLdb'
			pass
		else:
			parameter = (self.url,self.sha256,self.content,str(self.sentiment_positive),self.theme,db_company,db_org,db_job,db_product,db_person,db_locations)
			# go
			conn = MySQLdb.connect('localhost','root',db_passw0rd,'nlp',charset="utf8")
			cursor = conn.cursor()
			cursor.execute("INSERT INTO `nlp`.`storage` (`url`, `sha256`, `text`, `positive`, `theme`, `company`, `org`, `job`, `product`, `person_name`, `locations`) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')"%parameter)
			cursor.close()
			conn.commit()
			conn.close()
			return 'Use MySQLdb'
		if not has_pymysql:
			return 'NO pymysql'
		else:
			# print ('Hhhh')
			connection = pymysql.connect(
			host='127.0.0.1',
			user = 'root',
			password = db_pass_word,
			db = db_name,
			charset = 'utf8')
			try:
				with connection.cursor() as cursor:
					sql = u"INSERT INTO `nlp_storage` (`url`, `sha256`, `text`, `positive`, `theme`, `company`, `org`, `job`, `product`, `person_name`, `locations`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
					# para = (self.url,self.sha256,self.str_company,self.str_org,self.str_job,self.str_product,self.str_person,self.str_location,self.sentiment_str,self.theme)
					para = (self.url,self.sha256,self.content,str(self.sentiment_positive),self.theme,db_company,db_org,db_job,db_product,db_person,db_locations)
					cursor.execute(sql,para)
				connection.commit()
				cursor.close()
			except Exception,e:  
				print(e)
			finally:
				connection.close()
				return 'DONE by pymysql'
		pass # end of the function
	# 添加一个常用的re方法，静态的
	@staticmethod
	def resume_list(input_str):
		pattern = re.compile('/(.*?)/',re.S)
		items = re.findall(pattern,input_str)
		return items
		pass


	# 查看是否存在 
	# now support pymysql
	def check_exist(self):
		# print ('check_exist(')
		if has_MySQLdb == False:
			# return 'DO NOT HAVE MySQLdb!'
			pass
		else:
			sql = "SELECT * FROM `nlp_storage` WHERE `sha256` = \'%s\' " % self.sha256
			conn = MySQLdb.connect('localhost','root',db_passw0rd,'nlp',charset="utf8")
			cursor = conn.cursor()
			cursor.execute(sql)
			# 做相关的后续数据库操作
			result =  cursor.fetchall()
			cursor.close()
			# conn.commit()
			conn.close()
			# return 'DONE by MySQLdb'
			pass # end of else
		if has_pymysql == False:
			return 'DO NOT HAVE pymysql'
		else:
			# do things using pymysql
			connection = pymysql.connect(
			host='127.0.0.1',
			user = 'root',
			password = db_pass_word,
			db = db_name,
			charset = 'utf8')
			try:
				with connection.cursor() as cursor:
					sql = u"SELECT * FROM `nlp_storage` WHERE `sha256` = %s "
					para = (self.sha256)
					cursor.execute(sql,para)
					result = cursor.fetchall()
					cursor.close()
			finally:
				connection.close()
			pass #end of the else
		if len(result) == 0:
			return False # 不存在
		else:
			# 也就是存在
			# 那么就要读数据了
			result = result[0] # 反正只取第一个 
		#go
		# print (result)
		# x = 0
		# for i in result:
		# 	print ( str(x) + '-------')
		# 	print (i)
		# 	x = x+ 1
		# 	pass # end of for i
		self.sentiment_positive = float(result[3])
		self.theme = result[4]
		# 最后返回True
		# print (self.theme)
		self.company_name = nlp.resume_list(result[5])
		self.org_name = nlp.resume_list(result[6])
		self.job_title = nlp.resume_list(result[7])
		self.product_name = nlp.resume_list(result[8])
		self.person_name = nlp.resume_list(result[9])
		self.locations = nlp.resume_list(result[10])
		# ner处理
		self.ner_process()
		# 还有一个情感处理
		positive = self.sentiment_positive 
		negative = 100 - positive
		if positive > 80:
			status = '正面概率很大，约为:'+ str(positive) + '%。'
		elif positive >55:
			status = '正面概率较大，约为:'+ str(positive) + '%。'
		elif positive > 45:
			status ='情感倾向适中，其中正面概率约为:'+ str(positive) + '%。'
		elif positive > 30:
			status = '负面概率较大，约为:'+ str(negative) + '%。'
		else:
			status = '负面概率很大，约为:'+ str(negative) + '%。'
			pass
		# 下面开始写入类数据
		self.sentiment_str = status #字符串
		self.sentiment_negative = negative
		return True
		pass# end of the function
	# 最后一个run方法：
	def run(self):
		exist = self.check_exist()
		if exist == True:
			# print ('已存在')
			pass
		else:
			try:
				self.sentiment()
				self.ner(3)
				self.classify()
			except:
				pass
			# 别忘了写数据库
			# print ('写数据库')
			s = self.write_db_str()
			y =  self.write_db_storage()
			# print (s)
			# print (y)
			# 写数据库结束
			pass # 分支结构结束

		pass



def main():# u主函数一般用来测试
	# 测试代码
	# example = nlp()
	# 从文本获取内容，并设置内容
	text = nlp.get_TEXT()
	#example.set_content(text)
	# 设置内容完毕
	# print (text)
	# 先是情感分析－－正面或者负面
	# example.sentiment()
	# 情感分析结束
	# 下一个是命名实体识别！最重要的这个
	# example.ner(3)
	# print (example.sha256)
	# example.classify()
	# print (example.theme)
	# example.show()
	# example.write_db_str()
	# example.write_db_storage()
	# example.check_exist()
	#example.show()
	# 下面需要总结出一个run 方法，现在这样main有点麻烦
	# 然后这个模块就搞定了
	'''
		最终的使用方法如下
	'''
	example = nlp(content = text,url = 'http://baike.baidu.com/subview/133041/5358738.htm')
	example.run()
	example.show()
	# 基本完成
	# UNIX时间戳 1466515285.327357
	# AT ChengDu
	pass


if __name__ == '__main__':
	main()
		