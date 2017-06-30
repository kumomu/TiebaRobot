#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''图像特性匹配'''

import numpy as np
import cv2

class ImgAttr(object):
	def __init__(self, imgcv):
		self.img = imgcv
	def phash_img(self):
		def phash(img_32x32):
			dct = cv2.dct(np.float32(img_32x32))
			dct_roi = dct[0:8,0:8]
			avreage = np.mean(dct_roi)
			phashlist = []
			for i in range(8):
				for j in range(8):
					if dct_roi[i,j] > avreage:
						phashlist.append('1')
					else:
						phashlist.append('0')
			phashstr = ''.join(phashlist)
			phashhex = hex(int(phashstr, 2))[2:]
			return phashstr	
		self.img_32x32 = cv2.resize(self.img,(32,32))
		self.gray_32x32 = cv2.cvtColor(self.img_32x32, cv2.COLOR_BGR2GRAY)
		imghsv_32x32 = cv2.cvtColor(self.img_32x32, cv2.COLOR_BGR2HSV)
		self.h_32x32 = imghsv_32x32[:,:,0]
		self.s_32x32 = imghsv_32x32[:,:,1]
		self.v_32x32 = imghsv_32x32[:,:,2]
		imphash = phash(self.gray_32x32)
		h_phash = phash(self.h_32x32)
		s_phash = phash(self.s_32x32)
		v_phash = phash(self.v_32x32)
		return imphash, h_phash, s_phash, v_phash

def ImgCompare_phash(img1, img2, level=9):
	imgcv1 = cv2.imread(img1)
	imgcv2 = cv2.imread(img2)
	attr1 = ImgAttr(imgcv1)
	attr2 = ImgAttr(imgcv2)
	hash1 = attr1.phash_img()
	hash2 = attr2.phash_img()
	def Hamming_distance(str1, str2):
		pnum = 0
		for index in range(len(str1)):
			if str1[index] != str2[index]:
				pnum += 1
		return (1-pnum/64)
	h0 = Hamming_distance(hash1[0],hash2[0]) # 权重0.2
	h1 = Hamming_distance(hash1[1],hash2[1]) # 权重0.3
	h2 = Hamming_distance(hash1[2],hash2[2]) # 权重0.3
	h3 = Hamming_distance(hash1[3],hash2[3]) # 权重0.2
	hvalue = h0*0.2 + h1*0.3 + h2*0.3 + h3*0.2
	if hvalue > 0.11*level:
		return True
	else:
		return False

if __name__=='__main__':
	print('图像特性匹配模块')

