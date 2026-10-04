from datetime import date
from sqlalchemy import func, extract
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category

def calculate_historical_trends(user_id: int, months_back: int = 6) -> list:
    """
    Computes monthly expense and income totals for the past N months using standard library only.
    Returns: [{"label": "May 2026", "year": 2026, "month": 5, "expenses": 320.0, "income": 450.0}, ...]
    """
    today = date.today()
    trends = []

    # Iterate from (months_back - 1) months ago up to current month
    for i in range(months_back - 1, -1, -1):
        # Calculate year and month using standard math
        total_months = today.year * 12 + today.month - 1 - i
        target_year = total_months // 12
        target_month = (total_months % 12) + 1
        month_label = date(target_year, target_month, 1).strftime("%b %Y")

        # Query total expenses for this month
        exp_total = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0))
            .join(Category, Expense.category_id == Category.id)
            .filter(
                Expense.user_id == user_id,
                Category.type == "expense",
                extract("year", Expense.expense_date) == target_year,
                extract("month", Expense.expense_date) == target_month,
            )
            .scalar()
        )

        # Query total income for this month
        inc_total = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0))
            .join(Category, Expense.category_id == Category.id)
            .filter(
                Expense.user_id == user_id,
                Category.type == "income",
                extract("year", Expense.expense_date) == target_year,
                extract("month", Expense.expense_date) == target_month,
            )
            .scalar()
        )

        trends.append({
            "label": month_label,
            "year": target_year,
            "month": target_month,
            "expenses": round(float(exp_total or 0.0), 2),
            "income": round(float(inc_total or 0.0), 2),
        })

    return trends
