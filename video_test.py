#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 13:53:53 2019

@author: wqf
"""

# coding: utf-8
 
 
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import cv2
import re
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
from train import BalloonConfig,CLASS_NAMES


base_dir='/Users/wqf/Desktop/Mask_RCNN/vedio/new'
target_dir='/Users/wqf/Desktop/Mask_RCNN/maskvideo2'
files=os.listdir(base_dir)
files.sort()
#print(len(files))
#print(type(files[1]))
#for i in range(1,len(files)):
#    print(type(files[i]))
#    print(float(re.findall(r"\d+\.?\d*", files[i])[0]))
##files.sort()
#print(files)
#files.sort()


EVENT_FOLDER='balloon20190420T1809'    
MODEL_FILE='mask_rcnn_balloon_0021.h5'   
TEST_IMGAGE='./vedio/jump/11.jpg'


# Directory to save logs and trained model
MODEL_DIR = os.path.join("logs",EVENT_FOLDER)

# Local path to trained weights file
COCO_MODEL_PATH =os.path.join(MODEL_DIR,MODEL_FILE)

config = BalloonConfig()
config.display()
 

# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
 
# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

 
class_names = CLASS_NAMES

#os.path.join('/Users/wqf/Desktop/Mask_RCNN/maskvideo',str(K)+'.jpg')

# images = os.listdir('images')
# for item in images:
for k in range(len(files)):
    image = skimage.io.imread(os.path.join(base_dir,str(k)+'.jpg'))
    print(k)
    #cv2.imshow('image', image)
    #print(image.shape)

    # Run detection
    results = model.detect([image], verbose=1)

    # Visualize results
    r = results[0]
    #print(r['masks'])
    K = k
    mask = visualize.display_instances_1(K,image, r['rois'], r['masks'], r['class_ids'],  class_names, r['scores'])
    #print(mask.shape)
#cv2.imwrite("./maskvideo/1.jpg", mask)