from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.budget import Budget

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")

@budgets_bp.route("", methods=["POST"])
@login_required
def set_budget():
    data = request.get_json() or {}
    try:
        today = date.today()
        year = int(data.get("year", today.year))
        month = int(data.get("month", today.month))
        amount = float(data.get("amount", 0))

        if amount <= 0:
            return jsonify({"error": "Budget limit must be greater than zero."}), 400

        budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=None,
            year=year,
            month=month,
        ).first()

        if budget:
            budget.amount_limit = amount
        else:
            budget = Budget(
                user_id=current_user.id,
                category_id=None,
                year=year,
                month=month,
                amount_limit=amount,
            )
            db.session.add(budget)

        db.session.commit()
        return jsonify(budget.to_dict()), 200
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
