#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 12:26:33 2019

@author: wqf
"""

import cv2
import os
import glob as gb

def video_to_image():
    #要提取视频的文件名，隐藏后缀
    sourceFileName='new'
    #在这里把后缀接上
    video_path = os.path.join("", "", sourceFileName+'.mp4')
    times=0
    #提取视频的频率，每25帧提取一个
    frameFrequency=1
    #输出图片到当前目录vedio文件夹下
    outPutDirName='vedio/'+sourceFileName+'/'
    if not os.path.exists(outPutDirName):
        #如果文件目录不存在则创建目录
        os.makedirs(outPutDirName) 
    camera = cv2.VideoCapture(video_path)
    while True:
        times+=1
        res, image = camera.read()
        if not res:
            print('not res , not image')
            break
        if times%frameFrequency==0:
            cv2.imwrite(outPutDirName + str(times)+'.jpg', image)
            print(outPutDirName + str(times)+'.jpg')
    print('图片提取结束')
    camera.release()


#import cv2
#from cv2 import VideoWriter,VideoWriter_fourcc,imread,resize
#import os

def image_to_video():
    
    #import glob as gb
    #import cv2

    img_path = gb.glob("vedio/tool/*.jpg") 
    videoWriter = cv2.VideoWriter('test.mp4', cv2.VideoWriter_fourcc(*'MJPG'), 1, (1080, 1920))

    for path in img_path:
        img  = cv2.imread(path) 
        img = cv2.resize(img,(1080, 1920))
        videoWriter.write(img)
#    img_root="vedio/tool"
#    #Edit each frame's appearing time!
#    fps=5
#    fourcc=VideoWriter_fourcc(*"MJPG")
#    videoWriter=cv2.VideoWriter("toolvedio.avi",fourcc,fps,(1200,1200))
#    
#    im_names=os.listdir(img_root)
#    for im_name in range(len(im_names)):
#    	frame=cv2.imread(img_root+str(im_name)+'.jpg')
#    	print (im_name)
#    	videoWriter.write(frame)
image = cv2.imread("vedio/tool/10.jpg")
print(image.shape)      
video_to_image()
#image_to_video()