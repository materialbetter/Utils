import os
import shutil
import xml.etree.ElementTree as ET

path = r'H:\label\2\label'

files = sorted(os.listdir(path))
for file in files:
    file_path = os.path.join(path,file)
    doc = ET.parse(file_path)
    root = doc.getroot()
    objs = root.findall('object')
    for obj in objs:
        name = obj.find('name')
        name.text = '1'
    doc.write(file_path)
