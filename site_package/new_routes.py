import random

from flask import render_template, redirect, flash, request
from sqlalchemy.sql.expression import func

from site_package import app, db
from site_package.forms import CategoryForm
from site_package.models import Anime, AnimeCategory


@app.route('/new_home', methods=['GET', 'POST'])
def new_home():
    pined_categories = ['Comedy', 'Adventure', 'Drama']
    categories = list(AnimeCategory.query.filter(AnimeCategory.animes.any(), AnimeCategory.name.in_(pined_categories)))
    categories += list(AnimeCategory.query.filter(AnimeCategory.animes.any(), ~AnimeCategory.name.in_(pined_categories)).order_by(func.random()).limit(5))
    category_animes = []
    
    for category in categories:
        animes = list(Anime.query.filter(Anime.categories.any(AnimeCategory.id==category.id)).order_by(func.random()).limit(8))

        if len(animes) < 8:
            animes = random.choices(animes, k=8)

        category_animes.append([category, animes])

    context = {
        'title': "Index page",
        'category_animes': category_animes,
    }

    return render_template('new/home.html', **context)


@app.route('/new_categories_list', methods=['GET'])
def new_categories_list():
    context = {
        'title': 'Categories list',
        'categories': AnimeCategory.query.all(),
    }

    return render_template('new/categories_list.html', **context)


@app.route('/new_category_change/<int:cat_id>', methods=['GET', 'POST'])
def new_category_change(cat_id):
    category = AnimeCategory.query.get(cat_id)
    form = CategoryForm(name=category.name, description=category.description)

    context = {
        'title': f'Change {category.name} Category',
        'category': category,
        'form': form,
    }

    if request.method == "POST" and form.validate_on_submit():
        if form.name.data and form.name.data != category.name:
            category.name = form.name.data
        if form.description.data and form.description.data != category.description:
            category.description = form.description.data

        db.session.commit()
        flash(f"Changes have been saved", category="success")

        return redirect(request.url)

    return render_template('new/category_change.html', **context)
