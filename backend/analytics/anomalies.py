import math

def get_anomalies(transactions):
    """
    Detects abnormal transactions using standard deviation (mean + 2*std_dev).
    Returns list of outlier expenses with their threshold and deviation details.
    """
    # Filter only expenses (negative amounts)
    expenses = [t for t in transactions if t.type == "Expense" or t.amount < 0]
    if len(expenses) < 2:
        # Standard deviation requires at least 2 data points
        return []

    amounts = [abs(t.amount) for t in expenses]
    mean = sum(amounts) / len(amounts)

    # Variance and standard deviation calculation
    variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
    std_dev = math.sqrt(variance)

    threshold = mean + 2 * std_dev

    anomalies = []
    for t in expenses:
        abs_amt = abs(t.amount)
        if abs_amt > threshold:
            anomalies.append({
                "id": t.id,
                "date": t.date.isoformat() if t.date else None,
                "description": t.description,
                "amount": round(t.amount, 2),
                "category": t.category,
                "type": t.type,
                "threshold": round(threshold, 2),
                "deviation": round(abs_amt - threshold, 2)
            })

    return anomalies
