import os
import uuid
import datetime
import random

import requests


from flask import render_template, redirect, url_for, flash, request, Markup
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename

from site_package import app, db, parsing
from site_package.forms import CategoryForm, AnimeImportForm
from site_package.models import Anime, AnimeCategory


@app.route('/new_home', methods=['GET', 'POST'])
def new_home():
    pined_categories = ['Comedy', 'Adventure', 'Drama']
    categories = list(AnimeCategory.query.filter(AnimeCategory.animes.any(), AnimeCategory.name.in_(pined_categories)))
    categories += list(AnimeCategory.query.filter(AnimeCategory.animes.any(), ~AnimeCategory.name.in_(pined_categories)).order_by(func.random()).limit(5))
    category_animes = []
    
    for category in categories:
        animes = list(Anime.query.filter(Anime.categories.any(AnimeCategory.id==category.id)).order_by(func.random()).limit(8))

        if len(animes) < 8:
            animes = random.choices(animes, k=8)

        category_animes.append([category, animes])

    context = {
        'title': "Index page",
        'category_animes': category_animes,
    }

    return render_template('new/home.html', **context)


@app.route('/new_categories_list', methods=['GET'])
def new_categories_list():
    context = {
        'title': 'Categories list',
        'categories': AnimeCategory.query.all(),
    }

    return render_template('new/categories_list.html', **context)


@app.route('/new_category_change/<int:cat_id>', methods=['GET', 'POST'])
def new_category_change(cat_id):
    category = AnimeCategory.query.get(cat_id)
    form = CategoryForm(name=category.name, description=category.description)

    context = {
        'title': f'Change {category.name} Category',
        'category': category,
        'form': form,
    }

    if request.method == "POST" and form.validate_on_submit():
        if form.name.data and form.name.data != category.name:
            category.name = form.name.data
        if form.description.data and form.description.data != category.description:
            category.description = form.description.data

        db.session.commit()
        flash(f"Changes have been saved", category="success")

        return redirect(request.url)

    return render_template('new/category_change.html', **context)


@app.route('/new_import_anime_from_mal', methods=['GET', 'POST'])
def new_import_anime_from_mal():
    form = AnimeImportForm(grade=0)

    context = {
        'title': f'Import anime from MAL',
        'form': form,
    }

    if request.method == "POST" and form.validate_on_submit():
        anime_url = request.form['url']
        data = parsing.parse_mal_anime_page(anime_url)

        release = datetime.datetime.strptime(data['release'], '%b %d %Y').date()
        grade = request.form['grade']

        # Main info
        anime = Anime(
            name=data['name'],
            alternative_name=data['alternative_name'],
            release=release,
            grade=grade,
            description=data['description']
        )
        
        # Add categories
        for category_name in data['categories']:
            if category:= AnimeCategory.query.filter_by(name=category_name).first():
                pass
            else:
                category = AnimeCategory(name=category_name)
                db.session.add(category)
                db.session.commit()

            anime.categories.append(category)

        # Image upload
        try:
            img_data = requests.get(data['img_url'], verify=False, timeout=5).content
            filename = str(uuid.uuid1()) + '_' + secure_filename(data['img_url'].split('/')[-1])
            folder_release = release.strftime('%Y/%m')
            img_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release)
            img_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release, filename)

            if not os.path.exists(img_folder):
                os.makedirs(img_folder)

            with open(img_path, 'wb') as handler:
                handler.write(img_data)

            anime.img = os.path.join(app.config['UPLOAD_FOLDER'][1:], folder_release, filename)
        except requests.exceptions.ConnectionError:
            flash('Image not available', category='danger')

        # Anime commit
        db.session.add(anime)
        db.session.commit()

        flash(Markup(f"Anime {anime.name} has been imported! <a href='{ url_for('change_anime_page', anime_id=anime.id) }'>Link here</a>"), category="success")

    return render_template('new/import_anime.html', **context)
