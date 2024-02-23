from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import logout_user, login_user

from site_package.blueprints.user.forms import LoginForm, RegisterForm
from site_package.extensions import db
from site_package.models.user import User

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/register/', methods=['GET', 'POST'])
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

        return redirect(url_for('media_bp.home'))

    if form.errors:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('user/register.html', title='Register page', form=form)


@user_bp.route('/login/', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if request.method == "POST":
        try:
            if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                if user and user.check_password_if_exists(form.password.data):
                    login_user(user)
                    flash(f"You have successfully logged in as {user.name}", category="success")

                    return redirect(url_for('media_bp.home'))
                if not user:
                    flash(f"User with that email does not exist!")

        except ValueError:
            flash(f"Email and password does not match!")

    if form.errors != {}:
        for error in form.errors.values():
            flash(f"Error: {error}", category="danger")

    return render_template('user/login.html', title='Login page', form=form)


@user_bp.route('/logout/')
def logout():
    logout_user()
    flash("You have successfully loged out", category="success")

    return redirect(url_for('media_bp.home'))
