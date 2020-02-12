#!/usr/bin/env python

import sys
import os
import subprocess

GALLERY_IMG_WIDTH = 900
GALLERY_IMG_HEIGHT = 150
arg_input = sys.argv[-1]


def generate_gallery_thumbail(inputs, output):
    # exclude gif to avoid each images to be in the gallery thumbnail
    inputs = [i for i in inputs if os.path.splitext(i)[1] != '.gif']
    img_width = GALLERY_IMG_WIDTH / len(inputs)
    command = ['magick', 'montage']
    command.extend(inputs)
    command.extend([
        '-colorspace', 'rgb',
        '-resize', 'x{h}'.format(h=GALLERY_IMG_HEIGHT),
        '-crop', '{w}x{h}+0+0'.format(w=img_width, h=GALLERY_IMG_HEIGHT),
        '-mode', 'concatenate',
        '-tile', 'x1',
        '-colorspace', 'srgb',
        os.path.join(output, 'collection.jpg')])
    subprocess.call(command)


images = [os.path.join(arg_input, i) for i in sorted(os.listdir(arg_input))]
output, _ = os.path.split(arg_input)
generate_gallery_thumbail(images, output)
