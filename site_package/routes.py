import os
import uuid
import datetime

import requests

from flask import render_template, redirect, url_for, flash, request, Markup
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from site_package import app, db, parsing
from site_package.forms import RegisterForm, LoginForm, AnimeModelForm
from site_package.models import Anime, User, AnimeCategory, ListCategory, UserAnimeList, anime_categories


def compare_category_with_ids(anime_categories: list, categories_ids: list) -> bool:
    return len(anime_categories) != len(set([cat.id for cat in anime_categories] + categories_ids))


@app.route('/', methods=['GET', 'POST'], defaults={"page": 1}) 
@app.route('/<int:page>', methods=['GET', 'POST'])
def anime_list(page):
    # Main variables
    page = page
    per_page = 25
    list_categories = ListCategory.query.all()

    # Get and paginate anime
    animes = Anime.query.filter(or_(Anime.name.like('%' + request.args.get('name', '') + '%'), 
                                    Anime.alternative_name.like('%' + request.args.get('name', '') + '%')))
    if request.args.get('sort', '') == "grade_up":
        animes = animes.order_by(Anime.grade.asc())
    else:
        animes = animes.order_by(Anime.grade.desc())
    animes = animes.paginate(page=page, per_page=per_page, error_out=False)
    
    if request.method == "POST":
        list_category_ids = request.form.get('str_list_category_ids', '').split()
        user_id = current_user.id
        anime_id = request.form.get('anime_id', '')

        if list_category_ids and user_id and anime_id:
            for category in list_category_ids:
                db.session.add(UserAnimeList(user_id=user_id, anime_id=anime_id, list_category_id=category))
            db.session.commit()

            flash(f"Anime successfuly added to your list(s)", category="success")
            return redirect(request.url)

        flash(f"Something went wrong", category="danger")
        return redirect(request.url)

    context = {
        'title': "Index page",
        'animes': animes,
        'request_args': request.args
    }

    return render_template('anime_list.html', **context)


@app.route('/seasonal/')
def seasonal_page():
    animes = parsing.parse_season_page()
    length = len(animes['name'])

    return render_template('seasonal_animes.html', title="Seasonal Animes", length=length, animes=animes)


@app.route('/my_lists/', methods=['GET'])
def my_lists_page():
    list_categories = ListCategory.query.all()

    if request.args.get('list_category_id'):
        list_category = ListCategory.query.get(request.args.get('list_category_id'))
    else:
        list_category = ListCategory.query.first()

    animes = UserAnimeList.query.filter_by(user=current_user, list_category=list_category)

    return render_template('my_lists.html', title="My Lists", list_categories=list_categories,
                           list_category=list_category, animes=animes)


@app.route('/add_anime/', methods=['GET', 'POST'])
def add_anime_page():
    form = AnimeModelForm()

    if request.method == "POST" and form.validate_on_submit():
        anime = Anime(name=form.name.data, release=form.release.data)

        if alter_name := form.alternative_name.data:
            anime.alternative_name = alter_name
        if description := form.description.data:
            anime.description = description
        if grade := form.grade.data:
            anime.grade = grade
        if img := form.img.data:
            filename = str(uuid.uuid1()) + '_' + secure_filename(img.filename)
            folder_release = anime.release.strftime('%Y/%m')

            if not os.path.exists(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release)):
                os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release))

            img.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release, filename))
            anime.img = os.path.join(app.config['UPLOAD_FOLDER'][1:], folder_release, filename)
        if categories := request.form.get('id_categories', '').split():
            for category_id in categories:
                anime.categories.append(AnimeCategory.query.get(category_id))

        db.session.add(anime)
        db.session.commit()

        flash(Markup(f"Anime {anime.name} has been added! <a href='{ url_for('change_anime_page', anime_id=anime.id) }'>Link here</a>"), category="success")

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('add_anime.html', title='Add anime', form=form, categories=AnimeCategory.query.all())


@app.route('/import_anime/', methods=['GET', 'POST'])
def import_anime():
    if request.method == "POST":
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

    return render_template('import_anime.html', title='Import Anime from MAL')


@app.route('/change_anime/<int:anime_id>/', methods=['GET', 'POST'])
def change_anime_page(anime_id):    
    anime = Anime.query.get_or_404(anime_id)
    available_categories = [c for c in AnimeCategory.query.all() if c not in anime.categories]

    form = AnimeModelForm()

    if request.method == "POST" and form.validate_on_submit():

        if form.name.data and form.name.data != anime.name:
            anime.name = form.name.data
        if form.alternative_name.data and form.alternative_name.data != anime.alternative_name:
            anime.alternative_name = form.alternative_name.data
        if form.release.data and form.release.data != anime.release:
            anime.release = form.release.data
        if form.description.data and form.description.data != anime.description:
            anime.description = form.description.data
        if form.grade.data and form.grade.data != anime.grade:
            anime.grade = form.grade.data
        if img := form.img.data:
            filename = str(uuid.uuid1()) + '_' + secure_filename(img.filename)
            folder_release = anime.release.strftime('%Y/%m')

            if not os.path.exists(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release)):
                os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release))

            img.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], folder_release, filename))
            anime.img = os.path.join(app.config['UPLOAD_FOLDER'][1:], folder_release, filename)

        categories = request.form.get('id_categories', '').split()
        if compare_category_with_ids(anime.categories, categories):
            category_objs = []
            for category_id in categories:
                category_objs.append(AnimeCategory.query.get(category_id))
            anime.categories = category_objs

        db.session.commit()

        flash(f"Changes have been saved", category="success")
        return redirect(url_for('anime_list'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('change_anime.html', title="Change anime", form=form, anime=anime, categories=available_categories)


@app.route('/delete_anime/<int:anime_id>', methods=['POST'])
def delete_anime(anime_id):
    anime = Anime.query.get(anime_id)
    anime_name = anime.name
    db.session.delete(anime)
    db.session.commit()

    flash(f"{anime_name} has been deleted!", category='success')
    return redirect(url_for('anime_list'))


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(name=form.name.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f"You have successfully logged in as {user_to_create.name}", category="success")

        return redirect(url_for('anime_list'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('register.html', title='Register page', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if request.method == "POST":
        try:
            if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                if user and user.check_password_if_exists(form.password.data):
                    login_user(user)
                    flash(f"You have successfully logged in as {user.name}", category="success")

                    return redirect(url_for('anime_list'))
                if not user:
                    flash(f"User with that email does not exist!")

        except ValueError:
            flash(f"Email and password does not match!")

    if form.errors != {}:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('login.html', title='Login page', form=form)


@app.route('/logout/')
def logout_page():
    logout_user()
    flash("You have successfully loged out", category="success")

    return redirect(url_for('anime_list'))
