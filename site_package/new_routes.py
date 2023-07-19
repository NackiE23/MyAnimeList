import os
import uuid
import datetime
import random

import requests


from flask import render_template, redirect, url_for, flash, request, Markup
from flask_login import current_user
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename

from site_package import app, db, parsing
from site_package.forms import CategoryForm
from site_package.models import Anime, AnimeCategory, Comment, RelationCategory, RelatedAnime


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


@app.route('/new_search_anime', methods=['GET']) 
def new_search_anime():
    page = int(request.args.get('page', 1))
    per_page = 50

    animes = Anime.query.filter(or_(Anime.name.like('%' + request.args.get('name', '') + '%'), 
                                    Anime.alternative_name.like('%' + request.args.get('name', '') + '%')))
    if request.args.get('sort', '') == "grade_up":
        animes = animes.order_by(Anime.grade.asc())
    else:
        animes = animes.order_by(Anime.grade.desc())
    animes = animes.paginate(page=page, per_page=per_page, error_out=False)

    context = {
        'title': "Search",
        'animes': animes,
        'request_args': {k:v for k, v in request.args.items() if k != "page"}
    }

    return render_template('new/search_anime.html', **context)


@app.route('/new_top_list', methods=['GET'])
def new_top_list():
    page = int(request.args.get('page', 1))
    per_page = 50

    context = {
        'title': "Top List",
        'animes': Anime.query.order_by(Anime.grade.desc()).paginate(page=page, per_page=per_page, error_out=False),
        'request_args': {k:v for k, v in request.args.items() if k != "page"}
    }

    return render_template('new/top_list.html', **context)


@app.route('/new_categories_list', methods=['GET'])
def new_categories_list():
    context = {
        'title': 'Categories list',
        'categories': AnimeCategory.query.all(),
    }

    return render_template('new/categories_list.html', **context)


@app.route('/new_category_change/<int:cat_id>', methods=['GET', 'POST'])
def new_category_change(cat_id):
    category = AnimeCategory.query.get_or_404(cat_id)
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
    context = {
        'title': f'Import anime from MAL'
    }

    if request.method == "POST":        
        anime_url = request.form['url']
        data = parsing.parse_mal_anime_page(anime_url)

        release = datetime.datetime.strptime(data['release'], '%b %d %Y').date()
        grade = int(request.form['grade'])

        if not 0 <= grade <= 100:
            flash('Grade', category='danger')
            return render_template('new/import_anime.html', **context)

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


@app.route('/new_anime/<int:anime_id>', methods=['GET', 'POST'])
def new_anime_page(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    comments = Comment.query.filter_by(anime_id=anime_id).order_by(Comment.created.desc()).all()

    context = {
        'title': anime.name,
        'anime': anime,
        'comments': comments
    }

    if request.method == "POST":
        # Comment instance
        comment = Comment(
            user_id=current_user.id,
            anime_id=anime.id,
            text=request.form.get('comment_text')
        )

        if request.form.get('comment_grade_permission'):
            comment.grade = request.form.get('comment_grade')
        
        # Comment commit
        db.session.add(comment)
        db.session.commit()

        flash(f"Comment has been successfuly added!", category="success")
        return redirect(request.url)

    return render_template('new/anime.html', **context)


@app.route('/related_anime/<int:anime_id>/add', methods=['GET', 'POST'])
def add_related_anime(anime_id):
    cur_anime = Anime.query.get_or_404(anime_id)
    animes = Anime.query.filter(Anime.id != anime_id)
    relation_categories = RelationCategory.query.all()

    if request.method == "POST":
        related_anime_id = request.form.get('related_anime_id')
        relation_category_id = request.form.get('relation_category_id')

        if related_anime_id and relation_category_id:
            # Create related anime instance
            rel_anime = RelatedAnime(
                to_anime_id = anime_id,
                relation_category_id = relation_category_id,
                anime_id = related_anime_id
            )

            # Related anime commit
            db.session.add(rel_anime)
            db.session.commit()

            # Generate success message
            flash(f"Related anime have been added", category="success")

            # Redirect to main anime page
            return redirect(url_for('new_anime_page', anime_id=anime_id))

    context = {
        'title': f'Add related anime to {cur_anime.name}',
        'cur_anime': cur_anime,
        'animes': animes,
        'relation_categories': relation_categories,
    }

    return render_template('new/add_related_anime.html', **context)
