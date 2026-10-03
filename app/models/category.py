from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), default="expense")  # 'expense' or 'income'
    color = db.Column(db.String(7), default="#0d6efd")  # Hex color for Chart.js
    icon = db.Column(db.String(30), default="bi-tag")   # Bootstrap icon class

    expenses = db.relationship("Expense", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "icon": self.icon,
        }

DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "type": "expense", "color": "#f59e0b", "icon": "bi-cup-hot"},
    {"name": "Books & Academics", "type": "expense", "color": "#3b82f6", "icon": "bi-book"},
    {"name": "Rent & Housing", "type": "expense", "color": "#8b5cf6", "icon": "bi-house-door"},
    {"name": "Transportation", "type": "expense", "color": "#10b981", "icon": "bi-bus-front"},
    {"name": "Entertainment", "type": "expense", "color": "#ec4899", "icon": "bi-controller"},
    {"name": "Utilities & Bills", "type": "expense", "color": "#6366f1", "icon": "bi-lightning-charge"},
    {"name": "Health & Personal", "type": "expense", "color": "#14b8a6", "icon": "bi-heart-pulse"},
    {"name": "Miscellaneous", "type": "expense", "color": "#64748b", "icon": "bi-three-dots"},
    {"name": "Income/Allowance", "type": "income", "color": "#22c55e", "icon": "bi-cash-coin"},
]

def seed_default_categories():
    """Seeds default global categories if none exist."""
    existing_count = Category.query.filter_by(user_id=None).count()
    if existing_count == 0:
        for cat in DEFAULT_CATEGORIES:
            db.session.add(Category(
                user_id=None,
                name=cat["name"],
                type=cat["type"],
                color=cat["color"],
                icon=cat["icon"]
            ))
        db.session.commit()
