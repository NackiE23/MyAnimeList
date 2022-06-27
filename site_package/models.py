from flask_login import UserMixin

from site_package import db, login_manager, bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)

    def __repr__(self):
        return self.name

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password_if_exists(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Anime(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    alternative_name = db.Column(db.String(length=60), nullable=True)
    release = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=True)
    grade = db.Column(db.Integer(), nullable=True)
    img = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return self.name
