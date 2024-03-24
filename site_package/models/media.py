from datetime import datetime

from flask import url_for

from site_package.extensions import db


media_categories = db.Table(
    'media_category',
    db.Column('media_id', db.Integer, db.ForeignKey('media.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
)


class MediaType(db.Model):
    __tablename__ = "media_type"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=255), nullable=False)

    media = db.relationship("Media", back_populates="type", lazy='subquery')

    def __repr__(self):
        return self.name


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    alternative_name = db.Column(db.String(length=60), nullable=True)
    release = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=True)
    grade = db.Column(db.Integer(), nullable=True, default=0)
    img = db.Column(db.String(), default="/static/images/base/default.png", nullable=True)

    type_id = db.Column(db.Integer, db.ForeignKey("media_type.id"), nullable=False)
    type = db.relationship("MediaType", back_populates="media", lazy='subquery')

    categories = db.relationship("MediaCategory", secondary=media_categories, lazy='subquery',
                                 backref=db.backref('medias', lazy=True))
    user_list = db.relationship("UserMediaList", lazy='subquery', backref=db.backref('media', lazy=True))
    comments = db.relationship("Comment", lazy='subquery', backref=db.backref('media', lazy=True))

    def __repr__(self):
        return self.name

    def categories_to_text(self):
        return " ".join([c.name for c in self.categories])

    def categories_to_text_ids(self):
        return " ".join([str(c.id) for c in self.categories])

    def normalize_release(self):
        return f"{number_to_month(self.release.month)} {self.release.day}, {self.release.year}"

    def get_url(self):
        return f"/#media_{self.id}"


class MediaCategory(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    description = db.Column(db.String(length=2000), nullable=True)

    def __repr__(self):
        return self.name

    def get_absolute_url(self):
        return url_for("media_bp.category_info", cat_id=self.id)


class RelationCategory(db.Model):
    __tablename__ = "relation_category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    priority = db.Column(db.Integer(), nullable=False, unique=True)

    def __repr__(self):
        return f'{self.name}'


class RelatedMedia(db.Model):
    __tablename__ = "related_media"

    id = db.Column(db.Integer(), primary_key=True)

    relation_category_id = db.Column(db.Integer, db.ForeignKey('relation_category.id'), nullable=False)
    # for 'to_media' pinnes 'media'
    to_media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    relation_category = db.relationship("RelationCategory", foreign_keys=[relation_category_id])
    to_media = db.relationship("Media", foreign_keys=[to_media_id])
    media = db.relationship("Media", foreign_keys=[media_id])

    def __repr__(self):
        return f"{self.media}"


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)
    last_changes = db.Column(db.DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    text = db.Column(db.String(), nullable=False)
    grade = db.Column(db.Integer(), nullable=True, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)


class ListCategory(db.Model):
    __tablename__ = "list_category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)

    user_media_list = db.relationship("UserMediaList", lazy='subquery', backref=db.backref('list_category', lazy=True))

    def __repr__(self):
        return self.name


class UserMediaList(db.Model):
    __tablename__ = "user_media_list"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), primary_key=True)
    list_category_id = db.Column(db.Integer, db.ForeignKey('list_category.id'), primary_key=True)

    def __repr__(self):
        return f"{self.user} {self.media} {self.list_category}"


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
