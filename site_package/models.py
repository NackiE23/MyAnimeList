from flask_login import UserMixin

from site_package import db, login_manager, bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    anime_list = db.relationship("UserAnimeList", lazy='subquery', backref=db.backref('user', lazy=True))

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


anime_categories = db.Table(
    'anime_category',
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
)


class Anime(db.Model):
    __tablename__ = "anime"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    alternative_name = db.Column(db.String(length=60), nullable=True)
    release = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=True)
    grade = db.Column(db.Integer(), nullable=True, default=0)
    img = db.Column(db.String(), nullable=True)
    categories = db.relationship("AnimeCategory", secondary=anime_categories, lazy='subquery',
                                 backref=db.backref('animes', lazy=True))
    user_list = db.relationship("UserAnimeList", lazy='subquery', backref=db.backref('anime', lazy=True))

    def __repr__(self):
        return self.name

    def categories_to_text(self):
        return " ".join([c.name for c in self.categories])

    def categories_to_text_ids(self):
        return " ".join([str(c.id) for c in self.categories])

    def normalize_release(self):
        return f"{number_to_month(self.release.month)} {self.release.day}, {self.release.year}"

    def get_url(self):
        return f"/#anime_{self.id}"


class AnimeCategory(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)

    def __repr__(self):
        return self.name


class ListCategory(db.Model):
    __tablename__ = "list_category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    user_anime_list = db.relationship("UserAnimeList", lazy='subquery', backref=db.backref('list_category', lazy=True))

    def __repr__(self):
        return self.name


class UserAnimeList(db.Model):
    __tablename__ = "user_anime_list"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), primary_key=True)
    list_category_id = db.Column(db.Integer, db.ForeignKey('list_category.id'), primary_key=True)

    def __repr__(self):
        return f"{self.user} {self.anime} {self.list_category}"


def number_to_month(number):
    if number == 1:
        return "Jan"
    elif number == 2:
        return "Feb"
    elif number == 3:
        return "Mar"
    elif number == 4:
        return "Apr"
    elif number == 5:
        return "May"
    elif number == 6:
        return "Jun"
    elif number == 7:
        return "Jul"
    elif number == 8:
        return "Aug"
    elif number == 9:
        return "Sep"
    elif number == 10:
        return "Oct"
    elif number == 11:
        return "Nov"
    elif number == 12:
        return "Dec"
    else:
        return "???"
