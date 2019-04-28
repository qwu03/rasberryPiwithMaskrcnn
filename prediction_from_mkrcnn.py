# coding: utf-8
 
"""
Created on Sat Apr 27 17:14:40 2019

@author: wqf
"""
 
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import cv2
import statistics

from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
from train import BalloonConfig,CLASS_NAMES



def get_mask_center(mask):
        horizontal_indicies = np.where(np.any(mask, axis=0))[0]
        vertical_indicies = np.where(np.any(mask, axis=1))[0]
        w = max(horizontal_indicies) - min(horizontal_indicies)
        h = max(vertical_indicies) - min(vertical_indicies)
        if w > h:
            x = statistics.median(horizontal_indicies)
            y_index = horizontal_indicies.index(x)
            y = vertical_indicies(y_index)
            return x,y
        else:
            y = statistics.median(horizontal_indicies)
            x_index = horizontal_indicies.index(y)
            x = vertical_indicies(x_index)
            return x,y



def prediction(image):
    EVENT_FOLDER='balloon20190420T1809'    
    MODEL_FILE='mask_rcnn_balloon_0021.h5'   
    #TEST_IMGAGE='./images/13.jpg'
    
    
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
    
    # images = os.listdir('images')
    # for item in images:
    
    #image = skimage.io.imread(TEST_IMGAGE)
    cv2.imshow('image', image)
    print(image.shape)
    
    # Run detection
    results = model.detect([image], verbose=1)
    
    # Visualize results
    r = results[0]
    visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],  class_names, r['scores'])

    x,y = get_mask_center(r['masks'])
    return x,y

