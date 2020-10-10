#!/usr/bin/env python

import sys
import os
import subprocess

arg_size = sys.argv[-3]
arg_input = sys.argv[-2]
arg_output = sys.argv[-1]

resolution = {
    'thumbnail': '300x300',
    'highres': '2048x2048'}
if arg_size not in resolution:
    size = arg_size
else:
    size = resolution[arg_size]


def resize_file(filepath, outputdir):
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


images = [
    os.path.join(arg_input, i) for i in sorted(os.listdir(arg_input))
    if i.endswith('.jpg')]
for filepath in images:
    resize_file(filepath, arg_output)
