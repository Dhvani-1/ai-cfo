from analytics.ratios import calculate_expense_ratio, calculate_savings_ratio
from analytics.risk_analysis import analyze_risk
from analytics.forecast import calculate_cash_runway

def generate_recommendations(transactions):
    """
    Evaluates ratios, risk, and runway, producing structured severity-based recommendations.
    Includes categories and priorities, sorted by priority ascending.
    """
    expense_ratio = calculate_expense_ratio(transactions)
    savings_ratio = calculate_savings_ratio(transactions)

    runway_info = calculate_cash_runway(transactions)
    runway_months = runway_info["months_remaining"]
    runway_status = runway_info["status"]

    risk_info = analyze_risk(transactions)
    risk_level = risk_info["risk_level"]

    recommendations = []

    # Expense Ratio Recommendations
    if expense_ratio > 70.0:
        recommendations.append({
            "severity": "critical",
            "priority": 1,
            "category": "expenses",
            "message": "Expenses are very high relative to income. Cut overhead and discretionary spending immediately."
        })
    elif expense_ratio > 50.0:
        recommendations.append({
            "severity": "warning",
            "priority": 2,
            "category": "expenses",
            "message": "Discretionary spending is elevated. Review non-essential costs."
        })
    else:
        recommendations.append({
            "severity": "info",
            "priority": 3,
            "category": "expenses",
            "message": "Spending is well within budget. Keep maintaining this level."
        })

    # Savings Ratio Recommendations
    if savings_ratio < 10.0:
        recommendations.append({
            "severity": "critical",
            "priority": 1,
            "category": "savings",
            "message": "Savings rate is critically low. Prioritize building an emergency fund."
        })
    elif savings_ratio < 20.0:
        recommendations.append({
            "severity": "warning",
            "priority": 2,
            "category": "savings",
            "message": "Savings rate is below target. Aim to save at least 20% of income."
        })
    else:
        recommendations.append({
            "severity": "info",
            "priority": 3,
            "category": "savings",
            "message": "Savings rate is strong. Consider investing surplus cash to generate passive returns."
        })

    # Cash Runway Recommendations
    if runway_status == "burn_rate_active":
        if runway_months is not None:
            if runway_months < 3.0:
                recommendations.append({
                    "severity": "critical",
                    "priority": 1,
                    "category": "cashflow",
                    "message": f"Cash runway is critically short ({runway_months} months). Urgently reduce net burn rate."
                })
            elif runway_months < 6.0:
                recommendations.append({
                    "severity": "warning",
                    "priority": 2,
                    "category": "cashflow",
                    "message": f"Cash runway is low ({runway_months} months). Defer major expansions or purchases."
                })
    else:
        recommendations.append({
            "severity": "info",
            "priority": 3,
            "category": "cashflow",
            "message": "Cash flow is positive. Cash runway is stable."
        })

    # Risk Recommendations
    if risk_level == "high":
        recommendations.append({
            "severity": "critical",
            "priority": 1,
            "category": "risk",
            "message": "Overall risk level is High. Formulate an immediate contingency plan."
        })
    elif risk_level == "medium":
        recommendations.append({
            "severity": "warning",
            "priority": 2,
            "category": "risk",
            "message": "Overall risk level is Medium. Monitor expense categories closely."
        })

    # Fallback to default if list is empty
    if len(recommendations) == 0:
        recommendations.append({
            "severity": "info",
            "priority": 3,
            "category": "cashflow",
            "message": "Maintain your current financial habits."
        })

    # Sort recommendations by priority ascending
    recommendations_sorted = sorted(recommendations, key=lambda x: x["priority"])

    return recommendations_sorted
