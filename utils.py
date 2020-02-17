# -*- coding: utf-8 -*-
# Developer : Nikola Liu
# Date		: 2020.02.17
# Filename	: tools.py
# Tool		: Visual Studio Code

# import fitz
import os
import datetime
import cv2
import numpy as np
import matplotlib.pyplot as plt
from cnocr import CnOcr
from keras_segmentation.predict import predict_multiple

def extract_text_from_image(path):
    """ CRNN to recognize text"""
    ocr = CnOcr()
    res = ocr.ocr_for_single_line(path)
    return ''.join(res)


# def pdf2img(pdf_path, image_path='./images'):
#     """ Convert PDF pages to PNG images.
#     Args:
#         pdf_path: Path of PDF file
#         image_path: Path of target images

#     Returns:
#         None
#     """

#     start_time = datetime.datetime.now()

#     print("Your images will be saved in directory: " + image_path)
#     pdf_doc = fitz.open(pdf_path)
#     for pg in range(pdf_doc.pageCount):
#         page = pdf_doc[pg]
#         rotate = int(0)
#         zoom_x = 1.6666666
#         zoom_y = 1.6666666
#         mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
#         pix = page.getPixmap(matrix=mat, alpha=False)

#         if not os.path.exists(image_path):
#             os.makedirs(image_path)

#         pix.writePNG(
#             image_path +
#             '/' +
#             pdf_path.split('.')[1].split('/')[2] +
#             '_' +
#             'images_%s.jpg' %
#             pg)
#     end_time = datetime.datetime.now()


def convert(input_path, output_path, target_size):
    """ Convert images to a scaled size(target_size).
    Args:
        input_path: Path of input image
        output_path: Path of resize image
        target_size: Size of target imag

    Returns:
        None

    """
    assert len(target_size) == 2, TypeError(
        "Length of target_size should be 2")
    file_list = os.listdir(input_path)
    for file_name in file_list:
        in_path = input_path + '/' + file_name
        img = cv2.imread(in_path)
        cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        out_path = output_path + '/' + file_name
        cv2.imwrite(out_path, img)


def inverse_convert(detect_rects, convert_size, original_size):
    """
    Args:
        detect_rects: Rectangle areas of detected object [(0,0) is left-up point]
        convert_size: Target size in convert()
        original_size: Original size of converted PDF images

    Returns:

    Examples:
        original_size = (794, 1123)
        convert_size = (397, 561)
        detect_rect = [[100,150], [200,170]]
        original_rect = inverse_convert(detect_rect, convert_size, original_size)

    """
    original_rects = []
    for detect_rect in detect_rects:
        left_up_x = detect_rect[0][0]
        left_up_y = detect_rect[0][1]
        right_down_x = detect_rect[1][0]
        right_down_y = detect_rect[1][1]

        original_rect_left_up_x = original_size[0] / \
            convert_size[0] * left_up_x
        original_rect_left_up_y = original_size[1] / \
            convert_size[1] * left_up_y
        original_rect_right_down_x = original_size[0] / \
            convert_size[0] * right_down_x
        original_rect_right_down_y = original_size[1] / \
            convert_size[1] * right_down_y

        original_rect_left_up = [
            original_rect_left_up_x,
            original_rect_left_up_y]
        original_rect_right_down = [
            original_rect_right_down_x,
            original_rect_right_down_y]
        original_rect = [original_rect_left_up, original_rect_right_down]
        original_rects.append(original_rect)
    print(
        "Rect Area inversion completed, %d objects detected..." %
        len(original_rects))
    return original_rects


def cut_areas(original_rects, image_path):
    """
    Args:
        original_rects: Area position list, generated by inverse_convert()
        image_path: Path to original image

    Returns:

    """
    image = cv2.imread(image_path)
    count = 0
    for original_rect in original_rects:
        crop_img = image[original_rect[0][0]:original_rect[0]
                         [1], original_rect[1][0]:original_rect[1][1]]
        cv2.imwrite('./segResult/' + image_path.split('/')
                    [-1].split('.')[0] + str(count) + '.PNG', crop_img)
        count += 1


def show_seg_result(original, seg_result):
    cv2.imshow('name', seg_result)
    cv2.waitKey(0)

    for i in range(original.shape[0]):
        for j in range(original.shape[1]):
            if seg_result[i][j][2] == 20:
                original[i][j] = 0
    return original


def show_dir_seg_result(original_dir, seg_result_dir):
    seg_results_paths = os.listdir(seg_result_dir)
    for path in seg_results_paths:
        seg_path = os.path.join(seg_result_dir, path)
        original_path = os.path.join(original_dir, path)
        original = cv2.imread(original_path)
        seg_result = cv2.imread(seg_path)
        image = show_seg_result(original, seg_result)
        cv2.imwrite('./' + path, image)


def line_segmentation(img, flag=1):
    start_row = 0
    segments = []

    def determine_white_line(row):
        pixel_sum = 0
        for i in range(img.shape[1]):
            if img[row][i][0] >= 230 and img[row][i][1] >= 230 and img[row][i][2] >= 230:
                pass
            elif img[row][i][0] <= 130 or img[row][i][1] <= 130 or img[row][i][2] <= 130:
                return False
            else:
                pixel_sum += 1
            if pixel_sum / img.shape[1] > 0.03:
                return False
        return True
        
    for i in range(img.shape[0]):
        if determine_white_line(i) and flag == 1:
            continue
        elif determine_white_line(i) and flag == 0:
            flag = 1
            segments.append([start_row - 1, i + 1])
        elif not determine_white_line(i) and flag == 1:
            flag = 0
            start_row = i
        else:
            continue
    return segments


def log_line_segmentation(img, segments, output_dir):
    for index, segment in enumerate(segments):
        cv2.imwrite(output_dir + '/seg' + str(index) + '.png',
                    img[segment[0]: segment[1], :, :])




def get_segmentation(model):
    if not os.path.isfile(model):
        try:
            # download model from github
            os.system('wget -p ./models https://github.com/Alpha-Monocerotis/PDF_FigureTable_Extraction/releases/download/v1.0/resnet_segnet_1.0')
        except Exception as e:
            # print(e)
            print("Download is not completed, please try again later.")
    else:
        print("Loading model from downloaded weight...")
    try:
        predict_multiple(
            inp_dir='./images',
            out_dir='./output_seg',
            checkpoints_path='./models'
        )
        print("Segmentation Completed!")
    except Exception as e:
        print("Segmentation was not completed, there's something wrong with it, please check the Exception below!")
        print(e)

def get_segmented_image():
    paths = os.listdir("./output_seg")
    for path in paths:
        if 'png' in path or 'jpg' in path:
            seg_result = cv2.imread(os.path.join('./output_seg', path))
            original_image= cv2.imread(os.path.join('./images', path))
            assert seg_result.shape == original_image.shape, "Shape of segmentation result is not compatible with original image"
            generate_result(seg_result, original)
        else:
            print("File format Error: " + path)

def generate_result():
    index = 0
    # TODO(NikolaLiu@icloud.com): Adding function about extract each block and related image


def text_extraction():
    pass

def image_or_table_extraction():
    pass


def seg_image_to_blocks1(image):
    category = dict()
    category[1] = 'table'
    category[2] = 'image'
    def isedge(x, y):
        count_backgroud_pixel = 0
        for i in range(-1, 2):
            for j in range(-1 , 2):
                if 0 <= x + i < image.shape[0] and 0 <= y + j <image.shape[1] and image[x + i][y + j][2] == 20:
                    return True
        return False
    edge_x = dict()
    edge_y = dict()
    edge_x_set = set()
    edge_y_set = set()
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i][j][2] != 20 and isedge(i, j):
                if i in edge_x_set:
                    edge_x[i] += 1
                else:
                    edge_x[i] = 1
                    edge_x_set.add(i)

                if i in edge_y_set:
                    edge_y[i] += 1
                else:
                    edge_y[i] = 1
                    edge_y_set.add(i)
    return edge_x, edge_y

def get_all_seg_areas(images):
    # TODO(NikolaLiu@icloud.com): As for a segmentation result, we can scan it to get each areas.
    pass

def process_area(images, x, y):
    # TODO(NikolaLiu@icloud.com): Scab column and row respectively, then get the split possibility. You should also consider the situation that hollows in an area could also be the sign of splitting. 
    pass


if __name__ == "__main__":
    edge_x, edge_y = seg_image_to_blocks(cv2.imread('path/to/image'))
    # print(edge_x.keys())
    # print(edge_y.keys())
    plt.figure()
    plt.plot(list(edge_x.values()))
    plt.savefig('edge_x.jpg')
    plt.figure()
    plt.plot(list(edge_y.values()))
    plt.savefig('edge_y.jpg')
    










