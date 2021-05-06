import os
import SimpleITK as sitk
import numpy as np
import pydicom
from skimage import measure


def _read_mask_nii(filepath):
    # 读取医学图像数据
    image = sitk.ReadImage(filepath)
    data = sitk.GetArrayFromImage(image)
    # data = np.transpose(data, [0, 2, 1])
    data = np.array(data, dtype='int16')
    return data


def _read__nii(filepath):
    # 读取医学图像数据
    image = sitk.ReadImage(filepath)
    data = sitk.GetArrayFromImage(image)
    # data = np.transpose(data, [0, 2, 1])
    data = np.array(data, dtype='int16')

    return data


def save_dcm(inputpath, pre_data, outpath, rows, columns, samples='examples.dcm', xmin=0, ymin=0):
    # 通过桥接的方式进行dicom文件的保存
    dcm = pydicom.dcmread(samples, force=True)

    # 判断是否是512*512的， 如果不是512*512的
    if rows < 512 or columns < 512:
        data = dcm.pixel_array
        datanew = data[0:rows, 0:columns]
        dcm.PixelData = datanew.tobytes()
        dcm.Rows, dcm.Columns = datanew.shape

    dataset = pydicom.dcmread(inputpath, force=True)  # 原始的 dicom文件

    # # 添加一些必要的tag值

    dcm.data_element('PatientName').value = dataset.data_element('PatientName').value
    dcm.data_element('PatientBirthDate').value = dataset.data_element('PatientBirthDate').value
    dcm.data_element('SliceThickness').value = dataset.data_element('SliceThickness').value
    dcm.data_element('SOPClassUID').value = dataset.data_element('SOPClassUID').value
    dcm.data_element('SOPInstanceUID').value = dataset.data_element('SOPInstanceUID').value
    dcm.data_element('SliceLocation').value = dataset.data_element('SliceLocation').value
    dcm.data_element('PatientPosition').value = dataset.data_element('PatientPosition').value
    dcm.data_element('InstanceNumber').value = dataset.data_element('InstanceNumber').value
    dcm.data_element('SeriesNumber').value = dataset.data_element('SeriesNumber').value
    dcm.data_element('StudyID').value = dataset.data_element('StudyID').value
    dcm.data_element('ImageOrientationPatient').value = dataset.data_element('ImageOrientationPatient').value
    dcm.data_element('PixelSpacing').value = dataset.data_element('PixelSpacing').value
    # dcm.data_element('ImagePositionPatient').value = dataset.data_element('ImagePositionPatient').value

    x_y_z = dataset.data_element('ImagePositionPatient').value
    space = dataset.data_element('PixelSpacing').value
    x = float(x_y_z[0])
    y = float(x_y_z[1])
    spacex = float(space[0])
    spacey = float(space[1])

    x = x + xmin * spacex
    y = y + ymin * spacey

    # dcm.data_element('ImagePositionPatient').value = dataset.data_element('ImagePositionPatient').value

    dcm.data_element('ImagePositionPatient').value = [str(x), str(y), x_y_z[2]]

    # 将数据写入到 dicom 文件中
    rescale_intercept = -dcm.RescaleIntercept

    pre_data = np.uint16(pre_data + rescale_intercept)
    dcm.pixel_array.data = pre_data
    dcm.PixelData = dcm.pixel_array.tobytes()

    # 保存 dicom 数据
    dcm.save_as(outpath)


# 裁剪dicom roi 并与原始数据保持同一坐标系
if __name__ == '__main__':

    all_data_path = r'F:\NII\data'
    all_dicoms_path = r'I:\origin_dicom'
    out_dir = r'F:\NII\IAS_SEGMENTATION\out'
    dirs = sorted(os.listdir(all_data_path))
    dirs = dirs[0:111]

    for dir in dirs:

        out_path = os.path.join(out_dir, dir)

        os.mkdir(out_path)

        data_path = os.path.join(all_data_path, dir, 'origin.nii.gz')
        dicom_path = os.path.join(all_dicoms_path, dir, 'data')
        dicoms = sorted(os.listdir(dicom_path))

        image_data = _read__nii(data_path)

        mask_path = os.path.join(all_data_path, dir, 'IAS.nii.gz')

        mask_data = _read_mask_nii(mask_path)

        mask_data[mask_data > 0] = 1
        mask_data[mask_data != 1] = 0
        # mask_data = mask_data * 255

        labels, num = measure.label(mask_data, connectivity=1, return_num=True)
        region = measure.regionprops(labels)
        t = 1
        for i in region:
            bbox = i.bbox

            zmin = min(bbox[3], bbox[0])
            ymin = min(bbox[4], bbox[1])
            xmin = min(bbox[5], bbox[2])

            area = i.area
            if area > 10:

                os.mkdir(os.path.join(out_path, str(t)))

                s_out_dir = os.path.join(out_path, str(t))

                os.mkdir(os.path.join(s_out_dir, 'data'))
                os.mkdir(os.path.join(s_out_dir, 'label'))

                oreal_path = os.path.join(s_out_dir, 'data')
                label_path = os.path.join(s_out_dir, 'label')

                t += 1
                shape = image_data.shape
                zmax, xmax, ymax = shape[0], shape[1], shape[2]

                x1, x2 = max(0, xmin - 48), min(xmin - 48 + 96, xmax)
                y1, y2 = max(0, ymin - 48), min(ymin - 48 + 96, ymax)
                z1, z2 = max(0, zmin - 48), min(zmin - 48 + 96, zmax)

                out = image_data[z1:z2, y1:y2, x1:x2]
                label = mask_data[z1:z2, y1:y2, x1:x2]

                print(dir)
                print(out.shape)

                row = out.shape[1]
                col = out.shape[2]
                i = 1
                z = max(0, zmin - 48)

                for file, lab in zip(out, label):
                    dic_path = os.path.join(dicom_path, dicoms[z])

                    out_file_path = os.path.join(oreal_path, str(i) + '.dcm')
                    out_label_path = os.path.join(label_path, str(i) + '.dcm')

                    save_dcm(dic_path, file, outpath=out_file_path, rows=row, columns=col, xmin=x1, ymin=y1)
                    save_dcm(dic_path, lab, outpath=out_label_path, rows=row, columns=col, xmin=x1, ymin=y1)

                    i += 1
                    z += 1
