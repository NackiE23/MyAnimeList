from flask import redirect, url_for

from site_package import app


@app.route('/', methods=['GET'])
def main_page():
    return redirect(url_for("media_bp.home"))
