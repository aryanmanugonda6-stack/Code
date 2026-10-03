import csv
import io
import hashlib
from datetime import datetime
from app.models.category import Category
from app.models.expense import Expense
from app.services.categorizer_service import predict_category_name

def generate_transaction_hash(user_id: int, date_str: str, amount: float, description: str) -> str:
    """Generates SHA-256 hash for transaction deduplication."""
    content = f"{user_id}:{date_str}:{amount:.2f}:{description.strip().lower()}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def clean_amount(val_str: str) -> float:
    """Parses amount string safely (e.g. '$12.50', '-$14.20', '(25.00)')."""
    val = val_str.strip().replace("$", "").replace(",", "")
    if val.startswith("(") and val.endswith(")"):
        val = "-" + val[1:-1]
    return float(val)

def parse_bank_csv(file_stream, user_id: int) -> dict:
    """
    Parses bank CSV stream, predicts categories, and flags existing duplicates.
    Returns: {"rows": [...], "total_count": int, "duplicates_count": int}
    """
    stream = io.StringIO(file_stream.read().decode("utf-8", errors="ignore"))
    reader = csv.reader(stream)

    header = next(reader, None)
    if not header:
        return {"rows": [], "total_count": 0, "duplicates_count": 0}

    # Normalize header names
    header_lower = [h.strip().lower() for h in header]

    # Find column indices
    date_idx = -1
    desc_idx = -1
    amount_idx = -1

    for idx, col in enumerate(header_lower):
        if any(term in col for term in ["date", "time"]):
            if date_idx == -1:
                date_idx = idx
        elif any(term in col for term in ["desc", "merchant", "payee", "detail", "name"]):
            if desc_idx == -1:
                desc_idx = idx
        elif any(term in col for term in ["amount", "total", "debit"]):
            if amount_idx == -1:
                amount_idx = idx

    # Fallbacks if columns weren't cleanly labeled
    if date_idx == -1: date_idx = 0
    if desc_idx == -1: desc_idx = 1
    if amount_idx == -1: amount_idx = 2

    # Fetch all categories to map predicted name to Category object
    categories = Category.query.all()
    cat_by_name = {c.name.lower(): c for c in categories}
    default_cat = cat_by_name.get("miscellaneous") or (categories[0] if categories else None)

    # Fetch existing transaction hashes for this user to check duplicates
    existing_hashes = set(
        h[0] for h in Expense.query.with_entities(Expense.import_hash)
        .filter(Expense.user_id == user_id, Expense.import_hash.isnot(None))
        .all()
    )

    parsed_rows = []
    duplicates_count = 0

    for row_num, row in enumerate(reader, start=2):
        if not row or len(row) <= max(date_idx, desc_idx, amount_idx):
            continue

        raw_date = row[date_idx].strip()
        raw_desc = row[desc_idx].strip()
        raw_amount = row[amount_idx].strip()

        if not raw_date or not raw_amount:
            continue

        try:
            # Handle negative bank debits vs positive credits
            parsed_amt = clean_amount(raw_amount)
            # Standardize: expenses are positive amounts, income is positive under income category
            abs_amount = abs(parsed_amt)
            if abs_amount == 0:
                continue

            # Standardize date format (try common formats)
            formatted_date = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    formatted_date = datetime.strptime(raw_date, fmt).date().isoformat()
                    break
                except ValueError:
                    continue

            if not formatted_date:
                formatted_date = datetime.utcnow().date().isoformat()

            predicted_cat_name = predict_category_name(raw_desc, parsed_amt)
            matched_cat = cat_by_name.get(predicted_cat_name.lower(), default_cat)

            tx_hash = generate_transaction_hash(user_id, formatted_date, abs_amount, raw_desc)
            is_duplicate = tx_hash in existing_hashes

            if is_duplicate:
                duplicates_count += 1

            parsed_rows.append({
                "row_id": row_num,
                "date": formatted_date,
                "description": raw_desc,
                "amount": round(abs_amount, 2),
                "suggested_category_id": matched_cat.id if matched_cat else 1,
                "suggested_category_name": matched_cat.name if matched_cat else "Miscellaneous",
                "is_duplicate": is_duplicate,
                "import_hash": tx_hash,
            })
        except Exception:
            continue

    return {
        "rows": parsed_rows,
        "total_count": len(parsed_rows),
        "duplicates_count": duplicates_count,
    }
