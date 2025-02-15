import os
from datetime import datetime

from flask import redirect, url_for, current_app
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import ImageUploadField
from flask_admin.menu import MenuLink
from flask_login import current_user

from site_package.extensions import db
from site_package.models.media import Media, MediaType, MediaCategory, RelatedMedia, RelationCategory, MediaImage
from site_package.models.user import User


class AccessMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user_bp.login_page'))


class CustomAdminIndexView(AccessMixin, AdminIndexView):
    pass


class AdminModelView(AccessMixin, ModelView):
    pass


def get_upload_path():
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    return os.path.join(current_app.config['UPLOAD_FOLDER'], year, month)


class MediaImageView(AdminModelView):
    # Customizing the form to use ImageUploadField for image uploads
    form_overrides = {
        'image_path': ImageUploadField
    }

    form_args = {
        'image_path': {
            'label': 'Image',
            'base_path': get_upload_path,  # Define the folder where images will be saved
            'allow_overwrite': False
        }
    }


class MediaAdminView(AdminModelView):
    form_columns = ['name', 'alternative_name', 'release', 'description', 'grade', 'img', 'type', 'categories', 'user_list', 'comments', 'images', 'added']
    column_searchable_list = ['name', 'alternative_name', 'description']
    column_filters = ['type', 'categories']


admin = Admin(name='admin', index_view=CustomAdminIndexView(), template_mode='bootstrap4')

admin.add_view(AdminModelView(User, db.session))
admin.add_view(MediaAdminView(Media, db.session))
admin.add_view(MediaImageView(MediaImage, db.session))
admin.add_view(AdminModelView(MediaType, db.session))
admin.add_view(AdminModelView(MediaCategory, db.session))
admin.add_view(AdminModelView(RelatedMedia, db.session))
admin.add_view(AdminModelView(RelationCategory, db.session))

admin.add_link(MenuLink(name='Back to site', endpoint='media_bp.home'))
