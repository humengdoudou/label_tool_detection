# -*- coding: utf-8 -*-

# This is the python code for object bounding box label tool
#
# I use the BBox-Label-Tool by labelling image as the following format in txt:
# 4
# coat 43 93 254 375
# pants 58 365 216 665
# shoes 26 663 90 717
# shoes 176 665 236 719
#
# the first line 4 is the total object num,
# the rest 4 lines represents each bbox coordinate as (class, top_x, top_y, button_x, button_y)
#
# the validation check is very easy, the first line number = total txt lines - 1
# from 2th line to end, each line contains a valid class label in CLASS_LABELS, and the rest are 4 numbers
#
# reference:
# 1 https://github.com/puzzledqs/BBox-Label-Tool
#
# Author: hzhumeng01 2018-01-23

from __future__ import print_function
import os
import sys

import random
import argparse
import cv2
import time
import traceback
import numpy as np

import os.path
import shutil

ROOT_PATH    = "/label_tool_detection/Labels/20180123/"
CLASS_LABELS = ['coat', 'pants', 'glasses', 'hat', 'shoes', 'bag']

def check_label_valid(root_path):

    # val root file folder
    if not os.path.exists(root_path):
        print ("Are you kidding?! path do not exists!!!!")

    # for each path, subdirs is the sub-dir, files include all images in path
    for path, subdirs, files in os.walk(root_path, followlinks=True):
        for file_name in files:
            # print((os.path.join(root_path, name)))

            with open(os.path.join(root_path, file_name), "r") as f_read:
                label_lines = f_read.readlines()

                int_label_num = int(label_lines[0].strip())
                if int_label_num != len(label_lines) - 1:
                    print ("wrong label txt:" , file_name)
                    print ("label num and object num unmatched")

                count = 0
                for each_line in label_lines:
                    if count == 0:    # first line, just the object num
                        count += 1
                        continue

                    labels = each_line.strip().split(" ")

                    if len(labels) != 5:
                        print("wrong label txt:", file_name)
                        print("wrong label format")

                    if labels[0] not in CLASS_LABELS:
                        print("wrong label txt:", file_name)
                        print("label class is not in classLabels")

                    for coordinate in labels[1:]:
                        if not coordinate.isdigit():
                            print("wrong label txt:", file_name)
                            print("label coordinate is not the digit in classLabels")

    print ("all ok!!!")


if __name__ == '__main__':

    check_label_valid(ROOT_PATH)
