from datetime import datetime
from app.extensions import db

class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 to 12
    amount_limit = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to category
    category = db.relationship("Category", backref="budgets", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "category_id", "year", "month", name="uq_user_cat_year_month"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "Overall Monthly",
            "year": self.year,
            "month": self.month,
            "amount_limit": float(self.amount_limit),
        }
