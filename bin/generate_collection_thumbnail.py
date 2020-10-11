#!/usr/bin/env python

import sys
import os
import subprocess
import json

GALLERY_IMG_WIDTH = 900
GALLERY_IMG_HEIGHT = 150

arg_json = sys.argv[-3]
arg_images_folder = sys.argv[-2]
arg_output_image = sys.argv[-1]


def generate_collection_thumbail(inputs, output):
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
        output])
    subprocess.call(command)


with open(arg_json) as f:
    data = json.load(f)

images = [os.path.join(arg_images_folder, i) for i in data['photos']]
generate_collection_thumbail(images, arg_output_image)
