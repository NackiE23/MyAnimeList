from flask import redirect, url_for

from site_package import app
from site_package.blueprints.media.routes import media_bp
from site_package.blueprints.old_version.routes import old_version_bp
from site_package.blueprints.user.routes import user_bp


app.register_blueprint(old_version_bp, url_prefix="/old")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(media_bp, url_prefix="/media")


@app.route('/', methods=['GET'])
def main_page():
    return redirect(url_for("media_bp.home"))
