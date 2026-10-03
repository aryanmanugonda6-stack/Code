KEYWORD_RULES = {
    "Food & Dining": [
        "chipotle", "mcdonald", "subway", "starbucks", "dunkin", "cafe", "coffee",
        "pizza", "dining", "doordash", "ubereats", "grocery", "trader joe", "kroger",
        "whole foods", "burger", "taco", "restaurant", "canteen", "cafeteria"
    ],
    "Books & Academics": [
        "bookstore", "chegg", "pearson", "quizlet", "canvas", "library", "tuition",
        "textbook", "barnes & noble", "course", "lab fee", "udemy", "coursera"
    ],
    "Rent & Housing": [
        "rent", "apartments", "housing", "dorm", "residence", "landlord", "lease"
    ],
    "Transportation": [
        "uber", "lyft", "transit", "metro", "bus", "subway", "shell", "chevron",
        "exxon", "gas", "fuel", "parking", "train", "amtrak", "scooter"
    ],
    "Entertainment": [
        "netflix", "spotify", "hulu", "steam", "playstation", "xbox", "cinema",
        "amc", "disney", "movie", "concert", "game"
    ],
    "Utilities & Bills": [
        "electric", "water", "wifi", "internet", "spectrum", "verizon", "t-mobile",
        "at&t", "coned", "utility", "phone"
    ],
    "Health & Personal": [
        "cvs", "walgreens", "pharmacy", "gym", "fitness", "doctor", "health",
        "barber", "salon", "dental"
    ],
    "Income/Allowance": [
        "payroll", "direct dep", "stipend", "zelle from", "financial aid",
        "scholarship", "refund", "deposit", "salary", "allowance"
    ],
}

def predict_category_name(description: str, amount: float = 0.0) -> str:
    """Predicts category name based on transaction description text and amount."""
    if not description:
        return "Income/Allowance" if amount > 0 else "Miscellaneous"

    desc_lower = description.lower()

    # Positive amounts or payroll indicators default to income
    if amount > 0 or any(k in desc_lower for k in ["payroll", "direct dep", "stipend", "scholarship"]):
        return "Income/Allowance"

    # Match merchant keywords
    for category_name, keywords in KEYWORD_RULES.items():
        if category_name == "Income/Allowance":
            continue
        for kw in keywords:
            if kw in desc_lower:
                return category_name

    return "Miscellaneous"
