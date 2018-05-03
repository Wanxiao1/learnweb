

import requests
import queue
from copy import deepcopy

dic=None
u='127.0.0.1'
q = queue.Queue()
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
# [print(i) for i in current_info_dic]
""" 最终每个url对应可以扫描的字典部分如下
['web.rar', 'web.zip', 'backup.rar', 'www.rar', 'bak.rar', 'wwwroot.zip', 'bak.zip', 'www.zip', 'wwwroot.rar', 'backup.zip', 'www.test.gov.cn.rar', 'www.test.gov.cn.zip', 'wwwtestgovcn.rar', 'wwwtestgovcn.zip', 'testgovcn.rar', 'testgovcn.zip', 'test.gov.cn.rar', 'test.gov.cn.zip']
['web.rar', 'web.zip', 'backup.rar', 'www.rar', 'bak.rar', 'wwwroot.zip', 'bak.zip', 'www.zip', 'wwwroot.rar', 'backup.zip', 'www.baidu.com.rar', 'www.baidu.com.zip', 'wwwbaiducom.rar', 'wwwbaiducom.zip', 'baiducom.rar', 'baiducom.zip', 'baidu.com.rar', 'baidu.com.zip']
"""

# for info in current_info_dic:
#     if u.startswith('http://') or u.startswith('https://'):
#         url = str(u) + '/' + str(info)
#     else:
#         url = 'http://' + str(u) + '/' + str(info)
#     q.put(url)
print (current_info_dic)