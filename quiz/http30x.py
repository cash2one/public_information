import requests
import time

test_list = [u'http://www.baidu.com/link?url=Fzo3hQAmJXkrn9HCqBFpmPjOz7208VqSKkXkCylDEIAlm4P2NpnK2WnUM1I3HTIca2i5i0tP0dX1mUIK5tNiT63pcFPxAMWWE7QzpVgO0Nm', u'http://www.baidu.com/link?url=U3L5h5CP_ueSxSk_P0jeN8xHpe_QUtdhuErya7DBr15vfZLLTXzWXJgElMdFoUx6DPGG5tK6ka9ZY20yJx11yHVkLyqj8531sNNFBHhUrsW', u'http://www.baidu.com/link?url=PN1UkcFGuxrmLugadLyMDWdKFowbwHAxEnTcdAyXyC5_y-qox3Z4qlCciUCBsYEfI3Y0VsTKZYQo_-ssuBlJwzSpH2JlnwtPmzuFup1OQY_', u'http://www.baidu.com/link?url=NqD5ulvW5VlBQm1rqhUpTXID7gBq2rBy0eq8qeqfadWEos5pneqKmc8DNXzxXljS', u'https://www.baidu.com/s?wd=www.docin.com@v&vmp_ec=8895224fa2188a600ec0d18be2=d5b11id763bd1d42j82bp8025ey7N03Xbkd7ebsc5dXJddd4c6135&vmp_ectm=1467599318&from=vs&rsv_dl=0_left_v_1', u'http://www.baidu.com/link?url=L44JhmS5A0Kv3Bn5yQ6UzfazEV453v_xI-5rOQYE2g7ozGkReXAFeojgq0PI8zY-0996JxDoIWyGhlmaYIcDvxtktfQ94Q7lDts1EO4S3Pj7Ugqa-N2QkIb9A3dd3TuE', u'http://www.baidu.com/link?url=oDinIX7lVmDGrMNiahf9FW9azN7ON2lIN2ctW-OeWgvM4TrJR2vj7FyH7ykPcv7z', u'https://www.baidu.com/s?wd=www.docin.com@v&vmp_ec=8895224fa2188a600ec0d18be2=d5b11id763bd1d42j82bp8025ey7N03Xbkd7ebsc5dXJddd4c6135&vmp_ectm=1467599318&from=vs&rsv_dl=0_left_v_1']

def get_302_Location(url,time_out = 7):
	r = requests.get(url,allow_redirects = False,timeout = time_out)
	headers = {}
	if r.status_code > 300:
		headers = r.headers
	elif r.status_code == 200:
		# fix the bug that under the condition that the url does not have a redirects
		return url
	else:
		return r.status_code
	location = headers['Location']
	# print location
	return location
	pass


def main():
	t1 = time.time()
	for i in test_list:
		print get_302_Location(i)
	t2 = time.time()
	print str(t2 - t1)

if __name__ == '__main__':
	main()