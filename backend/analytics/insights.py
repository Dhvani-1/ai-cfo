from collections import defaultdict

def generate_insights(transactions):
    """
    Generates structured financial indicators and textual insights based on transactions.
    """
    if not transactions:
        return {
            "financial_status": "neutral",
            "largest_category": None,
            "largest_category_percentage": 0.0,
            "insights": ["No transaction records found."]
        }

    total_income = sum(t.amount for t in transactions if t.type == "Income" or t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == "Expense" or t.amount < 0)

    # 1. Financial Status
    net = total_income - total_expenses
    if net > 0:
        financial_status = "positive_cashflow"
    elif net < 0:
        financial_status = "negative_cashflow"
    else:
        financial_status = "neutral"

    # 2. Category spending
    cat_spend = defaultdict(float)
    for t in transactions:
        if t.type == "Expense" or t.amount < 0:
            cat_spend[t.category] += abs(t.amount)

    insights_list = []

    # Net cash flow insight
    if financial_status == "positive_cashflow":
        insights_list.append("Net cash flow is positive.")
    elif financial_status == "negative_cashflow":
        insights_list.append("Net cash flow is negative.")
    else:
        insights_list.append("Net cash flow is neutral.")

    if not cat_spend:
        return {
            "financial_status": financial_status,
            "largest_category": None,
            "largest_category_percentage": 0.0,
            "insights": insights_list + ["No expenses recorded."]
        }

    # Sort categories by total spending descending
    sorted_cats = sorted(cat_spend.items(), key=lambda x: x[1], reverse=True)
    largest_category = sorted_cats[0][0]
    largest_category_spend = sorted_cats[0][1]

    largest_category_percentage = round((largest_category_spend / total_expenses) * 100, 2) if total_expenses > 0 else 0.0

    insights_list.append(f"{largest_category} is the largest expense category.")

    if len(sorted_cats) > 1:
        second_category = sorted_cats[1][0]
        insights_list.append(f"{second_category} is the second-largest category.")

    insights_list.append(f"{largest_category} represents {largest_category_percentage}% of total expenses.")

    return {
        "financial_status": financial_status,
        "largest_category": largest_category,
        "largest_category_percentage": largest_category_percentage,
        "insights": insights_list
    }
