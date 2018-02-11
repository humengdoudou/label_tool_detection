#!/usr/bin/env python

# This is the python code for generating image sub-patch by the label and org image
#
# the labels are labelled by the label_tool_detection, and I use the labelled .txt files to crop the sub-patch
# the procedure is very straightforward, read each labelled line in .txt files, and generate the rectangle coordinates
# to crop the image/txt name sub-patch, and save the sub-patch in each class folder
#
# Author: hzhumeng01 2018-01-23


import os
import sys
import cv2

# original whole image path
ROOT_IMAGE_ORG_PATH = "label_tool_detection/JPEGImages"

# sub-patch image save path
ROOT_IMAGE_SUB_PATH = "label_tool_detection/JPEGImages"

# label list path, where the txt labels come from
ROOT_LABEL_TXT_PATH = "label_tool_detection/Labels"

def crop_save_patch_image():

    list_txt = os.listdir(ROOT_LABEL_TXT_PATH)                        # whole .txt label files
    for i in range(0, len(list_txt)):

        txt_path = os.path.join(ROOT_LABEL_TXT_PATH, list_txt[i])     # each label image txt
        if os.path.exists(txt_path):                                  # .txt exists

            imgname  = list_txt[i].strip().split(".")[0] + ".jpg"
            img_path = os.path.join(ROOT_IMAGE_ORG_PATH, imgname)

            if os.path.exists(img_path):                              # .jpg/.jpeg/.png exists
                img = cv2.imread(img_path)

                with open(txt_path) as f_img:                         # read img ok
                    for (idx, single_class_label) in enumerate(f_img):
                        if idx == 0:    # first line is the object num in each image
                            continue

                        class_label = [t.strip() for t in single_class_label.split()]   # like: coat 62 454 131 521
                        object_label = []
                        for item in class_label[1:]:
                            object_label.append(int(item))                              # like: 62 454 131 521

                        object_class = class_label[0]                                   # like: coat
                        crop_img = img[object_label[1]:object_label[3], object_label[0]:object_label[2]]   # crop_img

                        img_patch_save_folder = os.path.join(ROOT_IMAGE_SUB_PATH, object_class)
                        if not os.path.isdir(img_patch_save_folder):      # mkdir if path not exists
                            os.mkdir(img_patch_save_folder)

                        imgpatchname = imgname.strip().split(".")[0] + "_" + str(idx) + ".jpg"     # rename img patch
                        img_patch_save_path = os.path.join(img_patch_save_folder, imgpatchname)
                        cv2.imwrite(img_patch_save_path, crop_img)                                 # image save

if __name__ == '__main__':
    crop_save_patch_image()