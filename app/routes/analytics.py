from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.analytics_service import calculate_historical_trends
from app.services.insights_service import generate_ai_insights

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/trends", methods=["GET"])
@login_required
def get_trends():
    months = int(request.args.get("months", 6))
    data = calculate_historical_trends(current_user.id, months_back=months)
    return jsonify(data)

@analytics_bp.route("/insights", methods=["GET"])
@login_required
def get_insights():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    data = generate_ai_insights(current_user.id, year, month)
    return jsonify(data)
