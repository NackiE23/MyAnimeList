import datetime
import os
import random
import uuid

import boto3
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, Markup, current_app
from flask_login import current_user
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename

from site_package import parsing
from site_package.decorators import admin_required
from site_package.extensions import db, compare_category_with_ids, s3
from site_package.models.media import Media, MediaCategory, Comment, RelatedMedia, RelationCategoryEnum, MediaImage

from .forms import CategoryForm, MediaForm, MediaImageForm

media_bp = Blueprint('media_bp', __name__)


@media_bp.route('/home', methods=['GET'])
def home():
    pined_categories = ['Comedy', 'Adventure', 'Drama']
    categories = list(MediaCategory.query.filter(MediaCategory.medias.any(), MediaCategory.name.in_(pined_categories)))
    categories += list(
        MediaCategory.query.filter(MediaCategory.medias.any(), ~MediaCategory.name.in_(pined_categories)).order_by(
            func.random()).limit(5))
    category_animes = []

    for category in categories:
        animes = list(
            Media.query.filter(Media.categories.any(MediaCategory.id == category.id)).order_by(
                func.random()).limit(8))

        if len(animes) < 8:
            animes = random.choices(animes, k=8)

        category_animes.append([category, animes])

    context = {
        'title': "Index page",
        'category_animes': category_animes,
    }

    return render_template('media/home.html', **context)


@media_bp.route('/search_media', methods=['GET'])
def search_media():
    page = int(request.args.get('page', 1))
    per_page = 50

    medias = Media.query.filter(or_(Media.name.like('%' + request.args.get('name', '') + '%'),
                                    Media.alternative_name.like('%' + request.args.get('name', '') + '%'))
                                )
    if request.args.get('sort', '') == "grade_up":
        medias = medias.order_by(Media.grade.asc())
    else:
        medias = medias.order_by(Media.grade.desc())
    medias = medias.paginate(page=page, per_page=per_page, error_out=False)

    context = {
        'title': "Search",
        'medias': medias,
        'request_args': {k: v for k, v in request.args.items() if k != "page"}
    }

    return render_template('media/search_media.html', **context)


@media_bp.route('/top_list', methods=['GET'])
def top_list():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    media_count = Media.query.count()

    context = {
        'title': "Top List",
        'animes': Media.query.order_by(Media.grade.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        ),
        'media_count': media_count,
        'per_page': per_page,
        'request_args': {k: v for k, v in request.args.items() if k != "page"}
    }

    return render_template('media/top_list.html', **context)


@media_bp.route('/categories_list', methods=['GET'])
def categories_list():
    categories = MediaCategory.query.order_by(MediaCategory.name).all()

    context = {
        'title': 'Categories list',
        'categories': categories,
        'categories_count': len(categories)
    }

    return render_template('media/categories_list.html', **context)


@media_bp.route('/category/<int:cat_id>', methods=['GET'])
def category_info(cat_id):
    category = MediaCategory.query.get_or_404(cat_id)
    animes = Media.query.order_by(Media.grade.desc()).filter(
        Media.categories.any(MediaCategory.id == category.id))

    page = int(request.args.get('page', 1))
    per_page = 50
    paginated_animes = animes.paginate(page=page, per_page=per_page, error_out=False)

    context = {
        'title': f'{category.name} anime',
        'category': category,
        'animes': paginated_animes,
        'anime_count': animes.count(),
        'average_rating': round(animes.with_entities(func.avg(Media.grade).label('average')).first()[0], 2),
        'request_args': {k: v for k, v in request.args.items() if k != "page"}
    }

    return render_template('media/category.html', **context)


@media_bp.route('/category_change/<int:cat_id>', methods=['GET', 'POST'])
@admin_required
def category_change(cat_id):
    category = MediaCategory.query.get_or_404(cat_id)
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

    return render_template('media/category_change.html', **context)


@media_bp.route('/import_anime_from_mal', methods=['GET', 'POST'])
@admin_required
def import_anime_from_mal():
    context = {
        'title': f'Import anime from MAL'
    }

    if request.method == "POST":
        anime_url = request.form['url']
        data = parsing.parse_mal_anime_page(anime_url)

        release = datetime.datetime.strptime(data['release'], '%b %d %Y').date()
        grade = int(request.form['grade'])

        if not 0 <= grade <= 100:
            flash('Grade', category='danger')
            return render_template('media/import_anime.html', **context)

        # Main info
        anime = Media(
            name=data['name'],
            alternative_name=data['alternative_name'],
            release=release,
            grade=grade,
            description=data['description'],
            type_id=1
        )

        # Add categories
        for category_name in data['categories']:
            if category := MediaCategory.query.filter_by(name=category_name).first():
                pass
            else:
                category = MediaCategory(name=category_name)
                db.session.add(category)
                db.session.commit()

            anime.categories.append(category)

        # Image upload
        try:
            img_data = requests.get(data['img_url'], verify=False, timeout=5).content
            filename = str(uuid.uuid1()) + '_' + secure_filename(data['img_url'].split('/')[-1])
            folder_release = release.strftime('%Y/%m')
            img_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], folder_release)
            img_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], folder_release, filename)

            if not os.path.exists(img_folder):
                os.makedirs(img_folder)

            with open(img_path, 'wb') as handler:
                handler.write(img_data)

            anime.img = os.path.join(current_app.config['UPLOAD_FOLDER'][1:], folder_release, filename)
        except requests.exceptions.ConnectionError:
            flash('Image not available', category='danger')

        # Anime commit
        db.session.add(anime)
        db.session.commit()

        flash(Markup(
            f"Anime {anime.name} has been imported! <a href='{url_for('media_bp.change_media', media_id=anime.id)}'>Link here</a>"),
              category="success")

    return render_template('media/import_anime.html', **context)


@media_bp.route('/<int:anime_id>', methods=['GET', 'POST'])
def anime_page(anime_id):
    media = Media.query.get_or_404(anime_id)
    related_media = RelatedMedia.query.filter_by(to_media_id=anime_id).order_by(RelatedMedia.order).all()
    gallery = MediaImage.query.filter_by(media_id=anime_id).order_by(MediaImage.order).all()
    comments = Comment.query.filter_by(media_id=anime_id).order_by(Comment.created.desc()).all()

    context = {
        'title': media.name,
        'media': media,
        'related_media': related_media,
        'comments': comments,
        'gallery': gallery,
    }

    if request.method == "POST":
        # Comment instance
        comment = Comment(
            user_id=current_user.id,
            media_id=media.id,
            text=request.form.get('comment_text')
        )

        if request.form.get('comment_grade_permission'):
            comment.grade = request.form.get('comment_grade')

        # Comment commit
        db.session.add(comment)
        db.session.commit()

        flash(f"Comment has been successfuly added!", category="success")
        return redirect(request.url)

    return render_template('media/anime.html', **context)


@media_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_media():
    form = MediaForm()

    context = {
        'title': "Create Media",
        'form': form,
        'categories': [c for c in MediaCategory.query.order_by('name').all()],
    }

    if request.method == "POST" and form.validate_on_submit():
        media = Media(name=form.name.data, release=form.release.data, type_id=form.type_id.data)

        if alter_name := form.alternative_name.data:
            media.alternative_name = alter_name
        if description := form.description.data:
            media.description = description
        if grade := form.grade.data:
            media.grade = grade
        if img := form.img.data:
            # Save to S3
            s3_path = f"{uuid.uuid4()}_{secure_filename(img.filename)}"
            s3.upload_fileobj(
                img, current_app.config['S3_BUCKET'], s3_path,
                ExtraArgs={"ContentType": img.mimetype}
            )

            media.img = f"{current_app.config['S3_DOMAIN']}/{s3_path}"
        if categories := request.form.get('id_categories', '').split():
            for category_id in categories:
                media.categories.append(MediaCategory.query.get(category_id))

        db.session.add(media)
        db.session.commit()

        flash(Markup(f"Media {media.name} has been added! <a href='{ url_for('media_bp.change_media', media_id=media.id) }'>Link here</a>"), category="success")

    return render_template('media/media_create.html', **context)


@media_bp.route('/<int:media_id>/change', methods=['GET', 'POST'])
@admin_required
def change_media(media_id):
    media = Media.query.get_or_404(media_id)
    form = MediaForm(**media.__dict__)

    context = {
        'title': f'Change {media.name}',
        'media': media,
        'categories': [c for c in MediaCategory.query.order_by('name').all() if c not in media.categories],
        'form': form,
    }

    if request.method == "POST" and form.validate_on_submit():
        if form.type_id.data and form.type_id.data != media.type_id:
            media.type_id = form.type_id.data
        if form.name.data and form.name.data != media.name:
            media.name = form.name.data
        if form.alternative_name.data and form.alternative_name.data != media.alternative_name:
            media.alternative_name = form.alternative_name.data
        if form.release.data and form.release.data != media.release:
            media.release = form.release.data
        if form.description.data and form.description.data != media.description:
            media.description = form.description.data
        if form.grade.data and form.grade.data != media.grade:
            media.grade = form.grade.data
        if img := form.img.data:
            # Save to S3
            s3_path = f"{uuid.uuid4()}_{secure_filename(img.filename)}"
            s3.upload_fileobj(
                img, current_app.config['S3_BUCKET'], s3_path,
                ExtraArgs={"ContentType": img.mimetype}
            )

            media.img = f"{current_app.config['S3_DOMAIN']}/{s3_path}"

        categories = request.form.get('id_categories', '').split()
        if compare_category_with_ids(media.categories, categories):
            category_objs = []
            for category_id in categories:
                category_objs.append(MediaCategory.query.get(category_id))
            media.categories = category_objs

        db.session.commit()

        flash(f"Changes have been saved", category="success")

        if request.args.get('redirect_to', ''):
            return redirect(request.args.get('redirect_to'))
        else:
            return redirect(url_for('media_bp.anime_page', anime_id=media.id))

    return render_template('media/media_change.html', **context)


@media_bp.route('/<int:media_id>/add_images', methods=['GET', 'POST'])
@admin_required
def add_media_images(media_id):
    media = Media.query.get_or_404(media_id)
    form = MediaImageForm()

    context = {
        'title': f'Add image to {media.name}',
        'media': media,
        'form': form,
    }

    if request.method == "POST" and form.validate_on_submit():
        for img in form.imgs.data:
            s3_path = f"{uuid.uuid4()}_{secure_filename(img.filename)}"

            # Завантаження в S3
            s3.upload_fileobj(
                img, current_app.config['S3_BUCKET'], s3_path,
                ExtraArgs={"ContentType": img.mimetype}
            )

            # Збереження URL в базі даних
            image_url = f"{current_app.config['S3_DOMAIN']}/{s3_path}"
            media_image = MediaImage(
                media_id=media_id,
                description=form.description.data,
                image_path=image_url,
                order=form.order.data,
            )
            db.session.add(media_image)

        db.session.commit()
        flash(f"Image has been added", category="success")
        return redirect(url_for('media_bp.anime_page', anime_id=media.id))

    return render_template('media/add_media_image.html', **context)


@media_bp.route('/related_media/<int:media_id>/add', methods=['GET', 'POST'])
@admin_required
def add_related_anime(media_id):
    cur_anime = Media.query.get_or_404(media_id)

    # 'not_in' doesn't work in pythonanywhere.
    # cur_related_anime = RelatedMedia.query.filter_by(to_media_id=anime_id)
    # unused_anime = [anime_id] + [anime.anime.id for anime in cur_related_anime]
    # animes = Anime.query.filter(Anime.id.not_in(unused_anime))

    medias = Media.query.filter(Media.id != media_id)
    relation_categories = RelationCategoryEnum.ordered_choices()

    if request.method == "POST":
        related_anime_id = request.form.get('related_anime_id')
        relation_category = request.form.get('relation_category')
        order = request.form.get('order')

        if related_anime_id and relation_category:
            # Create related anime instance
            rel_anime = RelatedMedia(
                to_media_id=media_id,
                media_id=related_anime_id,
                relation_category=RelationCategoryEnum(relation_category),
                order=order
            )

            # Related anime commit
            db.session.add(rel_anime)
            db.session.commit()

            # Generate success message
            flash(f"Related anime have been added", category="success")

            # Redirect to main anime page
            return redirect(url_for('media_bp.anime_page', anime_id=media_id))

    context = {
        'title': f'Add related anime to {cur_anime.name}',
        'cur_anime': cur_anime,
        'medias': medias,
        'relation_categories': relation_categories,
    }

    return render_template('media/add_related_anime.html', **context)
