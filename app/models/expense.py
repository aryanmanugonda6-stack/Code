from datetime import date, datetime
from app.extensions import db

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    expense_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    import_hash = db.Column(db.String(64), nullable=True, index=True)  # SHA-256 for duplicate detection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "Uncategorized",
            "category_type": self.category.type if self.category else "expense",
            "category_color": self.category.color if self.category else "#64748b",
            "category_icon": self.category.icon if self.category else "bi-tag",
            "amount": float(self.amount),
            "description": self.description or "",
            "expense_date": self.expense_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
