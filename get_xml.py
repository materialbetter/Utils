import os
import cv2 as cv
import numpy as np
from os import getcwd

from lxml.etree import Element, SubElement, tostring, ElementTree
from lxml.etree import ElementTree as ET


# from xml.etree import ElementTree as ET


def create_object(root, xi, yi, xa, ya, obj_name):  # 参数依次，树根，xmin，ymin，xmax，ymax
    # 创建一级分支object
    _object = SubElement(root, 'object')
    # 创建二级分支
    name = SubElement(_object, 'name')
    # print(obj_name)
    name.text = str(obj_name)
    pose = SubElement(_object, 'pose')
    pose.text = 'Unspecified'
    truncated = SubElement(_object, 'truncated')
    truncated.text = '0'
    difficult = SubElement(_object, 'difficult')
    difficult.text = '0'
    # 创建bndbox
    bndbox = SubElement(_object, 'bndbox')
    xmin = SubElement(bndbox, 'xmin')
    xmin.text = '%s' % xi
    ymin = SubElement(bndbox, 'ymin')
    ymin.text = '%s' % yi
    xmax = SubElement(bndbox, 'xmax')
    xmax.text = '%s' % xa
    ymax = SubElement(bndbox, 'ymax')
    ymax.text = '%s' % ya

    return root
    # return tostring(root, pretty_print=True)  # 格式化显示，该换行的换行


def create_tree(image_name, h, w):
    # 创建树根annotation
    annotation = Element('annotation')
    # 创建一级分支folder
    folder = SubElement(annotation, 'folder')
    # 添加folder标签内容
    folder.text = '1'

    # 创建一级分支filename
    filename = SubElement(annotation, 'filename')
    filename.text = image_name

    # 创建一级分支path
    path = SubElement(annotation, 'path')

    path.text = str(1) + '\\' + str(image_name)

    # 创建一级分支source
    source = SubElement(annotation, 'source')
    # 创建source下的二级分支database
    database = SubElement(source, 'database')
    database.text = 'Unknown'

    # 创建一级分支size
    size = SubElement(annotation, 'size')
    # 创建size下的二级分支图像的宽、高及depth
    width = SubElement(size, 'width')
    width.text = str(w)
    height = SubElement(size, 'height')
    height.text = str(h)
    depth = SubElement(size, 'depth')
    depth.text = '3'

    # 创建一级分支segmented
    segmented = SubElement(annotation, 'segmented')
    segmented.text = '0'

    return annotation


def read_image(path):
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)

    guangban_gray_image = image[:]
    guangban_gray_image[guangban_gray_image < 30] = 0
    guangban_gray_image[guangban_gray_image >= 30] = 1
    guangban_gray_image = guangban_gray_image * 255

    index = np.where(guangban_gray_image > 0)
    x_min = np.min(index[1])
    x_max = np.max(index[1])
    y_min = np.min(index[0])
    y_max = np.max(index[0])

    (h, w) = guangban_gray_image.shape

    return [x_min, x_max, y_min, y_max, h, w]


if __name__ == '__main__':


    guangban_path = '/media/hy/data/HY/Pupils/pic/guangban/7'
    tongkong_path = '/media/hy/data/HY/Pupils/pic/tongkong/7'
    o_path = '/media/hy/data/HY/Pupils/pic/guangban/xml/7_xml'

    if not os.path.exists(o_path):
        os.mkdir(o_path)
    imgs = sorted(os.listdir(guangban_path))
    for img in imgs:
        guangban_img_path = os.path.join(guangban_path, img)
        tongkong_img_path = os.path.join(tongkong_path, img)

        guangban = read_image(guangban_img_path)
        tongkong = read_image(tongkong_img_path)

        annotation = create_tree(os.path.basename(guangban_img_path), guangban[4], guangban[5])

        annotation1 = create_object(annotation, guangban[0], guangban[2], guangban[1] + 1, guangban[3] + 1, 0)
        annotation2 = create_object(annotation1, tongkong[0]+1, tongkong[2]+1, tongkong[1] + 1, tongkong[3] + 1, 1)

        xml = tostring(annotation2, pretty_print=True)

        name = os.path.basename(guangban_img_path).split('.')[0]
        save_path = os.path.join(o_path, name + '.xml')

        file_object = open(save_path, 'wb')
        file_object.write(xml)
        file_object.close()
