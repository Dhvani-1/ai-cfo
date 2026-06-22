def calculate_cashflow(transactions):

    income = sum(
        t.amount
        for t in transactions
        if t.type == "Income"
    )

    expenses = abs(sum(
        t.amount
        for t in transactions
        if t.type == "Expense"
    ))

    net = income - expenses

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "net_cashflow": round(net, 2)
    }