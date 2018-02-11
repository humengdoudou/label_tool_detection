#!/usr/bin/env python

# This is the python code for creating trainval/test .txt for fitting the pascal voc format
#
# the procedure is very straightforward, read the whole labelled image txt, get their name list,
# random shuffle the list, and finally split the list into trainval/test
# the trainval/test ratio settings is done by VAL_NUM_END/TRAIN_NUM_END
#
# Author: hzhumeng01 2018-01-23

import os
import sys
import random

ROOT_PATH = "bbox_label_tool/Labels/20171129/"

VAL_NUM_END   = 175     # 0 ~ VAL_NUM_END: val images num and list index
TRAIN_NUM_END = 975     # VAL_NUM_END ~ TRAIN_NUM_END: val images num and list index

def create_trainval_label(root_path):

    # val root file folder
    if not os.path.exists(root_path):
        print ("Are you kidding?! path do not exists!!!!")

    file_name_list = []

    # for each path, subdirs is the sub-dir, files include all images in path
    for path, subdirs, file_names in os.walk(root_path, followlinks=True):
        for file_name_with_exts in file_names:
            file_name = file_name_with_exts.strip().split(".")[0]
            file_name_list.append(file_name)

    return file_name_list


if __name__ == '__main__':
    file_name_list = create_trainval_label(ROOT_PATH)

    print (len(file_name_list))

    random.seed(100)
    random.shuffle(file_name_list)

    testFile  = open('test.txt', 'w')
    trainFile = open('trainval.txt', 'w')

    # 175 images for val/test, 800 images for train
    for i in range(VAL_NUM):
        testFile.write(str(file_name_list[i]) + '\n')

    for j in range(VAL_NUM_END, TRAIN_NUM_END, 1):
        trainFile.write(str(file_name_list[j]) + '\n')
