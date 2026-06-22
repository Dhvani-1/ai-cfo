def calculate_savings_ratio(transactions):
    """
    Computes savings ratio percentage: ((income - expenses) / income) * 100
    """
    total_income = sum(t.amount for t in transactions if t.type == "Income" or t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == "Expense" or t.amount < 0)

    if total_income <= 0:
        return 0.0

    savings_ratio = ((total_income - total_expenses) / total_income) * 100
    return round(savings_ratio, 2)

def calculate_expense_ratio(transactions):
    """
    Computes expense ratio percentage: (expenses / income) * 100
    """
    total_income = sum(t.amount for t in transactions if t.type == "Income" or t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.type == "Expense" or t.amount < 0)

    if total_income <= 0:
        return 0.0

    expense_ratio = (total_expenses / total_income) * 100
    return round(expense_ratio, 2)
