# New Project structure
# https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy
import os

from flask import Flask

from .blueprints.admin.routes import admin_bp
from .blueprints.media.routes import media_bp
from .blueprints.old_version.routes import old_version_bp
from .blueprints.user.routes import user_bp
from .extensions import db, bcrypt, login_manager, UPLOAD_FOLDER

app = Flask(__name__, instance_path=os.path.dirname(os.path.abspath(__file__)))
app.register_blueprint(old_version_bp, url_prefix="/old")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(media_bp)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SECRET_KEY'] = 'jhvaslkjh21234hghgjs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

from site_package import new_routes, error_handlers

# Create tables
# with app.app_context():
#     db.create_all()
