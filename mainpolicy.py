#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''百度贴吧新回贴检查主策略'''

import re
import os
import manage # 自定义模块
import imghash # 自定义模块
import temppolicy # 自定义模块, 临时策略
import tiebacontent # 自定义模块

class Settings(object):
	def __init__(self, forum):
		self.forum = forum
		self.KeyWords()
		self.BlackList()
		# self.WhiteList()
		self.ImgMatchList()
	def KeyWords(self):
		with open('删贴匹配关键词.js', 'r', encoding='utf-8') as f:
			keywords = eval(f.read())
		titlecomp = list(map(lambda x: re.compile(x), keywords['title']))# 创建一堆正则匹配pattern实例
		postcomp = list(map(lambda x: re.compile(x), keywords['post']))
		usercomp = list(map(lambda x: re.compile(x), keywords['user']))
		self.kwcompile = {'title':titlecomp, 'post':postcomp, 'user':usercomp}
	def BlackList(self):
		with open('删封匹配黑名单.js', 'r', encoding='utf-8') as f:
			blacklist = eval(f.read())
		tibancomp = list(map(lambda x: re.compile(x), blacklist['title']))# 创建一堆正则匹配pattern实例
		pobancomp = list(map(lambda x: re.compile(x), blacklist['post']))
		ubancomp = list(map(lambda x: re.compile(x), blacklist['user']))
		self.bkcompile = {'title':tibancomp, 'post':pobancomp, 'user':ubancomp}
	# def WhiteList(self):
	# 	self.whitelist = {'tid':['4203232865', '测试tid2'], 'user':['贴吧触点推广', '测试用户8']}
	def ImgMatchList(self):
		self.imglist = ['.\\ImgMatch\\' + x for x in os.listdir('.\\ImgMatch\\') if os.path.splitext(x)[1]=='.jpg']

class AssessPost(object):
	def __init__(self, post):
		self.tid, self.pid = post['tid'], post['pid']
		self.title, self.author = post['title'], post['author'] # tuple(name, portrait, lv, id)
		self.text, self.imgs = post['content'][0], post['content'][1]# tuple(text, [imgs1, imgs2..])
	def assesstitle(self, bantitle_list):
		# 标题分析判定, flag区分是Del还是Ban操作
		timatch =  list(map(lambda kw: str(kw)[12:-2] if kw.search(self.title) else None, bantitle_list))
		result = list(filter(lambda u: u and u.strip(), timatch))
		if result:
			return [self.tid, self.pid, self.author[0], self.title, '触发标题屏蔽: %s' % '&'.join(result)]
		t = temppolicy.assesstitle(self.text)
		if t:
			return [self.tid, self.pid, self.author[0], self.title, '标题临时策略:%s' % t]
	def assessuname(self, banuname_list):
		# 用户名分析判定
		unamematch = list(map(lambda kw: str(kw)[12:-2] if kw.search(self.author[0]) else None, banuname_list))
		result = list(filter(lambda u: u and u.strip(), unamematch))
		if result:
			return [self.tid, self.pid, self.author[0], self.text, '触发用户屏蔽: %s' % '&'.join(result)]
		t = temppolicy.assessuname(self.text)
		if t:
			return [self.tid, self.pid, self.author[0], self.text, '用户临时策略:%s' % t]
	def assesspost(self, banpost_list):
		# 贴子文字内容分析判定
		postmatch = list(map(lambda kw: str(kw)[12:-2] if kw.search(self.text) else None, banpost_list))
		result = list(filter(lambda p: p and p.strip(), postmatch))
		if result:
			return [self.tid, self.pid, self.author[0], self.text, '触发内容屏蔽: %s' % '&'.join(result)]
		t = temppolicy.assesspost(self.text)
		if t:
			return [self.tid, self.pid, self.author[0], self.text, '内容临时策略:%s' % t]	
	def assessimage(self, banimage_list):
		# 图片内容分析判定
		if self.imgs == []:
			return None
		item = self.imgs[0][0] #对第一张图片进行分析, 如要多张图分析可循环
		imgr = tiebacontent.TbImage(item).GetSrcImg()
		imgsave = '.\\__testimgcache__\\%s' % item # 用百度图片item值命名图片
		with open(imgsave, 'wb') as f:
			f.write(imgr.content)
		imgmatch = list(map(lambda img: imghash.ImgCompare_phash(imgsave, img), banimage_list))
		for i in range(len(banimage_list)):
			if imgmatch[i]:
				return [self.tid, self.pid, self.author[0], item, '匹配图像像素:%s' % banimage_list[i]]
		t = temppolicy.assessimage(imgsave)
		if t:
			return [self.tid, self.pid, self.author[0], item, '图片临时策略:%s' % t]

class ManageInfo(object):
	def __init__(self, forum):
		settings = Settings(forum)
		self.keywords = settings.kwcompile
		self.blacklist = settings.bkcompile
		self.imglist = settings.imglist
		self.manage = manage.Manager('管理员', forum)
	def assesspost(self, post):
		ap = AssessPost(post)
		if ap.author == None:
			return None
		at_del = ap.assesstitle(self.keywords['title'])
		au_del = ap.assessuname(self.keywords['user'])
		ap_del = ap.assesspost(self.keywords['post'])
		for ad in [at_del, au_del, ap_del]:
			if ad:
				tid, pid = ad[0], ad[1]
				managemsg = self.manage.DelPost(tid, pid)
				ad.append(managemsg)
				return ad
		if int(ap.author[2]) > 7: # 用户等级大于7时不检查是否广告号
			return None
		at_ban = ap.assesstitle(self.blacklist['title'])
		au_ban = ap.assessuname(self.blacklist['user'])
		ap_ban = ap.assesspost(self.blacklist['post'])
		ai_ban = ap.assessimage(self.imglist)
		for ab in [at_ban, au_ban, ap_ban, ai_ban]:
			if ab:
				tid, pid, author = ab[0], ab[1], ab[2]
				managemsgd = self.manage.DelPost(tid, pid)
				managemsgb = self.manage.BlockID(author)
				managemsg = managemsgd+' '+managemsgb
				ab.append(managemsg)
				return ab

if __name__=='__main__':
	print('百度贴吧新回贴检查主策略模块')