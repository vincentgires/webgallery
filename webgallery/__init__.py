import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import json
import logging
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.add_url_rule(
    ('/media' if os.environ.get('GALLERY_PATH')
     else app.static_url_path + '/media'),
    endpoint='media')


def get_media_folderpath():
    folderpath = os.environ.get('GALLERY_PATH', app.static_folder)
    folderpath = os.path.join(folderpath, 'media')
    return folderpath


def get_json_files(category):
    path = os.path.join(get_media_folderpath(), category)
    return [i for i in sorted(os.listdir(path)) if i.endswith('.json')]


def get_photos_from_search(tags=None, date=None):
    tags_images = []
    date_images = []
    photos_path = os.path.join(get_media_folderpath(), 'photos')
    for j in get_json_files('photos'):
        with open(os.path.join(photos_path, j)) as f:
            data = json.load(f)
        # json root name should be the image filename
        image = os.path.splitext(j)[0]
        if tags is not None:
            if all(x in data['tags'] for x in tags):
                tags_images.append(image)
        if date is not None:
            dt = datetime.strptime(
                data['exifs']['datetime_taken'], '%Y:%m:%d %H:%M:%S')
            if date == dt.strftime('%Y-%m-%d'):
                date_images.append(image)
    if tags is not None:
        images = tags_images
    elif date is not None:
        images = date_images
    if tags is not None and date is not None:
        # Return only images that matches all criteria
        images = set.intersection(*map(set, [tags_images, date_images]))
    return images


# TODO
def generate_gallery_zip():
    pass


# TODO
def delete_media():
    """Delete all related media files: highres, thumbnail, tags, etc."""
    pass


@app.route('/')
def index():
    collections_path = os.path.join(get_media_folderpath(), 'collections')
    collections = []
    for i in get_json_files('collections'):
        with open(os.path.join(collections_path, i)) as f:
            data = json.load(f)
            if data.get('private', False):
                continue
            image = os.path.splitext(i)[0]
            collections.append(image)
    return render_template('index.html', collections=collections)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        args = {}
        tags = request.form.get('tags')
        date = request.form.get('date')
        if tags:
            tags = [t.lstrip() for t in tags.split(',')]
            args['tag'] = tags
        if date:
            args['date'] = date
        return redirect(url_for('search', **args))

    elif request.method == 'GET':
        # adress.net/search?tag=value&tag=value
        tags = request.args.getlist('tag')
        tags = [t.lstrip() for t in tags]
        date = request.args.get('date')
        images = get_photos_from_search(tags, date)
        return render_template('search.html', images=images)


@app.route('/collections/<name>')
def show_collection(name):
    collections_path = os.path.join(get_media_folderpath(), 'collections')
    with open(os.path.join(collections_path, name + '.json')) as f:
        data = json.load(f)
        images = data.get('photos') or []
        videos = data.get('videos') or []
    return render_template(
        'collection.html', collection_name=name, images=images, videos=videos)


@app.route('/add', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        # TODO
        # collection_name = request.form['collection_name']
        # if not collection_name:
        #     return redirect(request.url)
        # folderpath = os.path.join(
        #     get_collections_folderpath(), collection_name, HIGHRES_FOLDERNAME)
        # if not os.path.exists(folderpath):
        #     os.makedirs(folderpath)
        # for file in files:
        #     if not file.filename:
        #         flash('No selected file')
        #         return redirect(request.url)
        #     filename = secure_filename(file.filename)
        #     filepath = os.path.join(folderpath, filename)
        #     file.save(filepath)
        #     # TODO: generate media thumbnail
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
