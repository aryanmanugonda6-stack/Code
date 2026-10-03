import os
from flask import Flask
from config import config_by_name
from app.extensions import db, login_manager, bcrypt

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.expenses import expenses_bp
    from app.routes.budgets import budgets_bp
    from app.routes.importer import importer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(importer_bp)

    # Database bootstrap (tables, default categories, and demo user for prototype)
    with app.app_context():
        from app.models import User, Category, Expense, Budget, seed_default_categories
        db.create_all()
        seed_default_categories()

        # Seed demo user if no users exist
        if User.query.count() == 0:
            demo_user = User(
                name="Alex Student",
                email="demo@student.edu",
                currency="$"
            )
            demo_user.set_password("password123")
            db.session.add(demo_user)
            db.session.commit()

            # Add sample budget and initial sample expense for demo
            from datetime import date
            today = date.today()
            sample_budget = Budget(
                user_id=demo_user.id,
                year=today.year,
                month=today.month,
                amount_limit=650.00
            )
            db.session.add(sample_budget)

            food_cat = Category.query.filter_by(name="Food & Dining").first()
            book_cat = Category.query.filter_by(name="Books & Academics").first()
            if food_cat:
                db.session.add(Expense(
                    user_id=demo_user.id,
                    category_id=food_cat.id,
                    amount=14.50,
                    expense_date=today,
                    description="Campus Dining Hall Lunch"
                ))
            if book_cat:
                db.session.add(Expense(
                    user_id=demo_user.id,
                    category_id=book_cat.id,
                    amount=65.00,
                    expense_date=today,
                    description="Calculus Textbook"
                ))
            db.session.commit()

    return app
