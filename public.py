# -*- coding: utf-8 -*-

from quiz.cix_gfggfgffextractor import Extractor


def main():
	# 先测试web正文抽取函数
	# 用百度快照
	url = 'https://www.aliyun.com/zixun/content/3_12_406615.html'
	exp = Extractor(url)
	text = exp.getContext()
	print text

	pass


if __name__ == '__main__':
    main()