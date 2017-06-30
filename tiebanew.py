#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''百度贴吧获取实时最新贴子(回复)'''

import time
import tiebacontent # 自定义模块
from multiprocessing.dummy import Pool as ThreadPool

# RealTimeScan类实时获取最新贴子(回复)
class RealTimeGet(object):
	def __init__(self, forum, interval=3, with_floor=0):
		self.mainpage = tiebacontent.MainPage(forum)
		self.interval = interval
		self.with_floor = with_floor # 是否考虑楼中楼
		self.tl_earlier=[]
	def CheckUpdate(self):
		tl_new = self.mainpage.Threadlist()
		tl_updated = [t for t in tl_new if t not in self.tl_earlier]
		self.tl_earlier = tl_new
		return tl_updated
	def NewPostInfo(self,raw_info,ignoretid='4203232865'): # raw_info格式:(tid, title, reply_num, last_time_int, last_replyer, replyer_name)
		tid = raw_info[0]
		title = raw_info[1]
		last_time_int = raw_info[3]
		if tid == ignoretid:
			return {'tid':tid, 'title':title, 'pid':'0', 'author':None, 'time':last_time_int, 'content':('忽略检查该主题新回复',[])}
		thread = tiebacontent.Thread(tid)
		reverse = thread.ThreadInfo(pn=0, r=1) #倒序模式查看 reverse格式:(title, author, p_list)
		if reverse[1] == None: # '获取失败', None, Info['error_msg']
			return {'tid':'0', 'title':'None', 'pid':'0', 'author':None, 'time':'0', 'content':('没有找到更新信息',[])}
		lastpost = reverse[2][0]
		# 判断最后一个回复的作者和时间:
		lastpost_time = lastpost[2]	# lastpost格式:[pid, author, time, content]
		if int(lastpost_time) < int(last_time_int):
			return {'tid':tid, 'title':title, 'pid':'0', 'author':None, 'time':lastpost_time, 'content':('尾楼非最新回复',[])}
		newpost = {'tid':tid, 'title':title, 'pid':lastpost[0], 'author':lastpost[1], 'time':lastpost_time, 'content':lastpost[3]}
		return newpost
	def GetUpdates(self):
		tl_updated = self.CheckUpdate()
		pool = ThreadPool(4)
		t_list = pool.map(self.NewPostInfo, tl_updated)
		pool.close()
		pool.join()
		return t_list

if __name__=='__main__':
	print('百度贴吧获取实时最新贴子(回复)模块')