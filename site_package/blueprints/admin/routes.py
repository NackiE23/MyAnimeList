import os
from datetime import datetime

from flask import redirect, url_for, current_app
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import ImageUploadField
from flask_admin.menu import MenuLink
from flask_login import current_user

from site_package.extensions import db, UPLOAD_FOLDER
from site_package.models.media import Media, MediaType, MediaCategory, RelatedMedia, MediaImage, Comment
from site_package.models.user import User


class AccessMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user_bp.login_page'))


class CustomAdminIndexView(AccessMixin, AdminIndexView):
    @expose('/')
    def index(self):
        counts = [
            {'title': 'Users', 'count': User.query.count()},
            {'title': 'Media', 'count': Media.query.count()},
            {'title': 'Media Types', 'count': MediaType.query.count()},
            {'title': 'Media Categories', 'count': MediaCategory.query.count()},
            {'title': 'Related Media', 'count': RelatedMedia.query.count()},
            {'title': 'Media Images', 'count': MediaImage.query.count()},
        ]
        return self.render('admin/index.html', counts=counts)


class AdminModelView(AccessMixin, ModelView):
    pass


def get_upload_path():
    return current_app.root_path


def image_namegen(obj, file_data):
    """Generate a relative file path to store in the database."""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    filename = file_data.filename
    return os.path.join(current_app.config['UPLOAD_FOLDER'][2:], year, month, filename)  # Store relative path in DB


class UserAdminView(AdminModelView):
    form_columns = ['name', 'email', 'created', 'is_admin']
    column_searchable_list = ['name', 'email']
    column_filters = ['is_admin']


class MediaImageView(AdminModelView):
    column_searchable_list = ['media.name', 'media.alternative_name', 'description', 'image_path']
    # Customizing the form to use ImageUploadField for image uploads
    form_overrides = {
        'image_path': ImageUploadField
    }

    form_args = {
        'image_path': {
            'label': 'Image',
            'base_path': get_upload_path,
            'namegen': image_namegen,
            'allow_overwrite': False
        }
    }


class MediaAdminView(AdminModelView):
    form_columns = ['name', 'alternative_name', 'release', 'description', 'grade', 'img', 'type', 'categories', 'user_list', 'comments', 'images', 'added']
    column_searchable_list = ['name', 'alternative_name', 'description']
    column_filters = ['type', 'categories']


class CommentAdminView(AdminModelView):
    form_columns = ['user', 'media', 'text', 'created']
    column_searchable_list = ['text']
    column_filters = ['user.name', 'user.email', 'media.name', 'media.alternative_name', 'created']


class MediaTypeAdminView(AdminModelView):
    form_columns = ['name']
    column_searchable_list = ['name']
    column_filters = ['name']


class MediaCategoryAdminView(AdminModelView):
    form_columns = ['name', 'description']
    column_searchable_list = ['name']
    column_filters = ['name']


class RelatedMediaAdminView(AdminModelView):
    form_columns = ['media', 'to_media', 'relation_category', 'order']
    column_searchable_list = ['media.name', 'media.alternative_name', 'to_media.name', 'to_media.alternative_name']
    column_filters = ['media.name', 'media.alternative_name', 'to_media.name', 'to_media.alternative_name', 'relation_category', 'order']


admin = Admin(name='admin', index_view=CustomAdminIndexView(), template_mode='bootstrap4')

admin.add_view(UserAdminView(User, db.session))
admin.add_view(MediaAdminView(Media, db.session))
admin.add_view(CommentAdminView(Comment, db.session))
admin.add_view(MediaImageView(MediaImage, db.session))
admin.add_view(MediaTypeAdminView(MediaType, db.session))
admin.add_view(MediaCategoryAdminView(MediaCategory, db.session))
admin.add_view(RelatedMediaAdminView(RelatedMedia, db.session))

admin.add_link(MenuLink(name='Back to site', endpoint='media_bp.home'))
