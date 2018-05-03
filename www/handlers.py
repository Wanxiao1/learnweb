#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Ginkgo_wx'

import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from apis import Page, APIValueError, APIResourceNotFoundError,APIError
from aiohttp import web

from coroweb import get, post


from models import User, Comment, Blog, next_id
from config import configs
import random

import time
import queue
import argparse
import requests
import threading


COOKIE_NAME = 'Ginkgo_wx'
_COOKIE_KEY = configs.session.secret

class Dirscan(object):


	def __init__(self, scanSite, threadNum=10,scanDict="dict/dict.txt", scanOutput=0):
		self.USER_AGENTS = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
		"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
		"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
		"Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
		"Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
		"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
		"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
		"Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
		"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
		"Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
		"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
		"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
		"Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
		"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
		"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
		]
		print ('Dirscan is running!')
		self.scanSite = scanSite if scanSite.find('://') != -1 else 'http://%s' % scanSite
		print ('Scan target:',self.scanSite)
		self.scanDict = scanDict
		self.scanOutput = 'scanre/'+scanSite.rstrip('/').replace('https://', '').replace('http://', '')+'.txt' if scanOutput == 0 else scanOutput
		try:
			truncate = open(self.scanOutput,'a+')
			truncate.close()
			self.STOP_ME = False
		except:
			self.STOP_ME = True

		self.threadNum = threadNum
		self.lock = threading.Lock()
		self._random_useragent()
		self._loadHeaders()
		self._loadDict(self.scanDict)
		self._analysis404()
		

	def _loadDict(self, dict_list):

		self.q = queue.Queue()
		u=self.scanSite.rstrip('/').replace('https://', '').replace('http://', '')
		www1 = u.split('.')
		wwwlen = len(www1)
		wwwhost = ''
		s=['.rar',
		'.zip',
		'.gz',
		'.tar',
		'.tgz',
		'.tar.gz',
		'.7z',
		'.z',
		'.bz2',
		'.tar.bz2',
		'.iso',
		'.cab',]
		current_info_dic =[]
		for i in range(1, wwwlen):
		    wwwhost += www1[i]
		for j in s:	
			www1 = u.split('.')
			wwwlen = len(www1)
			wwwhost = ''	
			current_info_dic.append('/'+u + j)
			current_info_dic.append('/'+u.replace('.', '') + j)
			
			current_info_dic.append('/'+u.split('.', 1)[-1] + j)
			current_info_dic.append('/'+www1[0] + j)
			current_info_dic.append('/'+www1[1] + j)
		for s in current_info_dic:
			self.q.put(s)
		#最终生成目录如下
		#['/127.0.0.1.rar', '/127001.rar', '/0.0.1.rar', '/127.rar', '/0.rar', '/127.0.0.1.zip', '/127001.zip', '/0.0.1.zip', '/127.zip', '/0.zip', '/127.0.0.1.gz', '/127001.gz', '/0.0.1.gz', '/127.gz', '/0.gz', '/127.0.0.1.tar', '/127001.tar', '/0.0.1.tar', '/127.tar', '/0.tar', '/127.0.0.1.tgz', '/127001.tgz', '/0.0.1.tgz', '/127.tgz', '/0.tgz', '/127.0.0.1.tar.gz', '/127001.tar.gz', '/0.0.1.tar.gz', '/127.tar.gz', '/0.tar.gz', '/127.0.0.1.7z', '/127001.7z', '/0.0.1.7z', '/127.7z', '/0.7z', '/127.0.0.1.z', '/127001.z', '/0.0.1.z', '/127.z', '/0.z', '/127.0.0.1.bz2', '/127001.bz2', '/0.0.1.bz2', '/127.bz2', '/0.bz2', '/127.0.0.1.tar.bz2', '/127001.tar.bz2', '/0.0.1.tar.bz2', '/127.tar.bz2', '/0.tar.bz2', '/127.0.0.1.iso', '/127001.iso', '/0.0.1.iso', '/127.iso', '/0.iso', '/127.0.0.1.cab', '/127001.cab', '/0.0.1.cab', '/127.cab', '/0.cab']
		with open(dict_list) as f:
			for line in f:
				if line[0:1] != '#':
					self.q.put(line.strip())
		if self.q.qsize() > 0:
			print ('Total Dictionary:',self.q.qsize())
		else:
			print ('Dict is Null ???')
			quit()
	def random_x_forwarded_for(condition=False):
		if condition:
			return '%d.%d.%d.%d' % (random.randint(1, 254),random.randint(1, 254),random.randint(1, 254),random.randint(1, 254))
		else:
			return '8.8.8.8'
	def _random_useragent(self,condition=False):
		if condition:
			return random.choice(self.USER_AGENTS)
		else:
			return self.USER_AGENTS[0]
	def _loadHeaders(self):
		# 是否允许随机User-Agent
		allow_random_useragent = True

		# 是否允许随机X-Forwarded-For
		allow_random_x_forward = True
		self.headers = {
			'Accept': '*/*',
			'Referer': 'http://www.baidu.com',
			'User-Agent': self._random_useragent(allow_random_useragent),
			'Cache-Control': 'no-cache',
		}

	def _analysis404(self):
		notFoundPage = requests.get(self.scanSite + '/meiyouzhegemulu/hello.html', allow_redirects=False)
		self.notFoundPageText = notFoundPage.text.replace('/meiyouzhegemulu/hello.html', '')
		notFound = requests.get('http://www.xtqdyy.com//intraAdmin/modules/pm/include/install.php',allow_redirects=False)
		self.notFoundText = notFound.text.replace('http://www.xtqdyy.com//intraAdmin/modules/pm/include/install.php', '')

	def _writeOutput(self, result):
		self.lock.acquire()
		with open(self.scanOutput, 'a+') as f:
			f.write(result + '\n')
		self.lock.release()

	def _scan(self, url):
		html_result = 0
		try:
			html_result = requests.get(url, headers=self.headers, allow_redirects=False, timeout=3)
		except requests.exceptions.ConnectionError:
			# print 'Request Timeout:%s' % url
			pass
		finally:
			if html_result != 0:
				if html_result.status_code == 200 and html_result.text != self.notFoundPageText and html_result.text != self.notFoundText:
					print ('[%i]%s' % (html_result.status_code, html_result.url))
					self._writeOutput('%s' %  html_result.url)
			


	def run(self):
		while not self.q.empty() and self.STOP_ME == False:
			url = self.scanSite + self.q.get()
			self._scan(url)




def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		raise APIPermissionError()

def get_page_index(page_str):
	p = 1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p

def user2cookie(user, max_age):
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)


def text2html(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
	return ''.join(lines)


@asyncio.coroutine
def cookie2user(cookie_str):
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, sha1 = L
		if int(expires) < time.time():
			return None
		user = yield from User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None

@get('/')
async def index(request):
	summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	blogs = [
		Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
		Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
		Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
	]
	cookie_str=request.cookies.get(COOKIE_NAME)
	user='' 
	if cookie_str:
		if 'deleted' in cookie_str:
			user=''
			user= await cookie2user(cookie_str)
	return {
		'__template__':'index.html',
		'blogs':blogs,
		# 'page':page,
		'user':user
	}
	# user = None
	# try:
	# 	cookie_str = request.cookies.get(COOKIE_NAME)
	# 	user = await cookie2user(cookie_str)
	# except:
	# 	pass
	# return {
	# 	'__template__': 'blogs.html',
	# 	'blogs': blogs,
	# 	'user': user
	# 	}

@get('/register')
def register():
	return {
		'__template__': 'register.html'
	}

@get('/signin')
def signin():
	return {
		'__template__': 'signin.html'
	}


@post('/api/authenticate')
async def authenticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist.')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


@get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/api/users')
async def api_register_user(*, email, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = await User.findAll('email=?', [email])
	if len(users) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	await user.save()
	# make session cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


@post('/scan')
async def api_webscan(*,site,dict={'PHP'},threadNum=20):
	site=site.rstrip('/').replace('https://', '').replace('http://', '')
	#检查网站名是否正确
	if  site and  site.strip():
		
		try:
			headers = {
				'Accept': '*/*',
				'Referer': 'http://www.baidu.com',
				'User-Agent': "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
				'Cache-Control': 'no-cache',
				}
			scansite=site if site.find('://') != -1 else 'http://%s' % site
			truncate = open('scanre/'+site+'.txt','w')
			truncate.close()
			result = requests.get(scansite, headers=headers, allow_redirects=False, timeout=2)
		except:
			return {	
			'__template__': 'index.html',
			'error': '请检查您的网址！',			
			}
	else: 			
		return {	
			'__template__': 'index.html',
			'error': '请检查您的输入！',			
			}

	
	threadNum=20
	for dic in dict:
		scan = Dirscan(site,threadNum,scanDict="dict/"+dic+".txt", scanOutput=0)

		if scan!=None :
			for i in range(threadNum):
				t = threading.Thread(target=scan.run)
				t.setDaemon(True)
				t.start()
			while True:
				if threading.activeCount() <= 3 :
					break
				else:
					try:
						time.sleep(0.1)
					except KeyboardInterrupt as e:
						print ('\n[WARNING] User aborted, wait all slave threads to exit, current(%i)' % threading.activeCount())
						scan.STOP_ME = True
						break
			print ('Scan end!!!')
	re=[]
	try:
		with open('scanre/'+site+'.txt','r') as f:
			for line in f:
				re.append(line)
	except:
		with open('scanre/notfound.txt','r') as f:
			for line in f:
				re.append(line)

	return {	
	'__template__': 'index.html',
	'site': site,
	're': re,	
	}

@get('/scan')
async def aip_scan(*,site="127.0.0.1"):
	site=site.rstrip('/').replace('https://', '').replace('http://', '')
	
	re=[]
	with open(site+'.txt','r') as f:
		for line in f:
			re.append(line)
	return {
	'__template__': 'index.html',
	'site': site,
	're': re
	}
@post('/send')
async def apisend(request,*,site2):
	mailto=request.__user__.email
	re=[]
	with open(site2+'.txt','r') as f:
		for line in f:
			re.append(line)



	r = web.Response()
	r.content_type = 'application/json'
	r.body = json.dumps(site2, ensure_ascii=False).encode('utf-8')
	return r




#创建blog
# @post('/api/blogs')
# async def api_create_blog(request, *, name, summary, content):
#	 check_admin(request)
#	 if not name or not name.strip():
#		 raise APIValueError('name', 'name cannot be empty.')
#	 if not summary or not summary.strip():
#		 # raise APIValueError('summary', 'summary cannot be empty.')
#		 summary='1'
#	 if not content or not content.strip():
#		 # raise APIValueError('content', 'content cannot be empty.')
#		 content='1'
#	 blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
#	 await blog.save()
#	 return blog

# @get('/api/blogs')
# async def api_blogs(*, page='1'):
#	 page_index = get_page_index(page)
#	 num = await Blog.findNumber('count(id)')
#	 p = Page(num, page_index)
#	 if num == 0:
#		 return dict(page=p, blogs=())
#	 blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
#	 return dict(page=p, blogs=blogs)

# @get('/blog/{id}')
# async def get_blog(id):
#	 blog = await Blog.find(id)
#	 comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
#	 for c in comments:
#		 c.html_content = text2html(c.content)
#	 blog.html_content = markdown2.markdown(blog.content)
#	 return {
#		 '__template__': 'blog.html',
#		 'blog': blog,
#		 'comments': comments
#	 }
# @get('/manage/blogs/create')
# def manage_create_blog():
#	 return {
#		 '__template__': 'manage_blog_edit.html',
#		 'id': '',
#		 'action': '/api/blogs'
#	 }

# @get('/api/blogs/{id}')
# async def api_get_blog(*, id,page='1'):
#	 blog = await Blog.find(id)
#	 # return blog
#	 return {
#		 '__template__': 'manage_blogs.html',
#		 'page_index': get_page_index(page)
#	 }

# @get('/manage/blogs')
# def manage_blogs(*, page='1'):

#	 return {
#		 '__template__': 'manage_blogs.html',
#		 'page_index': get_page_index(page)
#	 }
