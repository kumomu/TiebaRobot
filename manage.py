#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''百度贴吧吧务管理模块'''


import requests
import json
import processparams

class Manager(object):
	def __init__(self, uname, forum):
		self.name = uname
		self.forum = forum
		self.fid = self.GetFid()
	def BDUSS(self):
		BDUSS = ''
		return BDUSS
	def Cookie(self): # 这里一般用不到
		BAIDUID = ''
		Cookie = {'BAIDUID': BAIDUID, 'BDUSS': self.BDUSS()}
		return Cookie
	def GetTbs(self):
		url = 'http://c.tieba.baidu.com/c/s/tbs'
		params = {'BDUSS': self.BDUSS()}
		data = processparams.Process(**params)# 调用自定义模块processparams
		r = requests.post(url, data=data, timeout=1)
		tbs = json.loads(r.text)['tbs']
		return tbs
	def GetFid(self):
		url = 'http://tieba.baidu.com/f/commit/share/fnameShareApi'
		params = {'fname': self.forum.encode('gbk')}
		data = processparams.Process(**params)
		r = requests.post(url, data=data, timeout=1)
		foruminfo = json.loads(r.text)
		fid = foruminfo['data']['fid']
		return fid
	def DelPost(self, tid, pid):
		def DelTry():
			tbs = self.GetTbs()
			params = {'tbs': tbs, 'from': 'tieba', 'fid': self.fid, 'z': tid, 'pid': pid}
			params['BDUSS'] = self.BDUSS()
			url = 'http://c.tieba.baidu.com/c/c/bawu/delpost'
			data = processparams.Process(**params)# 调用自定义模块processparams
			r = requests.post(url, data=data, timeout=1)
			ErrorInfo = json.loads(r.text)
			return ErrorInfo
		ErrorInfo = DelTry()
		if ErrorInfo['error_code'] == '220034': # '您的操作太频繁了'
			ErrorInfo = DelTry()
		if ErrorInfo['error_code'] == '0':
			remsg = '删除成功'
		else:
			remsg = '删除失败！错误原因:%s, 错误码%s' % (ErrorInfo['error_msg'], ErrorInfo['error_code'])
		return remsg
	def BlockID(self, username, day=10):
		tbs = self.GetTbs()
		params = {'ntn': 'banid', 'tbs': tbs, 'fid': self.fid, 'word': self.forum, 'un': username, 'z': '1111111111'}
		params['BDUSS'] = self.BDUSS()
		params['day'] = str(day)
		data = processparams.Process(**params)# 调用自定义模块processparams
		url = 'http://c.tieba.baidu.com/c/c/bawu/commitprison'
		r = requests.post(url, data=data, timeout=1)
		ErrorInfo = json.loads(r.text)
		if 'un' in ErrorInfo and ErrorInfo['error_code'] == '0':
			remsg = '封禁用户: %s 成功' % ErrorInfo['un']
		elif 'error_msg' in ErrorInfo:
			remsg = '封禁用户: %s 失败！错误原因:%s' % (username, ErrorInfo['error_msg'])
		else:
			remsg = '封禁用户: %s 失败！错误原因:未知(可能没有权限)' % username
		return remsg

if __name__=='__main__':
	print('百度贴吧吧务管理模块')