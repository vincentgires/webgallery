#!/usr/bin/env python

import os
from flask import Flask, render_template, flash, request, redirect
from werkzeug.utils import secure_filename
import subprocess
import json
import logging


SUPPORTED_IMAGE_EXT = ['.jpg', '.jpeg', '.png', '.gif']
HIGHRES_FOLDERNAME = 'highres'
THUMBNAIL_FOLDERNAME = 'thumbnail'
GALLERY_IMG_WIDTH = 900
GALLERY_IMG_HEIGHT = 150
COLLECTION_IMG_FILENAME = 'collection.jpg'
COLLECTION_CONFIG_FILE = 'collection.json'

app = Flask(__name__, template_folder='templates')
os.environ.get('GALLERY_PATH')
app.add_url_rule(
    ('/medias' if os.environ.get('GALLERY_PATH')
     else app.static_url_path + '/medias'),
    endpoint='medias')


def get_collections_folderpath():
    folderpath = os.environ.get('GALLERY_PATH', app.static_folder)
    folderpath = os.path.join(folderpath, 'medias', 'collections')
    return folderpath


def get_collection_folders():
    folderpath = get_collections_folderpath()
    galleries = [
        i for i in os.listdir(folderpath)
        if os.path.isdir(os.path.join(folderpath, i))]
    for i in galleries:
        config_file = os.path.join(folderpath, i, COLLECTION_CONFIG_FILE)
        is_config = os.path.exists(config_file)
        if is_config:
            with open(config_file) as f:
                config = json.load(f)
                if config.get('private'):
                    galleries.remove(i)
    return galleries


def get_images(foldername, imagetype, fullpath=False):
    folderpath = os.path.join(
        get_collections_folderpath(),
        foldername,
        imagetype)
    if os.path.isdir(folderpath):
        images = [
            i for i in sorted(os.listdir(folderpath))
            if os.path.splitext(i)[1].lower() in SUPPORTED_IMAGE_EXT]
        if fullpath:
            return [os.path.join(folderpath, i) for i in images]
        return images


def generate_media_thumbail(filepath):
    folderpath, filename = os.path.split(filepath)
    outputpath = os.path.normpath(os.path.join(
        folderpath, os.pardir, THUMBNAIL_FOLDERNAME))
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    outputpath = os.path.join(outputpath, filename)
    command = [
        'magick', 'convert',
        filepath,
        '-colorspace', 'rgb',
        '-resize', '300x300',
        '-colorspace', 'srgb',
        outputpath]
    subprocess.call(command)
    return outputpath


def generate_all_thumbails(foldername):
    images = get_images(
        foldername=foldername, imagetype=HIGHRES_FOLDERNAME, fullpath=True)
    for filepath in images:
        logging.info('thumbnail: {}'.format(filepath))
        generate_media_thumbail(filepath)


def generate_gallery_thumbail(foldername):
    inputs = get_images(foldername, THUMBNAIL_FOLDERNAME, fullpath=True)
    # exclude gif to avoid each images to be in the gallery thumbnail
    inputs = [i for i in inputs if os.path.splitext(i)[1] != '.gif']
    output = os.path.join(
        get_collections_folderpath(),
        foldername,
        COLLECTION_IMG_FILENAME)
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


# TODO
def generate_gallery_zip():
    pass


# TODO
def delete_media():
    """Delete all related media files: highres, thumbnail, tags, etc."""
    pass


@app.route('/')
def index():
    return render_template('index.html', collections=get_collection_folders())


# TODO
@app.route('/tags')
def show_tags():
    return '''
        <!doctype html>
        <title>Tags</title>
        <h1>Tags</h1>'''


@app.route('/collections/<name>')
def show_collection(name):
    images = (
        get_images(foldername=name, imagetype=THUMBNAIL_FOLDERNAME)
        or [])
    return render_template(
        'collection.html',
        collection_name=name,
        images=images)


@app.route('/add', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        collection_name = request.form['collection_name']
        if not collection_name:
            return redirect(request.url)
        folderpath = os.path.join(
            get_collections_folderpath(), collection_name, HIGHRES_FOLDERNAME)
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        for file in files:
            if not file.filename:
                flash('No selected file')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            filepath = os.path.join(folderpath, filename)
            file.save(filepath)
            generate_media_thumbail(filepath)
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
