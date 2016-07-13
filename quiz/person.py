#-*- coding:utf-8 -*-
'''
	模块：用途、工作。
'''
# import the modules
import pymysql
import re
import time
from BaiduResult import BaiduResult
import requests
import sys
from config import config
import json
from cix_extractor import Extractor
from NaturalLanguageProcessing import nlp

db_pass_word = 'Zh-L3z34IokS6fGze'
db_name = 'risk_assessment_system'


class person(object):
	# 变量定义
	risk_count = 0  # 这个是写在数据库 person_status 中的危险信息数量
	score = 0 # 这个是此人的总分数
	url_count = 0
	url_sum = 0 #  URL 上的分数的总得分
	key_word_list = [] # 这个列表后面才会用到	
	eva_standard = {}
	key_wd_dict = {}
	phone = ''
	qq = ''
	id = ''
	name = ''
	pid = 0
	cid = 0
	url_dict = {} # 举例：'url' -> 'search_condition'
	wd_list = []# 这个列表用来存放构造的关键词们--邮箱手机号
	wd_combine_list = [] # 这个列表存的是 姓名和公司简称的组合
	work_email_list = []
	person_email_list = []
	company_name_list = [] # 公司的简称列表
	connection = None # 数据库连接
	audit = False # 默认未处置
	exist = False # 是否存在？ 
	# init
	def __init__(self,person_id):
		self.pid = person_id
		self.db_init()
		# 先获取公司id
		self.get_basic_info()
		self.db_close # 获取基本信息之后，关闭数据库连接
		# 因为下面要进行网络数据收集，这其中并不需要持续写入数据
		# 上面的完成了之后，还要构造百度搜索关键词
		self.generate_wd()
		# 初始化完毕
		pass
	# 通过读数据库，获取一些基本的信息
	def get_basic_info(self):
		sql = u"SELECT * FROM `target_user` WHERE `id` = %s"
		para = (str(self.pid))
		result = self.db_read(sql,para)
		# 先看是否存在这个人
		if len(result) == 0:
			self.exist = False
			return 'Do NOT EXIST'
		else:
			self.exist = True
		# 是否存在判断完毕
		result = result[0] # 取结果
		self.name = result[1].encode('utf-8')
		self.person_email_list = person.separate(result[2].encode('utf-8'))
		self.work_email_list = person.separate(result[3].encode('utf-8'))
		self.id = result[4].encode('utf-8')
		self.qq = result[5].encode('utf-8')
		self.phone = result[6].encode('utf-8')
		self.cid = result[7]
		if result[8] == 'True':
			self.audit = True
		else:
			pass# 如果被处置过，后面的事情都不用做了
		# 现在完成了获取个人信息的步骤，现在根据已经获取的个人信息，该获取公司信息了
		sql = u"select nick_name from company where id = %s"
		para = (str(self.cid))
		result = self.db_read(sql,para)
		if len(result) == 0:
			return 'Company Do NOT EXIST'
		result = result[0]
		self.company_name_list = person.separate(result[0].encode('utf-8'))
		# 公司简称获取完毕，下面获取公司的敏感关键词
		sql = u"select level , word from key_word where company_id = %s"
		result = self.db_read(sql,para)
		if len(result) == 0:
			return 'KeyWD Do NOT EXIST'
		# 纳入字典
		for i in result:
			self.key_wd_dict[i[1].encode('utf-8')] = i[0]
		for i in self.company_name_list:
			self.key_wd_dict[i] = 1 # 默认等级为1
		# 纳入字典完毕
		# print self.key_wd_dict
		# 初始化过程完毕
		pass #end of the function
		
	# 下面这几个方法是操作数据库相关的函数
	def db_init(self):
		self.connection = pymysql.connect(
		host='127.0.0.1',
		user = 'root',
		password = db_pass_word,
		db = db_name,
		charset = 'utf8')
		pass #end of the function
	def db_read(self,sql,para):
		with self.connection.cursor() as cursor:
			cursor.execute(sql,para)
			result = cursor.fetchall()
			return result
	# 写操作
	def db_write(self,sql,para):
		with self.connection.cursor() as cursor:
			cursor.execute(sql,para)
		self.connection.commit()
	# 结束数据库连接
	def db_close(self):
		self.connection.close()
		pass
	# 数据库操作结束
	
	# 一个分离// 的静态方法
	@staticmethod
	def separate(input_str):
		pattern = re.compile('/(.*?)/',re.S)
		items = re.findall(pattern,input_str)
		# print items
		return items
		pass

	# 构造关键字	
	def generate_wd(self):
		mail = False
		# 构造搜索关键词，首先把邮箱姓名手机号qq号之类的加进来
		if mail:
			for i in self.work_email_list:
				self.wd_list.append(i)
				pass # end of for i 
			for i in self.person_email_list:
				self.wd_list.append(i)
			pass # end of if
		# 先不搜邮箱了把
		# 到这里邮箱添加完了
		self.wd_list.append(self.qq)
		self.wd_list.append(self.phone)
		self.wd_list.append(self.id)
		# 上面的内容就需要记录百度找到的搜索条数就可以了
		# 下面添加的内容需要进行详尽的搜索
		for i in self.company_name_list:
			each_string = self.name + ' + ' + i
			self.wd_combine_list.append(each_string)
			pass # end of for i 
		# 构造结束 现在就需要这些关键词  就够了
		pass
	# 改名为collect 方法，
	# 意思是数据收集
	def collect(self):
		if not self.exist:
			return 'NOT EXIST'
		self.db_init()
		# 首先详细检测各个项目
		for i in self.wd_combine_list:
			each_combine = BaiduResult(i,self.pid)
			time.sleep(0.3)
			each_combine.run(onlyCount = False)
			# print each_combine.dir
			for x in each_combine.direct_link_list:
				# 添加进字典
				if x in self.url_dict:
					pass 
				else:
					self.url_dict[x] = i # i 就是搜索条件
					# print i
				# print x
				pass #end of for x
			pass # end of for i
		# 然后对不需要详细URL的关键词搜索 
		for i in self.wd_list:
			each = BaiduResult(i,self.pid)
			each.run(onlyCount = True)
			time.sleep(0.6)
		# 现在要执行数据采集工作
		for direct_url in self.url_dict:
			exists = self.check_directlink_exist(direct_url)
			if exists:
				# 如果存在，仅更新时间
				# print 'exist'
				self.update_by_directlink(direct_url)
			else:
				# 如果不存在，那么需要获取数据
				try:
					r = requests.get(direct_url)
					# r.encoding = 'utf-8'
					text = r.text
					text = text.encode('utf-8',"ignore")
					url = r.url
					print r.url
				except requests.exceptions.ReadTimeout:
					url = direct_url
					text = '--TimeOutError--'
				except requests.exceptions.ChunkedEncodingError:
					url = direct_url
					text = '--ChunkedEncodingError--'
				except:
					url = direct_url
					text = '--RequestError--'
				exists2 = self.check_url_exist(url)
				if exists2:
					print 'exist2'
					# 如果real url 已经存在
					try:
						self.update_by_url(direct_url,url,text)
					except:
					 	self.update_by_url(direct_url,url,'--ERROR on Mysql--')
				else:
					# 就是完全不存在咯
					try:
						self.write_web_page(direct_url, url, text)
					except:
						self.write_web_page(direct_url, url, '--ERROR on Mysql--')
					pass # end of if exist2
				pass #end of if exist
			pass # end of for direct_url
		# 现在是函数了
		self.db_close()
		pass # end of the function collect  
	# 下面是另一些数据库操作
	def write_web_page(self,direct_link,url,plainText):
		sql = u"INSERT INTO `web_page` (`id`, `url`, `url_md5`, `raw_url`, `raw_url_md5`, `insert_time`, `update_time`, `origin_time`, `target_user_id`, `by_key_word`, `score`, `plain_text`, `evaluate`)  VALUES (NULL, %s, md5(%s),%s, md5(%s) , %s, %s, NULL, %s, %s, %s, %s, 'False')"
		para = (url,url,direct_link,direct_link,time.ctime(),time.ctime(),self.pid,self.url_dict[direct_link],'0',plainText)
		self.db_write(sql,para)
		pass
	def check_directlink_exist(self,direct_link):
		sql = u"SELECT `id` FROM `web_page` WHERE `raw_url_md5` = md5(%s) "
		para = (direct_link)
		result = self.db_read(sql,para)
		# print result
		if result is None:
			return False
		elif result is ():
			return False
		else:
			return True
		pass
	def update_by_directlink(self,direct_link):
		sql = u"UPDATE `web_page` SET `update_time`=%s WHERE `raw_url_md5` = md5(%s) "
		para = (time.ctime(),direct_link)
		self.db_write(sql,para)
		pass 
	def check_url_exist(self,real_url):
		sql = u"SELECT `id` FROM `web_page` WHERE `url_md5` = md5(%s) "
		para = (real_url)
		result = self.db_read(sql,para)
		# print result
		if result is None:
			return False
		elif result is ():
			return False
		else:
			return True
		pass
	def update_by_url(self,direct_link,url,plainText):
		sql = u"UPDATE `web_page` SET `raw_url` = %s, `raw_url_md5` = md5(%s) , `update_time`= %s , `plain_text` = %s  WHERE `url_md5` = md5(%s) "
		para = (direct_link,direct_link,time.ctime(), plainText ,url)
		self.db_write(sql,para)
		pass 
	# 评分函数，这个函数是离线的
	def evaluate(self):
		if self.audit:
			return 'Audit'
			pass # end of is audit
		# 载入配置文件
		self.eva_standard = config.load()
		# 载入完毕
		# 生成已知敏感关键词表
		self.key_word_list = []
		for i in self.key_wd_dict:
			self.key_word_list.append(i)
		# print key_word_list
		# print self.eva_standard
		# 先连接数据库
		self.db_init()
		# 我们已经有了关键词表 self.key_wd_dict
		sql = "select `id`, `plain_text`,`url` from `web_page` where `target_user_id` = %s and evaluate = 'False'"
		para = (self.pid)
		result = self.db_read(sql,para)
		if result is None:
			self.db_close()
			return 'NO DATA'
		elif  result is ():
			self.db_close()
			return 'NO DATA'
		else:
			pass # 说明有数据
		# print result[8][1]
		self.irrelevant = self.load_irrelevant_words()
		for each in result:
			sum = 0 # 总分
			id = each[0]
			url = each[2]
			text_html = each[1]
			score_key_words = self.count_key_words(text_html,url)
			# 下面要进行实体识别了
			if score_key_words > 0:
				# web正文抽取
				ext = Extractor(url = 'ras_sys',text = text_html)
				try:
					mainText = ext.getContext()
				except:
					mainText = 'Failed'
				# 抽取结束
				score_nlp = self.evaluate_nlp(mainText,url)
			else:
				score_nlp = 0
			# 对每个URL计算总分
			# 先加载权重
			a1 = self.eva_standard['baidu']['url']['each_url']['kw']['value']
			a2 = self.eva_standard['baidu']['url']['each_url']['nlp']['value']
			sum = a1 * score_key_words + a2 * score_nlp
			if sum > 0:
				self.risk_count += 1 # 危险信息数 +1
				print str(sum) + ' -> ' + url
			# 已经完成了对每个URL进行评分的过程
			#  现在更新
			sql = "update `web_page` set `score` = %s where `id` = %s ;"
			para = (sum, id)
			self.db_write(sql,para) # 写数据库，更新分数
			self.url_sum += sum
			pass # end of for each 
		# 现在已经对每个URL评分结束了
		# 现在是对这个人进行风险评估
		# URL部分
		a = self.eva_standard['baidu']['url']['each_url']['value']
		self.url_sum = self.url_sum * a
		if self.url_sum > 100:
			self.url_sum = 100
			pass
		# 现在还是在满分100分的状态下
		# print self.url_sum
		# URL部分结束
		# 下面是对数量进行评分
		sql = "select sum(item_count) from search_result where target_user_id = %s ;"
		para = (self.pid)
		result = self.db_read(sql,para)
		count = result[0][0]
		a = self.eva_standard['baidu']['count']['each']['value']
		# print type(a)
		# print type(self.url_count)
		self.url_count = a * float(count)
		if self.url_count > 100:
			self.url_count = 100 # 满分100
		# print self.url_count
		# 现在计算这个人的总分
		# 百度的，满分100
		a1 = self.eva_standard['baidu']['url']['value'] 
		a2 = self.eva_standard['baidu']['count']['value']
		self.score = a1 * self.url_sum + a2 * self.url_count
		print self.score # 这个就是总分
		# 计算总得分完毕
		# 数量评分结束
		# 现在应该写数据库了
		sql = "update person_status SET baidu_score = %s , baidu_count = %s WHERE target_user_id = %s"
		para = (self.score , self.risk_count , self.pid)
		self.db_write(sql,para)
		# 写数据库结束
		# 关闭数据库连接，函数结束
		self.db_close()
		pass # end of the function evaluate
	# 这个函数是命名实体识别的得分
	def evaluate_nlp(self,text,input_url):
		# print type(text)
		if text == 'Failed':
			return 0
		else:
			pass
		# 如果值得做识别，下面开始识别
		each = nlp(content = text,url = input_url)
		try:
			each.run()
		except:
			# 如果出错，以后再完善
			pass
		# 识别出来的明明实体，放到一个列表中
		score = 0
		entity_list = []
		# 添加公司名
		for i in each.company_name:
			entity_list.append(i)
			pass 
		# 添加 产品名称 
		for i in each.product_name:
			entity_list.append(i)
			pass
		# 添加 组织名称
		for i in each.org_name:
			entity_list.append(i)
			pass
		valid_list = []
		# 现在已经成功添加了未知实体的列表
		# 下面开始，先对未知的命名实体信息写入数据库
		# 同时把不属于无关信息的实体放进列表 
		for each_word in entity_list:
			each_word = each_word.encode('utf-8')
			# 下面时录入数据库
			if each_word in self.irrelevant:
				pass
			elif self.check_word_exists(each_word):
				self.update_unknown_word_count(each_word)
			else:
				self.add_unknown_word(each_word)
			# 计算分数的 
			if each_word not in self.irrelevant:
				valid_list.append(each_word)
			# print each_word
			pass # end of for each_word
		# 现在数据库操作完成了
		a1 = self.eva_standard['baidu']['url']['each_url']['nlp']['each_word']['value']
		# 列表去重
		valid_list = list(set(valid_list))
		score = a1 * len(valid_list)
		if score > 100:
			score = 100
		else:
			pass
		# print score
		return score
		pass
	# 导入无关词语列表
	def load_irrelevant_words(self):
		irr_list = self.key_word_list
		# 再从数据看里面读
		sql = "select word from unknown_word where irrelevent = 1"
		para = ()
		result = self.db_read(sql,para)
		for i in result:
			irr_list.append(i[0].encode('utf-8'))
		# 返回列表
		return irr_list
		pass
	# 检查是否存在
	def check_word_exists(self,word):
		sql = u"select word from unknown_word where word_md5 = md5(%s) and company_id = %s;"
		para = (word, self.cid)
		result = self.db_read(sql,para)
		try:
			if len(result) > 0:
				return True
		except:
			pass
		if result is ():
			return False
		elif result is None:
			return False
		else:
			return True
		pass
	# 更新关键词的count
	def update_unknown_word_count(self,word):
		sql = "select id,count from unknown_word where word_md5 = md5(%s) and company_id = %s ;"
		para = (word,self.cid)
		result = self.db_read(sql,para)
		id = result[0][0]
		count = result[0][1]
		sql = "update unknown_word set count = %s where id = %s"
		para = (count + 1, id)
		self.db_write(sql,para)
		pass
	# 添加新的未知实体信息
	def add_unknown_word(self,word):
		sql = u"INSERT INTO `unknown_word`( `id` ,`word`, `word_md5`, `company_id`, `count`, `irrelevent`) VALUES (NULL, %s ,md5( %s ), %s,1,0);"
		para = (word, word, self.cid)
		self.db_write(sql ,para)
		pass
	# 针对文本信息进行风险评估
	# 统计关键词个数，返回分数
	def count_key_words(self,plainText,url):
		text = plainText.encode('utf-8')
		sum = 0
		score = {}
		score[1] = 0
		score[2] = 0
		score[3] = 0
		score[10] = 0
		# 把score设置成字典？
		for i in self.key_wd_dict:
			score[self.key_wd_dict[i]] = text.count(i)  + score[self.key_wd_dict[i]]
			# 计算各个词出现的个数
			pass # end of for i 
		score[1] = score[1] * self.eva_standard['baidu']['url']['each_url']['kw']['level_1']['each']['value']
		score[2] = score[2] * self.eva_standard['baidu']['url']['each_url']['kw']['level_2']['each']['value']
		score[3] = score[3] * self.eva_standard['baidu']['url']['each_url']['kw']['level_3']['each']['value']
		# 然后是一种“削平”的操作
		for i in score:
			if score[i] > 100:
				score[i] = 100
			else:
				pass 
			pass # end of for i
		a1 = self.eva_standard['baidu']['url']['each_url']['kw']['level_1']['value']
		a2 = self.eva_standard['baidu']['url']['each_url']['kw']['level_2']['value']
		a3 = self.eva_standard['baidu']['url']['each_url']['kw']['level_3']['value']
		sum = a1 * score[1] + a2 * score[2] + a3 * score[3]
		if score[10] > 0:
			# 一票否决类型的词
			return 100
			pass # end of score[10]
		if ('wenku.baidu.com' in url) | ('www.docin.com' in url):
			# 动态内容不能解析，但是百度给出的结果通常都比较准确
			# print url
			if sum > 0:
				return sum + 70
			else:
				pass
			return sum 
		if self.name in text:
			return sum
		else:
			return 0
		pass# end of the function

		


def main():
	example = person(8)
	# example.db_init()
	# sql = u"SELECT * FROM `search_result` WHERE `search_condition_md5` = md5(%s)"
	# para = ('刘时勇+成飞')
	# result = example.db_read(sql,para)
	# print result
	# result = example.db_read(sql,para)
	# print result
	# example.db_close()
	# for i in example.wd_list:
	# 	print i
	# for i in example.wd_combine_list:
	# 	print i
	# example.run()
	# print example.wd_list
	# print time.ctime() + ' Start Requests'
	# t1 = time.time()
	# for url in example.url_dict:
	# 	r = requests.get(url)
	# 	pass # end of for
	# print time.ctime() + ' End Requests'
	# print str(time.time() - t1)
	# example.url_dict['directlink'] = '中文'
	# example.write_web_page('directlink','real_url','plainText')
	# print example.check_directlink_exist('directlink')
	# print example.check_url_exist('real_url')
	# example.collect()
	example.evaluate()
	# for i in example.key_wd_dict:
	# 	print i +  str(example.key_wd_dict[i])
	# print example.check_word_exists('腾讯微博')
	# example.update_unknown_word_count('腾讯微博')


if __name__ == "__main__":
	main()