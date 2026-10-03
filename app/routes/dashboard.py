from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.category import Category

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    today = date.today()
    categories = Category.query.all()
    return render_template(
        "dashboard.html",
        user=current_user,
        today=today,
        categories=categories,
    )
