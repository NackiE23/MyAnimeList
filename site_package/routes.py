from flask import render_template
from site_package import app
from site_package.models import Anime


@app.route('/')
def main_page():
    return render_template('index.html', title="Main", animes=Anime.query.all())
