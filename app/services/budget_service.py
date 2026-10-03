import calendar
from datetime import date
from sqlalchemy import func, extract
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category
from app.models.budget import Budget

def calculate_monthly_summary(user_id: int, year: int, month: int) -> dict:
    """Calculates all metrics for the student dashboard for a specific month."""
    today = date.today()

    # 1. Total spent this month (Expenses only, exclude Income/Allowance)
    total_spent_query = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .join(Category, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Category.type == "expense",
            extract("year", Expense.expense_date) == year,
            extract("month", Expense.expense_date) == month,
        )
    )
    total_spent = float(total_spent_query.scalar() or 0.0)

    # 2. Total income this month
    total_income_query = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .join(Category, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Category.type == "income",
            extract("year", Expense.expense_date) == year,
            extract("month", Expense.expense_date) == month,
        )
    )
    total_income = float(total_income_query.scalar() or 0.0)

    # 3. Category-wise breakdown for Chart.js
    category_rows = (
        db.session.query(
            Category.id,
            Category.name,
            Category.color,
            Category.icon,
            func.sum(Expense.amount).label("total")
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Category.type == "expense",
            extract("year", Expense.expense_date) == year,
            extract("month", Expense.expense_date) == month,
        )
        .group_by(Category.id, Category.name, Category.color, Category.icon)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    categories_breakdown = [
        {
            "id": r.id,
            "name": r.name,
            "color": r.color,
            "icon": r.icon,
            "total": float(r.total),
        }
        for r in category_rows
    ]

    # 4. Budget limit
    budget = Budget.query.filter_by(
        user_id=user_id,
        year=year,
        month=month,
        category_id=None
    ).first()

    budget_limit = float(budget.amount_limit) if budget else 0.0
    remaining_budget = max(0.0, budget_limit - total_spent) if budget_limit > 0 else 0.0
    utilization_pct = round((total_spent / budget_limit * 100), 1) if budget_limit > 0 else 0.0

    # 5. Alert Level
    if budget_limit > 0 and total_spent >= budget_limit:
        alert_status = "critical"
        alert_message = f"Budget Exceeded! You have spent ${total_spent - budget_limit:.2f} over your limit."
    elif budget_limit > 0 and utilization_pct >= 80.0:
        alert_status = "warning"
        alert_message = f"Budget Alert: You have used {utilization_pct}% of your monthly budget."
    else:
        alert_status = "normal"
        alert_message = "Your spending is on track."

    # 6. Safe daily spend calculation
    days_in_month = calendar.monthrange(year, month)[1]
    if year == today.year and month == today.month:
        remaining_days = max(1, days_in_month - today.day + 1)
    elif date(year, month, 1) > today:
        remaining_days = days_in_month
    else:
        remaining_days = 1

    safe_daily_spend = round(remaining_budget / remaining_days, 2) if budget_limit > 0 else 0.0

    return {
        "period": f"{year}-{month:02d}",
        "year": year,
        "month": month,
        "total_spent": round(total_spent, 2),
        "total_income": round(total_income, 2),
        "budget_limit": round(budget_limit, 2),
        "remaining_budget": round(remaining_budget, 2),
        "utilization_pct": utilization_pct,
        "alert_status": alert_status,
        "alert_message": alert_message,
        "safe_daily_spend": safe_daily_spend,
        "remaining_days": remaining_days,
        "categories": categories_breakdown,
    }
