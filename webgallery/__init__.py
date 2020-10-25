import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import json
import logging
from datetime import datetime
import sqlite3
from jinja2 import Template

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


def get_database_path():
    if os.environ.get('GALLERY_PATH') is not None:
        return os.path.join(os.environ.get('GALLERY_PATH'), 'database.db')
    else:
        return 'database.db'


def find_images_from_json(tags=None, date=None, to_date=None):
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
            # skip  %H:%M:%S to be able to compare better with selected
            # date and to_date that does not have it and risk to make errors
            ymd_date = data['exifs']['datetime_taken'].split(' ')[0]
            dt = datetime.strptime(ymd_date, '%Y:%m:%d')
            if to_date is not None:
                dt_date = datetime.strptime(date, '%Y-%m-%d')
                dt_to_date = datetime.strptime(to_date, '%Y-%m-%d')
                if dt_date <= dt <= dt_to_date:
                    date_images.append(image)
            elif date == dt.strftime('%Y-%m-%d'):
                date_images.append(image)
    if tags is not None:
        images = tags_images
    elif date is not None:
        images = date_images
    if tags is not None and date is not None:
        # Return only images that matches all criteria
        images = sorted(
            set.intersection(*map(set, [tags_images, date_images])))
    return images


def find_images_from_database(tags=None, date=None, to_date=None):
    tags = tags or []
    connexion = sqlite3.connect(get_database_path())
    cursor = connexion.cursor()
    query = '''select filename, strftime('%Y-%m-%d', date)  from images
{% for t in tags %}
    inner join tagged_images as image_tag_{{loop.index}} on image_tag_{{loop.index}}.image_filename = images.filename
    inner join tags as tag_{{loop.index}} on tag_{{loop.index}}.id = image_tag_{{loop.index}}.tag_id
{% endfor %}

{% if tags %}
    where {% for t in tags %}tag_{{loop.index}}.name = ?{{" and " if not loop.last}}{% endfor %}
{% endif %}

{% if date and not tags %}
    where
{% elif tags and date %}
    and
{% endif %}
{% if date %}
    date >= '{{date}}' and date <= '{% if to_date %}{{to_date}}{% else %}{{date}}{% endif %} 23:59:59.999'
{% endif %}

order by images.date'''
    query = Template(query).render(tags=tags, date=date, to_date=to_date)
    cursor.execute(query, tags)
    result = [r[0] for r in cursor.fetchall()]
    connexion.close()
    return result


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
        to_date = request.form.get('to_date')
        if tags:
            tags = [t.lstrip() for t in tags.split(',')]
            args['tag'] = tags
        if date:
            args['date'] = date
        if to_date:
            args['to_date'] = to_date
        return redirect(url_for('search', **args))

    elif request.method == 'GET':
        # adress.net/search?tag=value&tag=value
        tags = request.args.getlist('tag')
        tags = [t.lstrip() for t in tags]
        date = request.args.get('date')
        to_date = request.args.get('to_date')
        # images = find_images_from_json(tags, date, to_date)
        images = find_images_from_database(tags, date, to_date)
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


def create_or_update_database_from_json():
    # TODO: remove from database if json does not exist anymore
    connexion = sqlite3.connect(get_database_path())
    cursor = connexion.cursor()
    cursor.execute(
        'create table if not exists images(filename text unique, date text)')
    cursor.execute(
        'create table if not exists '
        'tags(id integer primary key autoincrement unique, name text unique)')
    cursor.execute(
        'create table if not exists '
        'tagged_images(image_filename text, tag_id text)')

    photos_path = os.path.join(get_media_folderpath(), 'photos')
    for j in get_json_files('photos'):
        with open(os.path.join(photos_path, j)) as f:
            data = json.load(f)
        filename = os.path.splitext(j)[0]
        date = data['exifs']['datetime_taken']
        # convert date to interpretable format for sqlite
        dt = datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        date = dt.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('select * from images where filename = ?', (filename,))
        image_exist = cursor.fetchone()
        if image_exist is None:
            cursor.execute(
                'insert into images(filename, date) values (?, ?)',
                (filename, date))

        for tag in data['tags']:
            cursor.execute('select * from tags where name = ?', (tag,))
            result = cursor.fetchone()
            if result is None:
                cursor.execute('insert into tags(name) values (?)', (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = result[0]

            # Don't add new tag/image association if they are already linked
            cursor.execute(
                'select * from tagged_images where '
                'image_filename = ? and tag_id = ?', (filename, tag_id))
            if cursor.fetchone() is None:
                cursor.execute(
                    'insert into tagged_images(image_filename, tag_id) '
                    'values (?, ?)', (filename, tag_id))

    connexion.commit()
    connexion.close()


if __name__ == '__main__':
    # create_or_update_database_from_json()
    app.run(debug=True)
