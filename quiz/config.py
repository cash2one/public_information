#-*- coding:utf-8 -*-
import json

class config(object):
	@staticmethod
	def load():
		path = '/Users/guoyunzhe/Documents/conf/conf.json'
		file_object = open(path)
		try:
			text = file_object.read()
		finally:
			file_object.close()
		return json.loads(text)
	

if __name__ == "__main__":
	dict = conf.load()
	print  dict
		
 
