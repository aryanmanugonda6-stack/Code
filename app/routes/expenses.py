from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category
from app.services.budget_service import calculate_monthly_summary

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")

@expenses_bp.route("/summary", methods=["GET"])
@login_required
def get_summary():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    data = calculate_monthly_summary(current_user.id, year, month)
    return jsonify(data)

@expenses_bp.route("", methods=["GET"])
@login_required
def list_expenses():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    expenses = (
        Expense.query.filter(
            Expense.user_id == current_user.id,
            db.extract("year", Expense.expense_date) == year,
            db.extract("month", Expense.expense_date) == month,
        )
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .all()
    )
    return jsonify([e.to_dict() for e in expenses])

@expenses_bp.route("", methods=["POST"])
@login_required
def create_expense():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero."}), 400

        category_id = int(data.get("category_id"))
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Invalid category."}), 400

        expense_date_str = data.get("expense_date")
        expense_date = (
            datetime.strptime(expense_date_str, "%Y-%m-%d").date()
            if expense_date_str
            else date.today()
        )
        description = data.get("description", "").strip()

        expense = Expense(
            user_id=current_user.id,
            category_id=category_id,
            amount=amount,
            expense_date=expense_date,
            description=description,
        )
        db.session.add(expense)
        db.session.commit()

        return jsonify(expense.to_dict()), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True, "message": "Expense deleted."})
