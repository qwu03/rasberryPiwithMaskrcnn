#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 17:14:40 2019

@author: wqf
"""

#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import cv2
import numpy as np
import time
import urllib
import threading
import signal
import LeArm
import kinematics as kin
import RPi.GPIO as GPIO
import prediction_from_mkrcnn.prediction as pd

stream = None
bytes = ''
orgFrame = None
minFrame = None
Running = False
get_image_ok = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
key = 22
GPIO.setup(key, GPIO.IN, GPIO.PUD_UP)

correction_flag = False


color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
              }

position_color_list = []

cv_blocks_ok = False

step = 0
num_random = None

cv_count = 0

last_blocks = []
last_x = 0
stable = False

storage_blocks = []



def cv_stop(signum, frame):
    global Running

    print("Stop face detection")
    if Running is True:
        Running = False
    cv2.destroyWindow('face_detection')
    cv2.destroyAllWindows()



def cv_continue(signum, frame):
    global stream
    global Running
    if Running is False:
        
        if stream:
            stream.close()
        stream = urllib.urlopen("http://127.0.0.1:8080/?action=stream?dummy=param.mjpg")
        bytes = ''
        Running = True



signal.signal(signal.SIGTSTP, cv_stop)
signal.signal(signal.SIGCONT, cv_continue)


def get_image():
    global Running
    global orgFrame, minFrame
    global bytes
    global get_image_ok
    while True:
        if Running:
            try:
                bytes += stream.read(2048)  
                a = bytes.find('\xff\xd8')  
                b = bytes.find('\xff\xd9')  
                if a != -1 and b != -1:
                    jpg = bytes[a:b + 2]  
                    bytes = bytes[b + 2:]  
                    orgFrame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)  
                    minFrame = cv2.resize(orgFrame, (320, 240), interpolation=cv2.INTER_LINEAR)  
                    get_image_ok = True
            except Exception as e:
                print(e)
                continue
        else:
            time.sleep(0.01)



th1 = threading.Thread(target=get_image)
th1.setDaemon(True)  
th1.start()



def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def move_blocks():
    global cv_blocks_ok, position_list, step
    while True:
        if cv_blocks_ok is True:
            if len(position_list) == 1:    
                
                print(position_color_list, 'pos')
                if step == 0:
                    x_pix_cm = position_list[0][1]
                    y_pix_cm = position_list[0][2]
                    angle = position_list[0][3]
                    
                    n_x = int(leMap(x_pix_cm, 0.0, 320.0, -1250.0, 1250.0)) * 1.0
                    n_y = int(leMap(240 - y_pix_cm, 0.0, 240.0, 1250, 3250.0)) * 1.0
                    
                    if n_x < -100:
                        n_x -= 120  
                    LeArm.setServo(1, 700, 500)
                    time.sleep(0.5)
                    step = 1
                elif step == 1:
                    
                    if kin.ki_move(n_x, n_y, 200.0, 1500):
                        step = 2
                    else:
                        step = 6
                elif step == 2:
                    
                    if angle <= -45:
                        angle = -(90 + angle)
                    n_angle = leMap(angle, 0.0, -45.0, 1500.0, 1750.0)
                    if n_x > 0:
                        LeArm.setServo(2, 3000 - n_angle, 500)
                    else:
                        LeArm.setServo(2, n_angle, 500)
                    time.sleep(0.5)
                    step = 3
                elif step == 3:
                    
                    print('3 ok')
                    LeArm.setServo(1, 1200, 500)
                    time.sleep(0.5)
                    step = 4
                elif step == 4:     
                    print('4 ok')
                    kin.ki_move(n_x, n_y, 700.0, 1000)
                    step = 5
                elif step == 5:     
                    print ('5 ok')
                    if position_list[0][0] == 'red':
                        LeArm.runActionGroup('red', 1)
                    elif position_list[0][0] == 'blue':
                        LeArm.runActionGroup('blue', 1)
                    elif position_list[0][0] == 'green':
                        LeArm.runActionGroup('green', 1)
                    step = 6
                elif step == 6:     
                    print('6 ok')
                    LeArm.runActionGroup('rest', 1)
                    threadLock.acquire()
                    position_list = []
                    cv_blocks_ok = False
                    threadLock.release()
                    step = 0
        else:
            time.sleep(0.01)



th2 = threading.Thread(target=move_blocks)
th2.setDaemon(True)
th2.start()


threadLock = threading.Lock()



lens_mtx = np.array([
                [993.17745922, 0., 347.76412756],
                [0., 992.6210587, 198.08924031],
                [0., 0., 1.],
           ])
lens_dist = np.array([[-2.22696961e-01, 3.34897836e-01, 1.43573965e-03, -5.99140365e-03, -2.03168813e+00]])



def lens_distortion_adjustment(image):
    global lens_mtx, lens_dist
    h, w = image.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(lens_mtx, lens_dist, (w, h), 0, (w, h))  # 自由比例参数
    dst = cv2.undistort(image, lens_mtx, lens_dist, None, newcameramtx)
    return dst



def Arm_Pos_Corr():
    LeArm.setServo(1, 1200, 500)
    time.sleep(0.5)
    kin.ki_move(0, 2250, 200.0, 1500)

#def apply_mask(image, mask, color, alpha=0.5):
#    """Apply the given mask to the image.
#    """
#    for c in range(3):
#        image[:, :, c] = np.where(mask == 1,
#                                  image[:, :, c] *
#                                  (1 - alpha) + alpha * color[c] * 255,
#                                  image[:, :, c])
#    return image
#
#run_corr_one = 0
#cv_continue(1, 1)

LeArm.runActionGroup('rest', 1)
while True:
    if GPIO.input(key) == 0:
        time.sleep(0.1)
        if GPIO.input(key) == 0:
            correction_flag = not correction_flag
            if correction_flag is False:
                LeArm.runActionGroup('rest', 1)
    if correction_flag is False:
        run_corr_one = 0
        if minFrame is not None and get_image_ok:
            t1 = cv2.getTickCount()
            frame = lens_distortion_adjustment(minFrame)
            img_h, img_w = frame.shape[:2]
            
            img_center_x = img_w / 2
            img_center_y = img_h / 2
            if cv_blocks_ok is False:
                x,y = pd(frame)
                angle = 0
                position_list.append((int(y), int(x)), int(angle))
                cv_blocks_ok = True
            cv2.imshow('image', frame)
            cv2.waitKey(1)
            get_image_ok = False
            t2 = cv2.getTickCount()
            time_r = (t2 - t1) / cv2.getTickFrequency() * 1000
        else:
            time.sleep(0.01)
    else:
        if correction_flag and run_corr_one == 0:
            run_corr_one += 1
            Arm_Pos_Corr()
        else:
            time.sleep(0.01)


