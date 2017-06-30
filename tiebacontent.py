#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''百度贴吧内容获取模块'''

import requests
import json
import processparams # 自定义模块

# MainPage类按贴吧名称获取首页内容
class MainPage(object):
	def __init__(self, forum, pn=1, rn=6):
		self.forum = forum
		params = {'kw': forum, 'pn': pn, 'rn': rn, '_client_version': '5.1.0'}
		self.data = processparams.Process(**params) # 调用自定义模块processparams
		self.url = 'http://c.tieba.baidu.com/c/f/frs/page'
	def GetList(self): # return Info(json to dict)
		trynum = 0
		while trynum < 5: # 最多重试 5次以解决莫名的json解析错误或thread_list缺失
			r = requests.post(self.url, data=self.data, timeout=2)
			try:
				Info = json.loads(r.text)
				thread_list = Info['thread_list']
				trynum = 100 # 跳出循环
				return thread_list
			except:
				trynum += 1
		return []
	def Threadlist(self): # return list[(tid, reply_num, last_time_int, last_replyer, replyer_name), ...]
		thread_list = self.GetList()
		def threadinfo(thread):
			tid = thread['tid']
			if tid == '' or thread['title'] == None: # 贴子列表内的广告tid等都为空字符串
				return None
			title = thread['title'].encode('gbk', 'ignore').decode('gbk')
			reply_num = thread['reply_num']
			last_time_int = thread['last_time_int']
			last_re = thread['last_replyer'] # 访谈话题直播时没有此项和create_time, 因此加入一次判断
			last_replyer = ''
			replyer_name = ''
			if last_re != '':
				last_replyer = last_re['id']
				replyer_name = last_re['name']
			info = (tid, title, reply_num, last_time_int, last_replyer, replyer_name)
			return info
		t_list = list(map(threadinfo, thread_list))
		result = list(filter(lambda m: m, t_list)) # 过滤返回值为None的thread
		return result
	def Foruminfo(self): # 获取该贴吧的会员和贴子数量等信息,比较少用到
		trynum = 0
		while trynum < 5: # 最多重试 5次以解决莫名的json解析错误或thread_list缺失
			r = requests.post(self.url, data=self.data, timeout=2)
			try:
				Info = json.loads(r.text)
				forum = Info['forum']
				foruminfo = (forum['name'], forum['slogan'], forum['member_num'], forum['thread_num'],forum['post_num'])
				trynum = 100 # 跳出循环
				return foruminfo
			except:
				trynum += 1

# Thread类按贴子号tid获取贴子内容
class Thread(object):
	def __init__(self, tid):
		self.tid = tid 
		self.url = 'http://c.tieba.baidu.com/c/f/pb/page'
	def GetThread(self, pn=1, rn=3, with_floor=0, r=0, lz=0):
		params = {'kz': self.tid, 'pn': pn, 'rn': rn, 'with_floor': with_floor, 'r': r, 'lz': lz, '_client_version': '5.1.0'}
		data = processparams.Process(**params) # 调用自定义模块processparams
		try:
			r = requests.post(self.url, data=data, timeout=2)
			Info = json.loads(r.text)
			return Info
		except:
			return {'error_msg': '获取贴子信息失败'}
	def ThreadInfo(self, pn=1, rn=3, with_floor=0, r=0, lz=0):
		Info = self.GetThread(pn, rn, with_floor, r, lz)
		if 'error_code' not in Info:
			return '连接超时?', None, Info['error_msg']
		if Info['error_code'] != '0':	# 贴子可能被删除的错误代码为4
			return '获取失败', None, Info['error_msg']
		title = Info['thread']['title']
		author = Info['thread']['author']['name']
		post_list = Info['post_list']
		def Authorinfo(author): # 获取作者信息(name, portrait, level, id)
			return author['name'], author['portrait'].split('?')[0], author['level_id'], author['id']
		def Content(co_list): # 获取具体楼层内容(text, [imgs1, imgs2..])
			text, imgs= '', []
			def contype(con):
				text = ''
				if con['type'] in ['0', '1', '4', '5', '9']:
					text = con['text'].replace('\n', '')
				if con['type'] == '2':
					text = '<表情:%s>' % con['c']
				if con['type'] == '10':
					text = '<语音>' + con['voice_md5'][:12]
				if con['type'] == '3' or con['type'] == '16':
					if 'cdn_src' in con:
						img = (con['cdn_src'].split('/')[-1],)
						return img
				return text
			content = list(map(contype, co_list))
			for c in content:
				if type(c) == str:
					text += c
				else:
					imgs.append(c)
			return text.encode('gbk', 'ignore').decode('gbk'), imgs
		def PostInfo(post):	# 获取回贴的最主要信息：[pid, author, time, content]
			pid = post['id']
			re_author = Authorinfo(post['author'])
			re_time = int(post['time'])
			if re_author[0] == '贴吧触点推广':
				re_content = '', []
			else:
				re_content = Content(post['content'])
			return [pid, re_author, re_time, re_content]
		p_list = list(map(PostInfo, post_list))
		return title, author, p_list

# TbImage类获取贴吧贴子的相关图片
class TbImage(object):
	def __init__(self, item):
		self.item = item
	def GetSrcImg(self): # 获取原始未压缩的最大图片
		if self.item[-1] != 'g': # 不以jpg或png结尾的放弃
			return None
		url = 'http://imgsrc.baidu.com/forum/pic/item/' + self.item
		r = requests.get(url, timeout=2)
		return r # 返回的是二进制形式的图像数据

if __name__=='__main__':
	print('百度贴吧内容获取模块')
	# print('测试李毅吧：')
	# m = MainPage('李毅')
	# c = m.Threadlist()
	# for x in c:
	# 	print(x)
	t = Thread('1000000000')
	print(t.LastPost())
