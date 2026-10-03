from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category
from app.services.csv_parser_service import parse_bank_csv

importer_bp = Blueprint("importer", __name__, url_prefix="/api/import")

@importer_bp.route("/csv/preview", methods=["POST"])
@login_required
def preview_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only .csv files are supported."}), 400

    try:
        result = parse_bank_csv(file.stream, current_user.id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 500

@importer_bp.route("/csv/confirm", methods=["POST"])
@login_required
def confirm_import():
    data = request.get_json() or {}
    transactions = data.get("transactions", [])

    if not transactions:
        return jsonify({"error": "No transactions provided."}), 400

    created_expenses = []
    skipped_count = 0

    try:
        for tx in transactions:
            # Skip if user unchecked duplicate or opted out
            if tx.get("skip", False):
                skipped_count += 1
                continue

            amt = float(tx.get("amount", 0))
            if amt <= 0:
                continue

            cat_id = int(tx.get("category_id"))
            date_obj = datetime.strptime(tx.get("date"), "%Y-%m-%d").date()
            desc = tx.get("description", "").strip()
            tx_hash = tx.get("import_hash")

            expense = Expense(
                user_id=current_user.id,
                category_id=cat_id,
                amount=amt,
                expense_date=date_obj,
                description=desc,
                import_hash=tx_hash,
            )
            db.session.add(expense)
            created_expenses.append(expense)

        db.session.commit()

        return jsonify({
            "success": True,
            "imported_count": len(created_expenses),
            "skipped_count": skipped_count,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save transactions: {str(e)}"}), 500
