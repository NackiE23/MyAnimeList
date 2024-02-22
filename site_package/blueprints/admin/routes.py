from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route("/", methods=["GET"])
def index():
    return "Admin page"
