#!/usr/bin/env python

import sys
import os
import subprocess

arg_output = sys.argv[-1]
arg_input = sys.argv[-2]


def resize_file(filepath, outputdir):
    folderpath, filename = os.path.split(filepath)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputpath = os.path.join(outputdir, filename)
    command = [
        'magick', 'convert',
        filepath,
        '-colorspace', 'rgb',
        '-resize', '300x300',
        '-colorspace', 'srgb',
        outputpath]
    print(command)
    subprocess.call(command)
    return outputpath


images = [os.path.join(arg_input, i) for i in sorted(os.listdir(arg_input))]
for filepath in images:
    resize_file(filepath, arg_output)
