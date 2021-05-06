import os
import shutil
import time

import SimpleITK as sitk
import cv2
import numpy as np
import pydicom


def save_dcm(inputpath, pre_data, outpath, rows, columns, samples='examples.dcm'):
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
    dcm.data_element('ImagePositionPatient').value = dataset.data_element('ImagePositionPatient').value
    dcm.data_element('ImageOrientationPatient').value = dataset.data_element('ImageOrientationPatient').value
    dcm.data_element('PixelSpacing').value = dataset.data_element('PixelSpacing').value

    # 将数据写入到 dicom 文件中
    rescale_intercept = -dcm.RescaleIntercept

    pre_data = np.uint16(pre_data + rescale_intercept)
    dcm.pixel_array.data = pre_data
    dcm.PixelData = dcm.pixel_array.tobytes()

    # 保存 dicom 数据
    dcm.save_as(outpath)


def dcm2nii(path_read, path_save):
    # GetGDCMSeriesIDs读取序列号相同的dcm文件
    series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(path_read)
    # GetGDCMSeriesFileNames读取序列号相同dcm文件的路径，series[0]代表第一个序列号对应的文件
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(path_read, series_id[0])
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    image3d = series_reader.Execute()
    sitk.WriteImage(image3d, path_save)


def singlethread(path, paths, nii_out_path):
    for sig in paths:
        t0 = time.time()
        dicom_path = os.path.join(path, sig, 'data')
        bmp_path = os.path.join(path, sig, 'BMP')
        out_path = os.path.join(path, sig, 'dicom')
        nii_out_dir = os.path.join(nii_out_path, sig)

        if not os.path.exists(out_path):
            os.makedirs(out_path)

        if not os.path.exists(nii_out_dir):
            os.makedirs(nii_out_dir)

        save_nii_path = os.path.join(nii_out_dir, 'IAS.nii.gz')

        dicom_files = os.listdir(dicom_path)
        bmp_files = os.listdir(bmp_path)

        for index in range(len(bmp_files)):
            dicom = os.path.join(dicom_path, dicom_files[index])

            bmp = cv2.imread(os.path.join(bmp_path, bmp_files[index]), cv2.IMREAD_GRAYSCALE)
            out_file_path = os.path.join(out_path, dicom_files[index])
            save_dcm(dicom, pre_data=bmp, outpath=out_file_path, rows=512, columns=512, samples='examples.dcm')

        origin_nii_path = os.path.join(nii_out_dir, 'origin.nii.gz')
        if not os.path.exists(origin_nii_path):
            dcm2nii(path_read=dicom_path, path_save=origin_nii_path)

        dcm2nii(path_read=out_path, path_save=save_nii_path)
        shutil.rmtree(out_path)
        t1 = time.time()
        print("complete " + dicom_path)


if __name__ == '__main__':
    t0 = time.time()
    path = r'I:\NII\new'
    nii_out_path = r'I:\NII\2021_04_28'
    paths = os.listdir(path)

    singlethread(path, paths, nii_out_path)

    t1 = time.time()
  