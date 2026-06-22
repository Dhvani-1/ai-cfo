def estimate_tax(transactions):
    if not transactions:
        return {
            "income": 0.0,
            "expenses": 0.0,
            "taxable_income": 0.0,
            "expense_ratio": 0.0
        }
        
    income = sum(t.amount for t in transactions if t.amount >= 0)
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    taxable_income = income - expenses
    expense_ratio = round((expenses / income) * 100.0, 2) if income > 0 else 0.0
    
    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "taxable_income": round(taxable_income, 2),
        "expense_ratio": expense_ratio
    }

def generate_tax_insights(transactions):
    estimate = estimate_tax(transactions)
    taxable_income = estimate["taxable_income"]
    
    if taxable_income > 0:
        tax_status = "positive_income"
    elif taxable_income == 0:
        tax_status = "neutral"
    else:
        tax_status = "negative_income"
        
    # Determine largest expense category
    from collections import defaultdict
    categories = defaultdict(float)
    for t in transactions:
        if t.amount < 0:
            categories[t.category or "Others"] += abs(t.amount)
            
    largest_expense_category = None
    if categories:
        largest_expense_category = max(categories, key=categories.get)
        
    insights = []
    if taxable_income > 0:
        insights.append("Taxable income is positive.")
    else:
        insights.append("Taxable income is neutral or negative.")
        
    if largest_expense_category:
        insights.append(f"{largest_expense_category} represents the largest expense category.")
        
    income = estimate["income"]
    expenses = estimate["expenses"]
    if income > 0 and (expenses / income) > 0.70:
        insights.append("Expenses represent a high portion of your income.")
        
    return {
        "tax_status": tax_status,
        "largest_expense_category": largest_expense_category,
        "insights": insights
    }
