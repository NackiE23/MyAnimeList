from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user

from site_package.extensions import db
from site_package.models.media import Media, MediaType, MediaCategory, RelatedMedia, RelationCategory
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


class MediaAdminView(AdminModelView):
    form_columns = ['name', 'alternative_name', 'release', 'description', 'grade', 'img', 'type', 'categories', 'user_list', 'comments']


admin = Admin(name='admin', index_view=CustomAdminIndexView(), template_mode='bootstrap4')

admin.add_view(AdminModelView(User, db.session))
admin.add_view(MediaAdminView(Media, db.session))
admin.add_view(AdminModelView(MediaType, db.session))
admin.add_view(AdminModelView(MediaCategory, db.session))
admin.add_view(AdminModelView(RelatedMedia, db.session))
admin.add_view(AdminModelView(RelationCategory, db.session))

admin.add_link(MenuLink(name='Back to site', endpoint='media_bp.home'))
