# New Project structure
# https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy
import os

from dotenv import load_dotenv
from flask import Flask
from flask_babel import Babel

from .blueprints.admin.routes import admin
from .extensions import db, bcrypt, login_manager, UPLOAD_FOLDER, init_s3

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__, instance_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SECRET_KEY'] = 'jhvaslkjh21234hghgjs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FLASK_ADMIN_SWATCH'] = 'superhero'

# Babel
babel = Babel(app)

# AWS S3 configuration
app.config['S3_BUCKET'] = os.getenv("S3_BUCKET")
app.config['S3_REGION'] = os.getenv("S3_REGION")
app.config['S3_ACCESS_KEY'] = os.getenv("AWS_ACCESS_KEY_ID")
app.config['S3_SECRET_KEY'] = os.getenv("AWS_SECRET_ACCESS_KEY")
app.config['S3_DOMAIN'] = f"https://{app.config['S3_BUCKET']}.s3.{app.config['S3_REGION']}.amazonaws.com"
init_s3(app)

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)
admin.init_app(app)

from site_package import routes, error_handlers

# Create tables
with app.app_context():
    db.create_all()
