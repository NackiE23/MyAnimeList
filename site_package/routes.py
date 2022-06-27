from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user

from site_package import app, db
from site_package.forms import RegisterForm, LoginForm
from site_package.models import Anime, User


@app.route('/')
def index_page():
    return render_template('index.html', title="Index page", animes=Anime.query.all())


@app.route('/register/', methods=["GET", "POST"])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        print(f'{form.name=} \n'
              f'{form.email=} \n'
              f'{form.password1=}')
        user_to_create = User(name=form.name.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('index_page'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('register.html', title='Register page', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password_if_exists(form.password.data):
            login_user(user)

            return redirect(url_for('index_page'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('login.html', title='Login page', form=form)
