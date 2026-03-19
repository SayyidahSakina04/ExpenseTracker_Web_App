from flask import Flask, render_template, request, redirect, url_for
from expense import Expense
import calendar
import datetime as dt
import os

app = Flask(__name__)
expense_file = "expenses.csv"
total_budget = 30000

expense_categories = ["Food", "Home", "Work", "Fun", "Other"]

# Helper function to save expenses
def save_to_file(expense: Expense):
    with open(expense_file, "a") as f:
        f.write(f"{expense.name},{expense.amount},{expense.category}\n")

# Helper function to read expenses
def read_expenses():
    expenses = []
    if os.path.exists(expense_file):
        with open(expense_file, "r") as f:
            for line in f.readlines():
                exName, exAmount, exCategory = line.strip().split(",")
                expenses.append(Expense(exName, exCategory, float(exAmount)))
    return expenses

# Helper function for summary
def get_summary(expenses):
    amount_by_category = {}
    for expense in expenses:
        amount_by_category[expense.category] = amount_by_category.get(expense.category, 0) + expense.amount

    total_spent = sum(ex.amount for ex in expenses)
    remaining_budget = total_budget - total_spent

    now = dt.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0

    return amount_by_category, total_spent, remaining_budget, daily_budget

# ----- Routes -----
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        expense = Expense(name, category, amount)
        save_to_file(expense)
        return redirect(url_for("index"))

    expenses = read_expenses()
    summary = get_summary(expenses)
    return render_template("index.html", categories=expense_categories, summary=summary)

@app.route("/full_budget")
def full_budget():
    expenses = read_expenses()
    summary = get_summary(expenses)
    return render_template("full_budget.html", expenses=expenses, summary=summary)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
