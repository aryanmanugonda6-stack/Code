import calendar
from datetime import date
from app.services.budget_service import calculate_monthly_summary
from app.services.analytics_service import calculate_historical_trends
from app.models.expense import Expense

def generate_ai_insights(user_id: int, year: int, month: int) -> dict:
    """
    Generates intelligent, actionable financial insights and a student financial health score.
    Analyzes spending velocity, category spikes, subscription anomalies, and month-over-month comparisons.
    """
    summary = calculate_monthly_summary(user_id, year, month)
    today = date.today()
    days_in_month = calendar.monthrange(year, month)[1]
    
    current_day = today.day if (year == today.year and month == today.month) else days_in_month
    month_progress_pct = round((current_day / days_in_month) * 100, 1)

    insights = []
    health_score = 85  # Base healthy score out of 100

    total_spent = summary["total_spent"]
    budget_limit = summary["budget_limit"]
    utilization_pct = summary["utilization_pct"]
    categories = summary["categories"]

    # 1. Spending Velocity Analysis
    if budget_limit > 0:
        if utilization_pct > month_progress_pct + 15:
            burn_difference = round(utilization_pct - month_progress_pct, 1)
            projected_days_left = max(1, int((summary["remaining_budget"] / (total_spent / max(1, current_day)))))
            health_score -= 20
            insights.append({
                "type": "warning",
                "badge": "Velocity Warning",
                "icon": "bi-speedometer2",
                "color": "#ef4444",
                "title": "Spending Velocity is Running Ahead of Schedule",
                "detail": f"You're {month_progress_pct}% through the month, but have already consumed {utilization_pct}% of your budget (+{burn_difference}% faster than safe pace). At this rate, your budget will run out in ~{projected_days_left} days.",
                "action": f"Recommended adjustment: Cap daily spend to ${summary['safe_daily_spend']:.2f}/day."
            })
        elif utilization_pct <= month_progress_pct:
            health_score += 5
            insights.append({
                "type": "positive",
                "badge": "Pace On Track",
                "icon": "bi-check-circle-fill",
                "color": "#10b981",
                "title": "Pacing Within Safe Thresholds",
                "detail": f"Great discipline! You have utilized {utilization_pct}% of your budget while {month_progress_pct}% of the month has passed. You are on track to save this month.",
                "action": "Keep this cadence to build your emergency savings buffer."
            })

    # 2. Dominant Category Spike Analysis
    if categories and total_spent > 0:
        top_cat = categories[0]
        cat_pct = round((top_cat["total"] / total_spent) * 100, 1)
        if cat_pct >= 40:
            health_score -= 10
            insights.append({
                "type": "opportunity",
                "badge": "Category Concentration",
                "icon": "bi-pie-chart-fill",
                "color": "#f59e0b",
                "title": f"High Concentration in {top_cat['name']}",
                "detail": f"{top_cat['name']} accounts for {cat_pct}% (${top_cat['total']:.2f}) of your total monthly expenditures.",
                "action": "Meal prepping or utilizing campus dining discounts can trim this category by 15-20%."
            })

    # 3. Subscription & Recurring Expense Detection
    recent_expenses = Expense.query.filter_by(user_id=user_id).all()
    sub_keywords = ["netflix", "spotify", "hulu", "disney", "prime", "chegg", "gym"]
    detected_subs = []
    for exp in recent_expenses:
        desc_lower = (exp.description or "").lower()
        for kw in sub_keywords:
            if kw in desc_lower and kw not in [s["name"] for s in detected_subs]:
                detected_subs.append({"name": kw.title(), "amount": float(exp.amount)})

    if detected_subs:
        sub_names = ", ".join([s["name"] for s in detected_subs])
        insights.append({
            "type": "tip",
            "badge": "Student Perks",
            "icon": "bi-stars",
            "color": "#3b82f6",
            "title": "Unlock Student Subscription Rates",
            "detail": f"Detected digital recurring items ({sub_names}). Many student plans offer 50% discounts (e.g. Spotify Student + Hulu bundle, Prime Student, or GitHub Student Pack).",
            "action": "Verify your .edu email on these accounts to save up to $15–$25 monthly."
        })

    # 4. Month-over-Month Trend Insight
    trends = calculate_historical_trends(user_id, months_back=2)
    if len(trends) >= 2:
        last_month = trends[0]["expenses"]
        curr_month = trends[1]["expenses"]
        if last_month > 0:
            diff = curr_month - last_month
            diff_pct = round((abs(diff) / last_month) * 100, 1)
            if diff > 0 and diff_pct >= 15:
                insights.append({
                    "type": "warning",
                    "badge": "Trend Alert",
                    "icon": "bi-graph-up-arrow",
                    "color": "#f97316",
                    "title": f"Spending Increased by {diff_pct}% Compared to Last Month",
                    "detail": f"You've spent ${diff:.2f} more than this time last month (${last_month:.2f} vs ${curr_month:.2f}).",
                    "action": "Review your recent transactions to pinpoint unplanned purchases."
                })
            elif diff < 0 and diff_pct >= 10:
                health_score += 10
                insights.append({
                    "type": "positive",
                    "badge": "Saving Trend",
                    "icon": "bi-piggy-bank-fill",
                    "color": "#10b981",
                    "title": f"Spending Down by {diff_pct}% vs Last Month",
                    "detail": f"You are currently spending less than last month! Outstanding progress towards your financial goals.",
                    "action": "Consider depositing the surplus into a high-yield student savings account."
                })

    # Default Student Financial Health Tip if list is short
    if len(insights) < 2:
        insights.append({
            "type": "tip",
            "badge": "Smart Rule",
            "icon": "bi-lightbulb-fill",
            "color": "#6366f1",
            "title": "The Student 50/30/20 Rule",
            "detail": "Allocate 50% of your allowance to Needs (rent, books, groceries), 30% to Wants (dining, hobbies), and 20% to Savings or debt relief.",
            "action": "Use our 'Set Budget' tool to establish separate target thresholds."
        })

    # Clamp health score between 30 and 100
    final_score = max(30, min(100, health_score))

    return {
        "period": f"{year}-{month:02d}",
        "health_score": final_score,
        "health_label": "Excellent" if final_score >= 85 else ("Good" if final_score >= 70 else "Needs Attention"),
        "insights": insights
    }
