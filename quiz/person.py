#-*- coding:utf-8 -*-

# import the modules
import pymysql
import re
import time
from BaiduResult import BaiduResult
import requests
import sys

db_pass_word = 'Zh-L3z34IokS6fGze'
db_name = 'risk_assessment_system'


class person(object):
	# 变量定义
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
			self.key_wd_dict[i] = 2 # 默认等级为2
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
		# 首先对不需要详细URL的关键词搜索 
		for i in self.wd_list:
			each = BaiduResult(i,self.pid)
			each.run(onlyCount = True)
		for i in self.wd_combine_list:
			each_combine = BaiduResult(i,self.pid)
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
		# 现在要执行数据采集工作
		for direct_url in self.url_dict:
			exists = self.check_directlink_exist(direct_url)
			if exists:
				# 如果存在，仅更新时间
				print 'exist'
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
		# 先连接数据库
		self.db_init()
		# 我们已经有了关键词表 self.key_wd_dict
		sql = "select `id`, `plain_text` from `web_page` where `target_user_id` = %s and evaluate = 'False'"
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
		for each in result:
			print self.count_key_words(each[1])
		# 关闭数据库连接，函数结束
		self.db_close()
		pass # end of the function evaluate
	# 针对文本信息进行风险评估
	# 统计关键词个数，返回分数
	def count_key_words(self,plainText):
		text = plainText.encode('utf-8')
		score = 0 # 初始分数
		for i in self.key_wd_dict:
			score = text.count(i) * self.key_wd_dict[i] + score
			pass # end of for i 
		return score
		pass# end of the function

		


def main():
	example = person(6)
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
	


if __name__ == "__main__":
	main()