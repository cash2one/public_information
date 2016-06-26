# -*- coding: utf-8 -*-
import sys, urllib, urllib2, json


def main():
	fix_url = 'http://apis.baidu.com/weixinxi/extracter/extracter?url='
	target_url = 'http://cache.baiducontent.com/c?m=9f65cb4a8c8507ed4fece7631053803a401397634b87834e29938448e435061e5a22b8ec623f4006d7932d6257fb4e5eeaf0652160502bbc919c8a1e8abc852858d2616b2e08c31c528516b8bb4732b02b875b99b869e2ad813984afa2c4ae2744ba54120bf4e7fb581715ba7880172690ac8e381f4867be&p=c070dc16d9c118ff57ee957a110c80&newp=882a9644d2df10f10be296125849c9231611d73f6590cf512496fe4996700d1a2a22b4fb66794d58dcc17c6c04ae4a58edf63770360122bc90c38c41c9fdff6978ca28632c4a9a104c&user=baidu&fm=sc&query=%B3%C9%B7%C9%CA%B5%CF%B0%B1%A8%B8%E6&qid=ab9af08a00035b4e&p1=2'
	# url = 'http://apis.baidu.com/weixinxi/extracter/extracter?url=http%3A%2F%2Fwww.weixinxi.wang%2Fblog%2Faitrcle.html%3Fid%3D90'
	url = fix_url + target_url
	req = urllib2.Request(url)

	req.add_header("apikey", "4253cc4b92fdee52dfc4095a8e860939")

	resp = urllib2.urlopen(req)
	content = resp.read()
	if(content):
		print(content)

if __name__ == '__main__':
	main()
