import enum
from datetime import datetime

from flask import url_for
from sqlalchemy import Enum

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

    added = db.Column(db.Date(), default=datetime.now)

    type_id = db.Column(db.Integer, db.ForeignKey("media_type.id"), nullable=False)
    type = db.relationship("MediaType", back_populates="media", lazy='subquery')

    categories = db.relationship("MediaCategory", secondary=media_categories, lazy='subquery',
                                 backref=db.backref('medias', lazy=True))
    user_list = db.relationship("UserMediaList", lazy='subquery', backref=db.backref('media', lazy=True))
    comments = db.relationship("Comment", lazy='subquery', backref=db.backref('media', lazy=True))
    images = db.relationship("MediaImage", back_populates="media", lazy="subquery")

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


class MediaImage(db.Model):
    __tablename__ = "media_images"

    id = db.Column(db.Integer(), primary_key=True)
    media_id = db.Column(db.Integer(), db.ForeignKey("media.id"), nullable=False)
    image_path = db.Column(db.String(), nullable=False)  # Path where the image is stored
    description = db.Column(db.String(length=255), nullable=True)
    order = db.Column(db.Integer(), nullable=True, default=99)

    media = db.relationship("Media", back_populates="images")

    def __repr__(self):
        return f"<MediaImage {self.image_path}> ({self.description})"


class MediaCategory(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    description = db.Column(db.String(length=2000), nullable=True)

    def __repr__(self):
        return self.name

    def get_absolute_url(self):
        return url_for("media_bp.category_info", cat_id=self.id)


class RelationCategoryEnum(enum.Enum):
    # TODO: Make more flexible to not have to change the code when adding new categories
    SIMILAR = "similar"
    PREQUEL = "prequel"
    SEQUEL = "sequel"
    ALTERNATIVE_SETTING = "alternative_setting"
    ALTERNATIVE_VERSION = "alternative_version"
    SPIN_OFF = "spin-off"
    SIDE_STORY = "side_story"
    OTHER = "other"

    @classmethod
    def ordered_choices(cls):
        return [
            (cls.SIMILAR, "Similar"),
            (cls.PREQUEL, "Prequel"),
            (cls.SEQUEL, "Sequel"),
            (cls.ALTERNATIVE_SETTING, "Alternative Setting"),
            (cls.ALTERNATIVE_VERSION, "Alternative Version"),
            (cls.SPIN_OFF, "Spin-off"),
            (cls.SIDE_STORY, "Side Story"),
            (cls.OTHER, "Other"),
        ]

    @property
    def label(self):
        labels = {
            "similar": "Similar",
            "prequel": "Prequel",
            "sequel": "Sequel",
            "alternative_setting": "Alternative Setting",
            "alternative_version": "Alternative Version",
            "spin-off": "Spin-off",
            "side_story": "Side Story",
            "other": "Other",
        }
        return labels.get(self.value, "Unknown")


class RelatedMedia(db.Model):
    __tablename__ = "related_media"

    id = db.Column(db.Integer(), primary_key=True)
    # for 'to_media' pinnes 'media'
    to_media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    relation_category = db.Column(Enum(RelationCategoryEnum), nullable=False)
    to_media = db.relationship("Media", foreign_keys=[to_media_id])
    media = db.relationship("Media", foreign_keys=[media_id])

    order = db.Column(db.Integer(), nullable=True, default=99)

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
