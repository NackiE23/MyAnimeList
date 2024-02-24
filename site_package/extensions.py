from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = './static/uploads'
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def compare_category_with_ids(media_categories: list, categories_ids: list) -> bool:
    return len(media_categories) != len(set([cat.id for cat in media_categories] + categories_ids))
