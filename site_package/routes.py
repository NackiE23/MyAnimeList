import os.path
import uuid

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from werkzeug.utils import secure_filename

from site_package import app, db
from site_package.forms import RegisterForm, LoginForm, AddAnimeForm
from site_package.models import Anime, User


@app.route('/')
def index_page():
    return render_template('index.html', title="Index page", animes=Anime.query.all())


@app.route('/add_anime/', methods=['GET', 'POST'])
def add_anime_page():
    form = AddAnimeForm()

    if form.validate_on_submit():
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

        db.session.add(anime)
        db.session.commit()

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('add_anime.html', title='Add anime', form=form)


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

    return redirect(url_for('index_page'))
