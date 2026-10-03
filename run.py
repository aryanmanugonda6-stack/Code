import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Student Personal Finance Application (Phase 1 Prototype)")
    print("  Default Demo Account:")
    print("  Email:    demo@student.edu")
    print("  Password: password123")
    print("  Access at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
