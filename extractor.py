import cv2
import re
import pytesseract
from pytesseract import Output
import math
import numpy as np
import argparse
from os import path

def execute(img):
	h, w = img.shape[:2]
	#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(img, 75, 150)
	lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
	alist = []
	for line in lines:
		x1,y1,x2,y2 = line[0]
		#cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
		if x2-x1 == 0:
			continue
		angle = round(math.atan((y2-y1)/(x2-x1)),1)
		#angle = angle*180/np.pi
		if abs(angle) < 1 and abs(angle)>=0.1:
			if angle not in alist: 
				alist.append(angle)
				cv2.line(img, (x1, y1), (x2, y2), (0, 0, 128), 1)
		for i in alist:
			M = cv2.getRotationMatrix2D((w/2,h/2), np.degrees(i), 1)
			fy = cv2.warpAffine(img, M, (w, h))

			text = pytesseract.image_to_string(fy)
			#print(text)
			sens = text.split('\n')
			for sen in sens:
				words = sen.split()
				for word in words:
					if word.isdigit() and len(word)==10:
						#print(word+'\n')
						return word

	return 0

def argument():

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", type=str, required=True,
		help="path to input image")
	args = vars(ap.parse_args())
	if args["image"]!='':
		main(args["image"])
	else:
		print("input correct path of image\npython3 readv3.py -i <image file path>")

def main(image):
	imag = cv2.imread(image)
	imag = cv2.cvtColor(imag, cv2.COLOR_BGR2GRAY)
	#imag = cv2.threshold(imag, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	num_pattern = r'[0-9]+'
	data = pytesseract.image_to_data(imag, output_type=Output.DICT)
	img = imag.copy()
	n_boxes = len(data['text'])
	e = 200

	for i in range(n_boxes):
		if int(data['conf'][i]) > 20:
			if re.match(num_pattern, data['text'][i]):
				(x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
				a = y-int(e/2) if y-int(e/2)>0 else 0
				b = y+h+int(e/2) if y+h+int(e/2)<imag.shape[0] else imag.shape[0]
				c = x-e if x-e>0 else 0
				d = x+w+e if x+w+e<imag.shape[1] else imag.shape[1]
				dup = imag[a:b, c:d]
				#cv2.imshow('dup', dup)
				#cv2.waitKey(0)
				img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
				res = execute(dup)
				if len(str(res))==10:
					print(res)
					break
			

	#cv2.imshow('dup', img)
	#cv2.waitKey(0)

if __name__ == '__main__':
	argument()