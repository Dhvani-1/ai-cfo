from collections import defaultdict

def get_monthly_summary(transactions, month=None):
    """
    Groups transactions by month ("YYYY-MM"). For each month, calculates
    income, expenses, profit, and identifies the largest expense category.
    Supports filtering by a specific month string.
    """
    monthly_data = defaultdict(lambda: {"income": 0.0, "expenses": 0.0, "categories": defaultdict(float)})

    for t in transactions:
        if not t.date:
            continue

        m_str = t.date.strftime("%Y-%m")

        if month is not None and m_str != month:
            continue

        if t.type == "Income" or t.amount > 0:
            monthly_data[m_str]["income"] += t.amount
        elif t.type == "Expense" or t.amount < 0:
            monthly_data[m_str]["expenses"] += abs(t.amount)
            monthly_data[m_str]["categories"][t.category] += abs(t.amount)

    summary = {}
    for m, data in monthly_data.items():
        largest_cat = None
        max_spend = 0.0
        for cat, spend in data["categories"].items():
            if spend > max_spend:
                max_spend = spend
                largest_cat = cat

        summary[m] = {
            "income": round(data["income"], 2),
            "expenses": round(data["expenses"], 2),
            "profit": round(data["income"] - data["expenses"], 2),
            "largest_category": largest_cat
        }

    if month is not None:
        return summary.get(month, {
            "income": 0.0,
            "expenses": 0.0,
            "profit": 0.0,
            "largest_category": None
        })

    return summary


def get_top_expenses(transactions, limit=5):
    """
    Returns the top N highest expense transactions, sorted by absolute amount descending.
    """
    expenses = [t for t in transactions if t.type == "Expense" or t.amount < 0]
    sorted_expenses = sorted(expenses, key=lambda x: abs(x.amount), reverse=True)

    result = []
    for t in sorted_expenses[:limit]:
        result.append({
            "id": t.id,
            "date": t.date.isoformat() if t.date else None,
            "description": t.description,
            "amount": round(t.amount, 2),
            "category": t.category,
            "type": t.type
        })
    return result


def get_top_income(transactions, limit=5):
    """
    Returns the top N highest income transactions, sorted descending by amount.
    """
    income = [t for t in transactions if t.type == "Income" or t.amount > 0]
    sorted_income = sorted(income, key=lambda x: x.amount, reverse=True)

    result = []
    for t in sorted_income[:limit]:
        result.append({
            "id": t.id,
            "date": t.date.isoformat() if t.date else None,
            "description": t.description,
            "amount": round(t.amount, 2),
            "category": t.category,
            "type": t.type
        })
    return result


def get_category_ranking(transactions):
    """
    Ranks categories by total spending descending and includes metadata.
    """
    cat_spend = defaultdict(float)
    total_expenses = 0.0

    for t in transactions:
        if t.type == "Expense" or t.amount < 0:
            cat_spend[t.category] += abs(t.amount)
            total_expenses += abs(t.amount)

    sorted_ranking = sorted(cat_spend.items(), key=lambda x: x[1], reverse=True)

    categories = []
    for cat, spend in sorted_ranking:
        percentage = (spend / total_expenses * 100) if total_expenses > 0 else 0.0
        categories.append({
            "category": cat,
            "amount": round(spend, 2),
            "percentage": round(percentage, 2)
        })

    return {
        "total_expenses": round(total_expenses, 2),
        "categories": categories
    }
