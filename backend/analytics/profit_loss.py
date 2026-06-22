def profit_loss(transactions):

    income = sum(
        t.amount
        for t in transactions
        if t.amount > 0
    )

    expense = abs(sum(
        t.amount
        for t in transactions
        if t.amount < 0
    ))

    return {
        "revenue": round(income, 2),
        "expenses": round(expense, 2),
        "profit": round(income-expense, 2),
        "net_profit": round(income-expense, 2)
    }