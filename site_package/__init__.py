import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

UPLOAD_FOLDER = './static/uploads'

app = Flask(__name__, instance_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SECRET_KEY'] = 'jhvaslkjh21234hghgjs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

from site_package import routes, new_routes, error_handlers

# Create tables
# with app.app_context():
#     db.create_all()
