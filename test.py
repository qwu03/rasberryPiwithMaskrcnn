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

from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
from train import BalloonConfig,CLASS_NAMES


EVENT_FOLDER='balloon20190420T1809'    
MODEL_FILE='mask_rcnn_balloon_0021.h5'   
TEST_IMGAGE='./images/13.jpg'


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

image = skimage.io.imread(TEST_IMGAGE)
cv2.imshow('image', image)
print(image.shape)

# Run detection
results = model.detect([image], verbose=1)

# Visualize results
r = results[0]
print(r['masks'])
visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],  class_names, r['scores'])
