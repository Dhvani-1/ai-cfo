from analytics.ratios import calculate_expense_ratio, calculate_savings_ratio
from analytics.forecast import calculate_cash_runway

def analyze_risk(transactions):
    """
    Classifies risk as "low", "medium", or "high" and lists specific reasons.
    """
    expense_ratio = calculate_expense_ratio(transactions)
    savings_ratio = calculate_savings_ratio(transactions)

    runway_info = calculate_cash_runway(transactions)
    runway_months = runway_info["months_remaining"]
    runway_status = runway_info["status"]

    reasons = []

    if expense_ratio > 70.0:
        reasons.append("Expense ratio exceeds 70%")
    elif expense_ratio > 50.0:
        reasons.append("Expense ratio is elevated (exceeds 50%)")

    if savings_ratio < 20.0:
        reasons.append("Savings ratio below 20%")
    elif savings_ratio < 10.0:
        reasons.append("Savings ratio is critically low (below 10%)")

    if runway_status == "burn_rate_active":
        if runway_months is not None:
            if runway_months < 3.0:
                reasons.append(f"Cash runway is critically short ({runway_months} months remaining)")
            elif runway_months < 6.0:
                reasons.append(f"Cash runway is low ({runway_months} months remaining)")

    # Classification logic
    if expense_ratio > 70.0 or savings_ratio < 10.0 or (runway_status == "burn_rate_active" and runway_months is not None and runway_months < 3.0):
        risk_level = "high"
        risk_score = 80
        risk_desc = "High financial risk"
    elif expense_ratio > 50.0 or savings_ratio < 20.0 or (runway_status == "burn_rate_active" and runway_months is not None and runway_months < 6.0):
        risk_level = "medium"
        risk_score = 50
        risk_desc = "Moderate financial risk"
    else:
        risk_level = "low"
        risk_score = 20
        risk_desc = "Low financial risk"

    if not reasons:
        reasons.append("Expense ratio is stable and well within standard bounds.")
        reasons.append("Savings ratio is strong.")

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "description": risk_desc,
        "reasons": reasons
    }
