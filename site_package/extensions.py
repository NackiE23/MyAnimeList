from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = './static/uploads'
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
