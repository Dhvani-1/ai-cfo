from collections import defaultdict

def category_summary(transactions):

    summary = defaultdict(float)

    for t in transactions:

        if t.amount < 0:

            summary[t.category] += abs(t.amount)

    return {cat: round(amt, 2) for cat, amt in summary.items()}