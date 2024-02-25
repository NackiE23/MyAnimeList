from flask import Blueprint, render_template, abort

from site_package.models.media import Media, MediaType, MediaCategory, RelatedMedia, RelationCategory
from site_package.models.user import User

from .control import Admin, AdminModel

admin_bp = Blueprint('admin_bp', __name__)
admin = Admin()
admin.add_models([
    AdminModel(User, 'name'),
    AdminModel(Media, 'name'),
    AdminModel(MediaType, 'name'),
    AdminModel(MediaCategory, 'name'),
    AdminModel(RelatedMedia, 'id'),
    AdminModel(RelationCategory, 'name'),
])


@admin_bp.route("/", methods=["GET"])
def main():
    context = {
        "admin": admin,
    }

    return render_template("admin/base.html", **context)


@admin_bp.route("/<model_name>", methods=["GET"])
def model_info(model_name):
    current_model = admin.get_model_by_name(model_name)
    if not current_model:
        abort(404)

    context = {
        "admin": admin,
        "current_model": current_model,
    }

    return render_template("admin/base.html", **context)
