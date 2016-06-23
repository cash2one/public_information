#-*- coding:utf-8 -*-
import requests
import time
import threading

'''本次改变在于对1_3中的程序封装为class，添加了多线程访问，以便于后续的开发'''

class GetBaiduResults:
    '''
        这个类用来获取百度搜索结果页面的html内容
        Version: 0.1 @ 1/11/2016
        在 1/11/2016 添加了多线程抓取网页
    '''
    content_list = []
    # 用来存储html数据的列表
    def __init__(self,key_word,page_numbers):
        # _key_word -> 搜索的关键词
        # _page_numbers -> 搜索几页内容
        # _ACCEPT 和_USER_AGENT 为2个认为定义的HTTP请求头字段
        # 以上变量均为私有
        self._key_word = key_word
        self._page_numbers = page_numbers
        self._ACCEPT = '''text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'''
        self._USER_AGENT = '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56'''
    def get_file_name(self):
        # 获取存储网页的文件名
        # 在现行版本中暂时使用日期作为文件名，该方法不是很科学，以后可以改
        curr_time = time.ctime()
        curr_time_list = curr_time.split()
        file_name = ''
        for i in curr_time_list:
            file_name = file_name + i + '_'
        return file_name
    def wirte_to_file(self,html_content,file_name):
        # 该方法用于将html写入磁盘
        file = open(file_name, mode='w')
        file.writelines(html_content)
        file.close()
    def get_html(self,key_word,page_No):
        # 该方法用于获取html内容，单次获取
        # 考虑在run方法中添加多线程，来提高速度
        # key_word -> 搜索关键字
        # page_No -> 第几页
        #-----------------------------------#
        # pn是第几页所对应的URL参数
        pn = str((page_No - 1) * 10)
        # pay_load 为 URl参数
        pay_load = {'wd':key_word,'rn':10,'ie':'utf-8','tn':'baidulocal','pn':pn}
        # http_headers 为 HTTP请求头字段  伪装成浏览器
        # 以后可以随机选择多个 用户代理 来伪装成不同的客户端进行网页的抓取
        http_headers = {'Accept':self._ACCEPT,'User-Agent':self._USER_AGENT}
        # 获取网页
        r = requests.get('http://www.baidu.com/s',params = pay_load,headers = http_headers)
        # 写入列表
        self.content_list.append(r.content)
        # print time.ctime() + ' : '+ r.url + ' -> Done!' 
        # 就不打印了
    def run(self):
        for i in xrange(self._page_numbers):
            # 首先是顺序执行的程序
            # self.get_html(self._key_word, i + 1)
            t = threading.Thread(target=self.get_html, name='Get HTML Content', args=(self._key_word,i + 1,))
            t.start()
            time.sleep(1.2)

def main():
    print '关键词： 信息安全    搜索页数：4'
    scu = GetBaiduResults('信息安全',4)
    scu.run()
    print scu.content_list[0]


if __name__ == '__main__':
    main()