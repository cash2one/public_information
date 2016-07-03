#-*- coding:utf-8 -*-

# import the modules
import pymysql
import re
import time
from BaiduResult import BaiduResult

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
	url_list = [] 
	wd_list = []# 这个列表用来存放构造的关键词们
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

		pass


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



if __name__ == "__main__":
	main()