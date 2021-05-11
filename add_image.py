import os
import copy
import cv2
import numpy as np
import SimpleITK as sitk

image_path = r'F:\pc\vessel\frist_fantaiping\origin'
mask_path = r'F:\pc\vessel\frist_fantaiping\mask'
save_path = r'F:\pc\vessel\frist_fantaiping\add_mask'
for img, mask in zip(sorted(os.listdir(image_path)), sorted(os.listdir(mask_path))):
    img_path = os.path.join(image_path, img)
    mas_path = os.path.join(mask_path, mask)

    image_data = sitk.ReadImage(img_path)
    image_array = np.squeeze(sitk.GetArrayFromImage(image_data))

    mask_data = cv2.imread(mas_path)
    mask_data = np.array(mask_data, dtype='uint8')

    mask_data = np.transpose(mask_data, (2, 0, 1))

    g_mask = mask_data[0]
    b_mask = mask_data[1]
    r_mask = mask_data[2]

    image_array[image_array > 250] = 250
    image_array[image_array < -200] = -200
    image_array = ((image_array + 200) / 450) * 255
    image_array = np.array(image_array, dtype='uint8')
    #
    #
    out_image = np.zeros((3, 512, 512))
    # gbr
    image_arrayr = copy.deepcopy(image_array)
    image_arrayg = copy.deepcopy(image_array)
    image_arrayb = copy.deepcopy(image_array)

    for i in range(0, 512):
        for j in range(0, 512):
            if g_mask[i][j] == 254:
                image_arrayg[i][j] = 255
                image_arrayb[i][j] = 100

    for i in range(0, 512):
        for j in range(0, 512):
            if b_mask[i][j] == 254:
                image_arrayb[i][j] = 255
                image_arrayr[i][j] = 127

    out_image[0] = image_arrayg
    out_image[1] = image_arrayb
    out_image[2] = image_arrayr

    out_image = np.transpose(out_image, (1, 2, 0))

    name = img.split('.')[0]

    cv2.imwrite(os.path.join(save_path, name + '.bmp'), out_image)
