import requests

def get_302_Location(url,time_out = 10):
	r = requests.get(url,allow_redirects = False,timeout = time_out)
	headers = {}
	if r.status_code > 300:
		headers = r.headers
	else:
		return r.status_code
	location = headers['Location']
	# print location
	return location
	pass


def main():
	get_302_Location('http://github.com')

if __name__ == '__main__':
	main()