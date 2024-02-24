from flask import Blueprint, render_template, abort

from site_package.models.media import Media, MediaType, MediaCategory, RelatedMedia, RelationCategory
from site_package.models.user import User

admin_bp = Blueprint('admin_bp', __name__)

models = [
    # (Model, *order_by field*)
    (User, 'name'),
    (Media, 'name'),
    (MediaType, 'name'),
    (MediaCategory, 'name'),
    (RelatedMedia, 'id'),
    (RelationCategory, 'name')
]


@admin_bp.route("/", methods=["GET"])
def main():
    context = {
        "models": models,
    }

    return render_template("admin/base.html", **context)


@admin_bp.route("/<model_name>", methods=["GET"])
def model_info(model_name):
    for model, order_by in models:
        if model_name.lower() == model.__name__.lower():
            current_model = (model, order_by)
            break
    else:
        abort(404)

    context = {
        "models": models,
        "current_model": current_model,
    }

    return render_template("admin/base.html", **context)
