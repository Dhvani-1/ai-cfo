from analytics.ratios import calculate_savings_ratio, calculate_expense_ratio
from analytics.risk_analysis import analyze_risk
from analytics.forecast import calculate_cash_runway

def calculate_health_score(transactions):
    """
    Computes a weighted multi-factor financial health score from 0 to 100.
    Returns the overall score and the components breakdown (raw and weighted).
    """
    savings_ratio = calculate_savings_ratio(transactions)
    expense_ratio = calculate_expense_ratio(transactions)

    risk_info = analyze_risk(transactions)
    risk_level = risk_info["risk_level"]

    runway_info = calculate_cash_runway(transactions)
    runway_status = runway_info["status"]

    if runway_status == "cashflow_positive":
        cashflow_status = "positive_cashflow"
    elif not transactions:
        cashflow_status = "neutral"
    else:
        cashflow_status = "negative_cashflow"

    risk_component_val = {
        "low": 100,
        "medium": 70,
        "high": 40
    }[risk_level]

    cashflow_component_val = {
        "positive_cashflow": 100,
        "neutral": 60,
        "negative_cashflow": 20
    }[cashflow_status]

    savings_ratio_score = savings_ratio * 0.4
    expense_ratio_score = (100.0 - expense_ratio) * 0.3
    risk_score_component = risk_component_val * 0.2
    cashflow_score_component = cashflow_component_val * 0.1

    raw_score = (
        savings_ratio_score
        + expense_ratio_score
        + risk_score_component
        + cashflow_score_component
    )

    clamped_score = max(0.0, min(100.0, raw_score))

    return {
        "health_score": round(clamped_score, 2),
        "components": {
            "raw": {
                "savings_ratio": round(savings_ratio, 2),
                "expense_ratio": round(expense_ratio, 2),
                "risk_level": risk_level,
                "cashflow_status": cashflow_status
            },
            "weighted": {
                "savings_ratio_score": round(savings_ratio_score, 2),
                "expense_ratio_score": round(expense_ratio_score, 2),
                "risk_component": round(risk_score_component, 2),
                "cashflow_component": round(cashflow_score_component, 2)
            }
        }
    }

def get_financial_grade(score):
    """
    Maps health score to grade letter, description descriptor, and color.
    """
    if score >= 90.0:
        grade = "A"
        desc = "Excellent"
        color = "green"
    elif score >= 80.0:
        grade = "B"
        desc = "Good"
        color = "blue"
    elif score >= 70.0:
        grade = "C"
        desc = "Average"
        color = "yellow"
    elif score >= 50.0:
        grade = "D"
        desc = "Poor"
        color = "orange"
    else:
        grade = "F"
        desc = "Critical"
        color = "red"

    return {
        "score": round(score, 2),
        "grade": grade,
        "description": desc,
        "color": color
    }
