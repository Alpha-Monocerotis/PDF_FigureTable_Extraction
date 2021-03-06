# -*- coding: utf-8 -*-
# Developer : Nikola Liu
# Date		: 2020.02.18
# Filename	: mm_ai_get_mask.py
# Tool		: Visual Studio Code

import os
import cv2
import gc
# from core import generate_result
from keras_segmentation.predict import predict
from mm_ai_utils import get_single_segmentation, get_segmentations
from mm_core.mm_core_utils import check_necessary_folders, check_model_file

def check_env():
    check_model_file()
    check_necessary_folders()

def get_mask_for_single_image(file_path):
    check_env()
    assert os.path.isfile(file_path), "Your file path is not valid, cannot read image file."
    try:
        image = cv2.imread(file_path)
        assert len(image.shape) == 3 and image.shape[2] == 3, "Your input image is supposed to have 3 channels"
    except Exception as e:
        print("Cannot load image from your file_path, please check it.")
        print(e)

    get_single_segmentation(file_path)
        
def get_mask_for_image_dir(input_dir):
    check_env()
    assert os.path.isdir(input_dir), "Your directory path is not valid, cannot read file from it."
    get_segmentations(input_dir)
    # for path in os.listdir(input_dir):
    #     if "jpg" in path:
    #         seg_image =  "./.cached_masks/" + path
    #         ori_image = input_dir + "/" + path
    


if __name__ == "__main__":
    extract_single_image("./examples/Material31_images_64.jpg")