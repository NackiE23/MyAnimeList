# New Project structure
# https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy
import os

from flask import Flask
from flask_babel import Babel

from .blueprints.admin.routes import admin
from .extensions import db, bcrypt, login_manager, UPLOAD_FOLDER

app = Flask(__name__, instance_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SECRET_KEY'] = 'jhvaslkjh21234hghgjs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FLASK_ADMIN_SWATCH'] = 'superhero'

babel = Babel(app)

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)
admin.init_app(app)

from site_package import routes, error_handlers

# Create tables
# with app.app_context():
#     db.create_all()
