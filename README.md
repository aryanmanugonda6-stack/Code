# Student Personal Finance & Expense Tracker (Phase 1 Prototype)

A modern, responsive web application built with **Flask**, **Bootstrap 5**, and **Chart.js** for college students to track expenses, set monthly budgets, and import bank statements.

---

## 🚀 Quick Start (Run in 3 Steps)

### 1. Open Terminal in this Folder
```bash
cd "C:\Users\aryan\OneDrive\Desktop\university\Code"
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
Open your browser at **http://127.0.0.1:5000**

---

## 🔑 Pre-Seeded Demo Account
The database auto-initializes on startup with default student categories and a pre-configured demo account:
* **Email:** `demo@student.edu`
* **Password:** `password123`

*(You can also click the **"Quick Fill Demo Account"** button on the login screen or register a new account).*

---

## 🌟 Key Features in this Prototype

1. **Financial Dashboard:**
   * 💳 **Total Spent** and Income summary cards.
   * 💰 **Budget Remaining** with real-time percentage progress bar.
   * ⚡ **Safe Daily Spend** burn-rate calculation based on days left in the month.
   * ⚠️ **Automatic Budget Alerts** (Warning at $\ge 80\%$, Critical alert at $\ge 100\%$).

2. **Quick Expense Logging:**
   * Click **"+ Add Expense"** to log transactions with amount, category dropdown, date, and description.

3. **Interactive Chart.js Visualizations:**
   * Live Doughnut chart dynamically showing spending distribution by category without refreshing the page.

4. **Semi-Automated Bank Statement Import:**
   * Click **"Import CSV"** $\rightarrow$ select the included `sample_bank_statement.csv`.
   * Click **"Parse & Auto-Categorize"**:
     * Merchant keyword engine automatically classifies *Chipotle* as *Food & Dining*, *Bookstore* as *Books & Academics*, *Uber* as *Transportation*, *Spectrum* as *Utilities*, etc.
     * Shows a preview table with editable category dropdowns and duplicate detection.
   * Click **"Confirm & Save Transactions"** to commit them into the database.

---

## 📁 Project Architecture & Structure

```text
Code/
├── app/
│   ├── __init__.py           # Application Factory & Auto-Bootstrap
│   ├── extensions.py         # SQLAlchemy, LoginManager, Bcrypt
│   ├── models/               # User, Category, Expense, Budget models
│   ├── routes/               # Auth, Dashboard, Expenses, Budgets, Importer blueprints
│   ├── services/             # Categorizer, Budget math, CSV parser services
│   ├── static/               # CSS & JavaScript (Fetch API + Chart.js)
│   └── templates/            # Jinja2 templates (Bootstrap 5)
├── sample_bank_statement.csv # Ready-to-use CSV sample for testing
├── config.py                 # App configurations
├── run.py                    # Server entry point
└── requirements.txt          # Python dependencies
```
