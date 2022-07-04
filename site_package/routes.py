import os.path
import uuid

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from werkzeug.utils import secure_filename

from site_package import app, db
from site_package.forms import RegisterForm, LoginForm, AnimeModelForm
from site_package.models import Anime, User, AnimeCategory, ListCategory, UserAnimeList
from site_package.parsing import parse_season_page


def compare_category_with_name(anime_categories: list, categories_name: list) -> bool:
    # return len(anime_categories) == len(set([cat.name for cat in anime_categories] + categories_name))
    if len(anime_categories) != len(categories_name):
        return True

    for pk, category in enumerate(anime_categories):
        if category.name not in categories_name[pk]:
            return True

    return False


@app.route('/', methods=['GET', 'POST'])
def index_page():
    animes = Anime.query.all()
    list_categories = ListCategory.query.all()

    if request.method == "POST":
        list_category_ids = request.form.get('str_list_category_ids', '').split()
        user_id = request.form.get('user_id', '')
        anime_id = request.form.get('anime_id', '')

        if list_category_ids and user_id and anime_id:
            for category in list_category_ids:
                db.session.add(UserAnimeList(user_id=user_id, anime_id=anime_id, list_category_id=category))
            db.session.commit()

            flash(f"Anime successfuly added to your list(s)", category="success")
            return redirect(request.url)

        flash(f"Something went wrong", category="danger")
        return redirect(request.url)

    return render_template('anime_list.html', title="Index page", animes=animes, list_categories=list_categories)


@app.route('/seasonal/')
def seasonal_page():
    animes = parse_season_page()
    length = len(animes['name'])

    return render_template('seasonal_animes.html', title="Seasonal Animes", length=length, animes=animes)


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
            img.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            anime.img = os.path.join(app.config['UPLOAD_FOLDER'][1:], filename)
        if categories := request.form.get('categories', '').split():
            for category in categories:
                obj = AnimeCategory.query.filter_by(name=category).first()
                anime.categories.append(obj)

        db.session.add(anime)
        db.session.commit()

        flash(f"Anime {anime.name} added!", category="success")

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('add_anime.html', title='Add anime', form=form, categories=AnimeCategory.query.all())


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
            img.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            anime.img = os.path.join(app.config['UPLOAD_FOLDER'][1:], filename)

        categories = request.form.get('categories', '').split()
        if categories and compare_category_with_name(anime.categories, categories):
            category_objs = []
            for category in categories:
                obj = AnimeCategory.query.filter_by(name=category).first()
                category_objs.append(obj)
            anime.categories = category_objs

        db.session.commit()

        flash(f"Changes have been saved", category="success")
        return redirect(url_for('index_page'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('change_anime.html', title="Change anime", form=form, anime=anime, categories=available_categories)


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

        return redirect(url_for('index_page'))

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

                    return redirect(url_for('index_page'))
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

    return redirect(url_for('index_page'))
