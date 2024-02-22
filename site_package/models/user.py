from datetime import datetime
from flask_login import UserMixin

from site_package.extensions import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(), nullable=True)
    name = db.Column(db.String(length=60), nullable=False)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    media_list = db.relationship("UserMediaList", lazy='subquery', backref=db.backref('user', lazy=True))
    comment = db.relationship("Comment", lazy='subquery', backref=db.backref('user', lazy=True))

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
