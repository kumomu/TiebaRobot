#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'百度贴吧客户端参数md5加密'

import hashlib

def Process(*args, **kw):
	paramlist = []
	for k,v in kw.items():
		param = str(k) + '=' + str(v)
		paramlist.append(param)
	tocompute = ''.join(sorted(paramlist)) + 'tiebaclient!!!'
	md5 = hashlib.md5()
	md5.update(tocompute.encode('utf-8'))
	signkey = md5.hexdigest()
	kw['sign'] = signkey.upper()
	return kw

if __name__=='__main__':
	print('百度贴吧客户端参数md5加密模块')