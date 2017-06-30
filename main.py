#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''百度贴吧新回贴检查主程序'''

import time
import manage # 自定义模块
import tiebanew # 自定义模块
import mainpolicy # 自定义模块
from multiprocessing.dummy import Pool as ThreadPool

class RealTimeCheck(object):
	def __init__(self, forum):
		self.forum = forum
		self.posts = tiebanew.RealTimeGet(forum)
		self.minfo = mainpolicy.ManageInfo(forum)
	def singlecheck(self):
		posts_update = self.posts.GetUpdates()
		if posts_update == []:
			return None
		for p in posts_update:
			print(p)
		pool = ThreadPool(4)
		m_listraw = pool.map(self.minfo.assesspost, posts_update)
		pool.close()
		pool.join()
		m_list = list(filter(lambda m: m, m_listraw))
		return m_list
	def checkloop(self):
		errtime = 0
		print(time.strftime('%H:%M:%S'), '启动扫描...')
		while True:
			try:
				a = self.singlecheck()
				if a:
					print(a)
				time.sleep(2)
			except:
				errtime += 1
				print('检查出错')
				time.sleep(5)
				if errtime > 10:
					time.sleep(180)

if __name__=='__main__':
	print('百度贴吧新回贴检查主程序模块')

