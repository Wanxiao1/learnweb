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


import time
import queue
import argparse
import requests
import threading


COOKIE_NAME = 'Ginkgo_wx'
_COOKIE_KEY = configs.session.secret

class Dirscan(object):

	def __init__(self, scanSite, threadNum=10,scanDict="dict/dict.txt", scanOutput=0):
		print ('Dirscan is running!')
		self.scanSite = scanSite if scanSite.find('://') != -1 else 'http://%s' % scanSite
		print ('Scan target:',self.scanSite)
		self.scanDict = scanDict
		self.scanOutput = 'scanre/'+scanSite.rstrip('/').replace('https://', '').replace('http://', '')+'.txt' if scanOutput == 0 else scanOutput
		try:
			truncate = open(self.scanOutput,'w')
			truncate.close()
			self.STOP_ME = False
		except:
			self.scanOutput=r"scanre/notfound.txt"
			truncate = open(self.scanOutput,'w')
			truncate.write("site is not found!")
			truncate.close()
			self.STOP_ME = True
		self.threadNum = threadNum
		self.lock = threading.Lock()
		self._loadHeaders()
		self._loadDict(self.scanDict)
		self._analysis404()
		

	def _loadDict(self, dict_list):
		self.q = queue.Queue()
		with open(dict_list) as f:
			for line in f:
				if line[0:1] != '#':
					self.q.put(line.strip())
		if self.q.qsize() > 0:
			print ('Total Dictionary:',self.q.qsize())
		else:
			print ('Dict is Null ???')
			quit()

	def _loadHeaders(self):
		self.headers = {
			'Accept': '*/*',
			'Referer': 'http://www.baidu.com',
			'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; ',
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
async def api_webscan(*,site,dict=['PHP'],threadNum=20):
	if not site or not site.strip():		
		return {	
		'__template__': 'index.html',
		'error': '请检查您的输入！',			
		}

	site=site.rstrip('/').replace('https://', '').replace('http://', '')
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
