from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression

def build_monthly_series(transactions):
    """
    Groups transactions chronologically by month ("YYYY-MM").
    Returns a sorted list of dicts: [{"month": "YYYY-MM", "income": X, "expenses": Y}]
    """
    monthly_data = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
    for t in transactions:
        if not t.date:
            continue
        m_str = t.date.strftime("%Y-%m")
        if t.type == "Income" or t.amount > 0:
            monthly_data[m_str]["income"] += t.amount
        elif t.type == "Expense" or t.amount < 0:
            monthly_data[m_str]["expenses"] += abs(t.amount)

    sorted_months = sorted(monthly_data.keys())
    result = []
    for m in sorted_months:
        result.append({
            "month": m,
            "income": round(monthly_data[m]["income"], 2),
            "expenses": round(monthly_data[m]["expenses"], 2)
        })
    return result

def forecast_income_ma(transactions):
    """
    Primary income forecast using moving average of last 3 months.
    """
    series = build_monthly_series(transactions)
    if not series:
        return {
            "predicted_income": 0.0,
            "method": "moving_average",
            "months_used": 0
        }
    incomes = [item["income"] for item in series]
    last_3 = incomes[-3:]
    pred = sum(last_3) / len(last_3)
    return {
        "predicted_income": round(pred, 2),
        "method": "moving_average",
        "months_used": len(last_3)
    }

def forecast_expenses_ma(transactions):
    """
    Primary expenses forecast using moving average of last 3 months.
    """
    series = build_monthly_series(transactions)
    if not series:
        return {
            "predicted_expenses": 0.0,
            "method": "moving_average",
            "months_used": 0
        }
    expenses = [item["expenses"] for item in series]
    last_3 = expenses[-3:]
    pred = sum(last_3) / len(last_3)
    return {
        "predicted_expenses": round(pred, 2),
        "method": "moving_average",
        "months_used": len(last_3)
    }

def predict_income_trend(transactions):
    """
    Uses linear regression on monthly income series to classify trend.
    epsilon = 0.05
    """
    series = build_monthly_series(transactions)
    if len(series) < 2:
        return {
            "slope": 0.0,
            "trend": "stable"
        }
    incomes = [item["income"] for item in series]
    X = np.arange(len(incomes)).reshape(-1, 1)
    y = np.array(incomes)

    model = LinearRegression()
    model.fit(X, y)

    slope = float(model.coef_[0])
    epsilon = 0.05
    if abs(slope) <= epsilon:
        trend = "stable"
    elif slope > epsilon:
        trend = "increasing"
    else:
        trend = "decreasing"

    return {
        "slope": round(slope, 2),
        "trend": trend
    }

def predict_expense_trend(transactions):
    """
    Uses linear regression on monthly expense series to classify trend.
    epsilon = 0.05
    """
    series = build_monthly_series(transactions)
    if len(series) < 2:
        return {
            "slope": 0.0,
            "trend": "stable"
        }
    expenses = [item["expenses"] for item in series]
    X = np.arange(len(expenses)).reshape(-1, 1)
    y = np.array(expenses)

    model = LinearRegression()
    model.fit(X, y)

    slope = float(model.coef_[0])
    epsilon = 0.05
    if abs(slope) <= epsilon:
        trend = "stable"
    elif slope > epsilon:
        trend = "increasing"
    else:
        trend = "decreasing"

    return {
        "slope": round(slope, 2),
        "trend": trend
    }

def calculate_cash_runway(transactions):
    """
    Calculates cash runway details.
    """
    current_balance = sum(t.amount for t in transactions)
    series = build_monthly_series(transactions)

    if not series:
        return {
            "current_balance": round(current_balance, 2),
            "average_monthly_expenses": 0.0,
            "average_monthly_income": 0.0,
            "net_burn": 0.0,
            "months_remaining": None,
            "status": "cashflow_positive"
        }

    avg_income = sum(item["income"] for item in series) / len(series)
    avg_expenses = sum(item["expenses"] for item in series) / len(series)

    net_burn = avg_expenses - avg_income

    if net_burn <= 0:
        months_remaining = None
        status = "cashflow_positive"
    else:
        if current_balance <= 0:
            months_remaining = 0.0
        else:
            months_remaining = round(current_balance / net_burn, 2)
        status = "burn_rate_active"

    return {
        "current_balance": round(current_balance, 2),
        "average_monthly_expenses": round(avg_expenses, 2),
        "average_monthly_income": round(avg_income, 2),
        "net_burn": round(max(0.0, net_burn), 2),
        "months_remaining": months_remaining,
        "status": status
    }

def forecast_summary(transactions):
    """
    Generates a combined forecast summary with confidence level based on history length.
    """
    series = build_monthly_series(transactions)
    num_months = len(series)

    if num_months >= 12:
        confidence = "high"
    elif num_months >= 6:
        confidence = "medium"
    else:
        confidence = "low"

    inc_ma = forecast_income_ma(transactions)
    exp_ma = forecast_expenses_ma(transactions)
    inc_trend = predict_income_trend(transactions)
    exp_trend = predict_expense_trend(transactions)
    runway = calculate_cash_runway(transactions)

    return {
        "predicted_income": inc_ma["predicted_income"],
        "predicted_expenses": exp_ma["predicted_expenses"],
        "income_trend": inc_trend["trend"],
        "expenses_trend": exp_trend["trend"],
        "months_remaining": runway["months_remaining"],
        "runway_status": runway["status"],
        "confidence": confidence
    }
