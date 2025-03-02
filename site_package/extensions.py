import boto3
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = './static/uploads'
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
s3 = None


def init_s3(app):
    global s3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=app.config['S3_SECRET_KEY'],
        region_name=app.config['S3_REGION'],
    )


def compare_category_with_ids(media_categories: list, categories_ids: list) -> bool:
    return len(media_categories) != len(set([cat.id for cat in media_categories] + categories_ids))
