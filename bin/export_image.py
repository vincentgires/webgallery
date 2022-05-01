#!/usr/bin/env python

import sys
import os
import shutil
import subprocess

filepath = sys.argv[-1]
dirname, filename = os.path.split(filepath)

image_formats = {
    'thumbnails': '300x300',
    'highres': '2048x2048'}

def resize_file(filepath, size, outputdir):
    folderpath, filename = os.path.split(filepath)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputpath = os.path.join(outputdir, filename)
    command = [
        'magick', 'convert',
        filepath,
        '-colorspace', 'rgb',
        '-resize', size,
        '-colorspace', 'srgb',
        outputpath]
    print(command)
    subprocess.call(command)
    return outputpath


# Convert image to different formats
for image_format, size in image_formats.items():
    outputdir = os.path.join(dirname, image_format)
    os.makedirs(outputdir, exist_ok=True)
    resize_file(filepath, size, outputdir)

# Move files to fullres and json
fullres_dir = os.path.join(dirname, 'fullres')
os.makedirs(fullres_dir, exist_ok=True)
shutil.move(filepath, os.path.join(fullres_dir, filename))
json_path = filepath + '.json'
if os.path.exists(json_path):
    json_dir = os.path.join(dirname, 'json')
    os.makedirs(json_dir, exist_ok=True)
    shutil.move(json_path, os.path.join(json_dir, filename + '.json'))
